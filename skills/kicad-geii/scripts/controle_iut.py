"""Contrôle IUT en lecture seule. Exécuter avec le Python fourni par KiCad."""
import argparse
import fnmatch
import json
import math
import re
import sys
import tempfile
from pathlib import Path

import pcbnew
from kicad_common import controles, projet

mm = pcbnew.ToMM


def angle(u, v):
    lu, lv = math.hypot(*u), math.hypot(*v)
    if not lu or not lv:
        return None
    return math.degrees(math.acos(max(-1, min(1, (u[0] * v[0] + u[1] * v[1]) / (lu * lv)))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("projet", type=Path)
    parser.add_argument("--sortie", type=Path)
    parser.add_argument("--profil", type=Path, help="Objectifs de largeur propres au projet, JSON.")
    options = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    pro = projet(options.projet)
    out = options.sortie or Path(tempfile.mkdtemp(prefix="kicad-geii-"))
    out.mkdir(parents=True, exist_ok=True)
    if any((out / name).exists() for name in ("erc.json", "drc.json", "controle.json")):
        raise ValueError("Les rapports existent déjà. Choisir un nouveau dossier de sortie.")
    profil = json.loads(options.profil.read_text(encoding="utf-8")) if options.profil else {}
    net_settings = json.loads(pro.read_text(encoding="utf-8")) .get("net_settings", {})
    patterns = net_settings.get("netclass_patterns", [])
    classes = {c["name"]: c for c in net_settings.get("classes", [])}
    resultats = []

    def note(niveau, texte):
        resultats.append({"niveau": niveau, "texte": texte})
        print(f"[{niveau}] {texte}")

    def classe(net):
        matches = [p["netclass"] for p in patterns if fnmatch.fnmatchcase(net, p["pattern"])]
        assigned = (net_settings.get("netclass_assignments") or {}).get(net)
        if assigned:
            matches.extend([assigned] if isinstance(assigned, str) else assigned)
        return set(matches or ["Default"])

    rapports = controles(pro, out)
    for nom, r in rapports.items():
        niveau = "ERREUR" if r["erreurs"] else "À VOIR" if r["avertissements"] or r["exclusions"] else "OK"
        note(niveau, f'{nom} : {r["erreurs"]} erreur(s), {r["avertissements"]} avertissement(s), '
             f'{r["exclusions"]} exclusion(s).')
    b = pcbnew.LoadBoard(str(pro.with_suffix(".kicad_pcb")))
    footprints = list(b.GetFootprints())
    pads = [p for f in footprints for p in f.Pads()]
    tracks = list(b.GetTracks())
    pistes = [t for t in tracks if t.GetClass() == "PCB_TRACK"]
    vias = [t for t in tracks if t.GetClass() == "PCB_VIA"]
    arcs = [t for t in tracks if t.GetClass() == "PCB_ARC"]
    if arcs:
        note("À VOIR", f"{len(arcs)} arc(s) cuivre : contrôlés par DRC ; angles aux jonctions à examiner visuellement.")
    trous = [(p.GetParentFootprint().GetReference(), min(mm(p.GetDrillSize().x), mm(p.GetDrillSize().y)))
             for p in pads if p.GetDrillSize().x > 0]
    trous += [("via", mm(v.GetDrill())) for v in vias]
    petits = sorted({(ref, round(d, 3)) for ref, d in trous if d < 0.8 - 1e-6})
    note("ERREUR" if petits else "OK", "Perçages ≥ 0,8 mm" + (f" : {petits}" if petits else "."))
    anneaux = []
    for p in pads:
        if p.GetAttribute() != pcbnew.PAD_ATTRIB_PTH:
            continue
        size, drill = p.GetSize(pcbnew.B_Cu), p.GetDrillSize()
        ring = min(mm(size.x - drill.x), mm(size.y - drill.y)) / 2
        if ring < 0.4 - 1e-6:
            anneaux.append(p.GetParentFootprint().GetReference())
    note("À VOIR" if anneaux else "OK", "Anneau estimé ≥ 0,4 mm" +
         (f" : vérifier {', '.join(sorted(set(anneaux)))}." if anneaux else "."))
    fines = []
    secteur = set()
    for t in pistes + arcs:
        net = t.GetNetname()
        netclasses = classe(net)
        if "Secteur" in netclasses:
            secteur.add(net)
        target = max(float(classes.get(c, {}).get("track_width", 0.6)) for c in netclasses)
        key = "largeur_secteur_mm" if "Secteur" in netclasses else "largeur_tbt_mm"
        target = float(profil.get(key, target))
        if target <= 0:
            raise ValueError("Une largeur demandée doit être positive.")
        if mm(t.GetWidth()) < target - 1e-6:
            point = t.GetStart()
            fines.append({"net": net, "largeur_mm": round(mm(t.GetWidth()), 3), "minimum_mm": target,
                          "x_mm": mm(point.x), "y_mm": mm(point.y), "uuid": str(t.m_Uuid.AsString())})
    note("ERREUR" if fines else "OK", f"Largeurs : {len(fines)} segment(s) sous les objectifs "
         + ("du profil." if profil else "des classes du projet."))
    for item in fines[:12]:
        note("ERREUR", f'{item["net"]} : {item["largeur_mm"]} mm < {item["minimum_mm"]} mm '
             f'en ({item["x_mm"]:.2f} ; {item["y_mm"]:.2f}).')

    straps = [t for t in pistes if t.GetLayer() == pcbnew.F_Cu]
    pb = []
    courtyard_absent = set()
    for t in straps:
        start, end = t.GetStart(), t.GetEnd()
        if start.x != end.x and start.y != end.y:
            pb.append("strap en diagonale")
        for point in (start, end):
            if not any(v.GetNetCode() == t.GetNetCode()
                       and (v.GetPosition() - point).EuclideanNorm() < pcbnew.FromMM(0.05) for v in vias):
                pb.append(f"bout sans via du même net ({mm(point.x):.2f};{mm(point.y):.2f})")
        for f in footprints:
            courtyard = f.GetCourtyard(pcbnew.F_CrtYd)
            if not courtyard.OutlineCount():
                courtyard_absent.add(f.GetReference())
            elif courtyard.Collide(pcbnew.SEG(start, end)):
                pb.append(f"strap sous {f.GetReference()}")
    for v in vias:
        count = sum(any((p - v.GetPosition()).EuclideanNorm() < pcbnew.FromMM(0.05)
                        for p in (t.GetStart(), t.GetEnd())) for t in straps)
        if count > 1:
            pb.append(f"via utilisé par {count} segments F.Cu")
        for f in footprints:
            courtyard = f.GetCourtyard(pcbnew.F_CrtYd)
            if courtyard.OutlineCount() and courtyard.Collide(v.GetPosition()):
                pb.append(f"via sous {f.GetReference()}")
    note("ERREUR" if pb else "OK", f"Straps F.Cu : {len(straps)} segment(s)" +
         (" : " + "; ".join(sorted(set(pb))) if pb else "."))
    if courtyard_absent:
        note("À VOIR", "Emprise des composants sans courtyard à vérifier : " + ", ".join(sorted(courtyard_absent)))

    bouts = {}
    for t in pistes:
        for a, z in ((t.GetStart(), t.GetEnd()), (t.GetEnd(), t.GetStart())):
            bouts.setdefault((t.GetNetname(), t.GetLayer(), a.x, a.y), []).append((z.x-a.x, z.y-a.y))
    angles = []
    for (net, layer, x, y), directions in bouts.items():
        point = pcbnew.VECTOR2I(x, y)
        if len(directions) < 2 or any(p.HitTest(point) for p in pads):
            continue
        if any((v.GetPosition()-point).EuclideanNorm() < pcbnew.FromMM(0.1) for v in vias):
            continue
        for i, u in enumerate(directions):
            for v in directions[i+1:]:
                value = angle(u, v)
                if value is not None and (value < 88 or (abs(value-90) < 2 and len(directions) == 2)):
                    angles.append(f"{net} : {value:.1f}° en ({mm(x):.2f};{mm(y):.2f})")
    note("À VOIR" if angles else "OK", "Jonctions de segments : " +
         ("; ".join(angles[:12]) if angles else "aucun coude droit ou angle aigu détecté."))
    note("À VOIR", "Les raccords en milieu de segment et les contours de zones nécessitent une revue visuelle.")

    elements = list(b.GetDrawings())
    for f in footprints:
        elements.extend(f.GraphicalItems())
        elements.extend((f.Reference(), f.Value()))
    textes = [d for d in elements if d.GetClass() in ("PCB_TEXT", "FP_TEXT")
              and d.GetLayer() == pcbnew.B_Cu and d.IsVisible()]
    mauvais = [d.GetText() for d in textes if not d.IsMirrored()]
    note("ERREUR" if mauvais else "OK", f"Textes B.Cu : {len(textes)} visibles" +
         (" ; non miroirs : " + ", ".join(mauvais) if mauvais else ", tous en miroir."))
    petits_textes = [d.GetText() for d in textes if mm(d.GetTextHeight()) < 1
                     or 0 < mm(d.GetTextThickness()) < 0.2]
    if petits_textes:
        note("À VOIR", "Textes sous la recommandation locale 1 mm / 0,2 mm : " + ", ".join(petits_textes))
    note("À VOIR", "Vérifier titre, groupe et repères utiles selon l'énoncé ; limiter les textes gravés.")
    bord = [d for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]
    bb = b.GetBoardEdgesBoundingBox()
    note("OK" if bord else "ERREUR", f"Edge.Cuts : {len(bord)} élément(s), "
         f"{mm(bb.GetWidth()):.2f} × {mm(bb.GetHeight()):.2f} mm ; fermeture vérifiée par DRC.")
    plans = [z for z in b.Zones() if not z.IsTeardropArea() and not z.GetIsRuleArea() and z.GetNetname() == "GND"]
    note("À VOIR", f"Zones GND : {len(plans)} ; vérifier remplissage et séparation des domaines avant ajout d'un plan.")
    if secteur:
        note("À VOIR", "Classe Secteur : " + ", ".join(sorted(secteur)) +
             ". Le nom des réseaux ne prouve pas leur domaine électrique.")
        note("À VOIR", "Isolement : vérifier les conditions et priorités du .kicad_dru et tester son déclenchement "
             "sur une copie. Ce script ne mesure pas la ligne de fuite et ne certifie pas la sécurité secteur.")
    payload = {"kicad": pcbnew.GetBuildVersion(), "rapports": rapports, "resultats": resultats,
               "largeurs_non_conformes": fines,
               "limites": "Revue électrique, tensions admissibles, thermique et isolement de sécurité non automatisés."}
    (out / "controle.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Rapports : {out}")
    return 1 if any(r["niveau"] == "ERREUR" for r in resultats) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError) as error:
        print(f"ÉCHEC : {error}", file=sys.stderr)
        sys.exit(2)
