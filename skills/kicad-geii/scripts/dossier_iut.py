"""Dossier de fabrication au format de l'IUT GEII Lyon 1 (module CAO / SAE), en une commande.

Usage : python dossier_iut.py <dossier-du-projet ou .kicad_pro> [--nom "G20x NOM Prenom"] [--sortie DOSSIER]

Produit dans <projet>/Dossier de fabrication/<horodatage>/ (ou --sortie) :
  - schema.pdf, F_Fab.pdf (couche de fabrication + contour), F_Cu.pdf (straps), vue_3d.png, bom.csv ;
  - Gerber/ : B.Cu, Edge.Cuts (+ F.Cu s'il y a des straps) et perçage, plus Gerber.zip ;
  - apercu_gerber.png (contrôle de ce qui part à la gravure) ;
  - DOSSIER DE FABRICATION.pdf : page de garde, sommaire, schéma, couche de fabrication et vue 3D,
    straps, BOM — l'ordre de l'exemple du prof.
Ne modifie pas les fichiers du projet.
"""
import argparse, csv, datetime, json, sys, zipfile
from pathlib import Path
from kicad_common import champ, controles, enfants, lancer, lire, projet
from gerber_vue import generer


def assembler(out, nom, titre_projet, straps):
    import pymupdf
    doc = pymupdf.open()
    A4 = pymupdf.paper_rect("a4")

    def page_titre(texte, sous=None):
        p = doc.new_page(width=A4.width, height=A4.height)
        taille = min(26, 475 / max(1, pymupdf.get_text_length(texte, fontsize=1)))
        p.insert_text((60, 120), texte, fontsize=taille, fontname="helv")
        if sous:
            p.insert_textbox(pymupdf.Rect(60, 150, A4.width - 60, A4.height - 60), sous, fontsize=12, fontname="helv")
        return p

    def cadre(page_pdf):
        r = pymupdf.Rect()
        for dessin in page_pdf.get_drawings():
            r |= dessin["rect"]
        return (r + (-5, -5, 5, 5)) if not r.is_empty else page_pdf.rect

    page_titre("DOSSIER DE FABRICATION", f"{titre_projet}\n\n{nom}")
    sommaire = ["1. Schéma", "2. Couche de fabrication et vue 3D", "3. Straps (F.Cu)", "4. BOM (Bill Of Material)"]
    page_titre("TABLE DES MATIÈRES", "\n".join(sommaire))

    page_titre("1. SCHÉMA")
    doc.insert_pdf(pymupdf.open(out / "schema.pdf"))

    p = page_titre("2. COUCHE DE FABRICATION ET VUE 3D")
    fab = pymupdf.open(out / "F_Fab.pdf")
    p.show_pdf_page(pymupdf.Rect(40, 160, A4.width - 40, 470), fab, 0, clip=cadre(fab[0]))
    if (out / "vue_3d.png").exists():
        p.insert_image(pymupdf.Rect(40, 490, A4.width - 40, A4.height - 40), filename=str(out / "vue_3d.png"))

    p = page_titre("3. STRAPS (F.CU)", None if straps else "Carte en simple face : aucun strap.")
    if straps:
        fcu = pymupdf.open(out / "F_Cu.pdf")
        p.show_pdf_page(pymupdf.Rect(40, 160, A4.width - 40, A4.height - 40), fcu, 0, clip=cadre(fcu[0]))

    p = page_titre("4. BOM (BILL OF MATERIAL)")
    with open(out / "bom.csv", encoding="utf-8-sig", newline="") as source:
        lignes = list(csv.reader(source))
    y = 170
    for i, l in enumerate(lignes):
        cellules = [(l[0], 60, 235), (l[1] if len(l) > 1 else "", 250, A4.width - 60)]
        hauteur = max(25, max(len(texte) // max(1, int((x2-x1)/6)) + 1 for texte, x1, x2 in cellules) * 15 + 8)
        if y + hauteur > A4.height - 50:
            p, y = page_titre("4. BOM (SUITE)"), 170
        for texte, x1, x2 in cellules:
            if p.insert_textbox(pymupdf.Rect(x1, y, x2, y+hauteur), texte, fontsize=10,
                                fontname="hebo" if i == 0 else "helv") < 0:
                raise ValueError("Cellule BOM trop longue : élargir sa mise en page avant livraison.")
        y += hauteur
    doc.save(out / "DOSSIER DE FABRICATION.pdf")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("projet", type=Path)
    a.add_argument("--nom", default="GROUPE NOM")
    a.add_argument("--sortie", type=Path)
    o = a.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    import pymupdf, gerbonara, resvg_py
    pro = projet(o.projet)
    sch, pcb = pro.with_suffix(".kicad_sch"), pro.with_suffix(".kicad_pcb")
    out = o.sortie or pro.parent / "Dossier de fabrication" / datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = out.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError("La sortie doit être vide. Choisir un nouveau dossier pour préserver les exports précédents.")
    out.mkdir(parents=True, exist_ok=True)
    rapports = controles(pro, out)
    (out / "controle.json").write_text(json.dumps(rapports, ensure_ascii=False, indent=2), encoding="utf-8")
    for nom, rapport in rapports.items():
        print(f'{nom} : {rapport["erreurs"]} erreur(s), {rapport["avertissements"]} avertissement(s), '
              f'{rapport["exclusions"]} exclusion(s)')
    if any(r["erreurs"] for r in rapports.values()):
        raise ValueError("Export interrompu : corriger les erreurs ERC/DRC. Rapports conservés dans la sortie.")
    ger = out / "Gerber"
    ger.mkdir(parents=True)

    carte = lire(pcb)
    straps = any(champ(item, "layer") == "F.Cu" for key in ("segment", "arc", "zone") for item in enfants(carte, key))
    if any(champ(item, "layer") not in ("B.Cu", "F.Cu")
           for key in ("segment", "arc") for item in enfants(carte, key)):
        raise ValueError("Cuivre interne détecté : utiliser un export industriel adapté au lieu du profil IUT.")

    lancer("sch", "export", "pdf", "-o", out / "schema.pdf", sch)
    lancer("pcb", "export", "pdf", "--layers", "F.Fab,Edge.Cuts", "--mode-single", "--black-and-white", "--check-zones",
           "--exclude-value", "-o", out / "F_Fab.pdf", pcb)
    lancer("pcb", "export", "pdf", "--layers", "F.Cu,Edge.Cuts", "--mode-single", "--black-and-white", "--check-zones",
           "-o", out / "F_Cu.pdf", pcb)
    lancer("pcb", "render", "--quality", "high", "--floor", "-w", "1600", "-h", "1000", "-o", out / "vue_3d.png", pcb)
    lancer("sch", "export", "bom", "--fields", "Reference,Value", "--labels", "Reference,Value",
           "--ref-range-delimiter", "", "-o", out / "bom.csv", sch)
    bom = out / "bom.csv"
    bom.write_text(bom.read_text(encoding="utf-8"), encoding="utf-8-sig")

    couches = "B.Cu,Edge.Cuts" + (",F.Cu" if straps else "")
    lancer("pcb", "export", "gerbers", "--layers", couches, "--check-zones", "-o", str(ger) + "/", pcb)
    lancer("pcb", "export", "drill", "--format", "excellon", "-o", str(ger) + "/", pcb)
    with zipfile.ZipFile(out / "Gerber.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for g in ger.iterdir():
            z.write(g, g.name)
    generer(ger, out / "apercu_gerber.png")
    cartouche = enfants(lire(sch), "title_block")
    titre = champ(cartouche[0], "title", pro.stem) if cartouche else pro.stem
    assembler(out, o.nom, titre, straps)
    print("Dossier PDF : DOSSIER DE FABRICATION.pdf")
    print("Fichiers : " + ", ".join(sorted(p.name for p in out.iterdir())))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, ImportError) as error:
        print(f"ÉCHEC : {error}", file=sys.stderr)
        sys.exit(2)
