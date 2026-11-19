"""Accès KiCad et lecture de fichiers sans modifier les sources."""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path


def cli():
    configured = os.environ.get("KICAD_CLI")
    if configured:
        return configured
    found = shutil.which("kicad-cli")
    if found:
        return found
    roots = [Path.home() / "AppData/Local/Programs/KiCad", Path("C:/Program Files/KiCad")]
    for version in ("10.0", "9.0"):
        for root in roots:
            candidate = root / version / "bin/kicad-cli.exe"
            if candidate.is_file():
                return str(candidate)
    raise RuntimeError("kicad-cli introuvable. Définir KICAD_CLI ou installer KiCad.")


def lancer(*args, codes=(0,)):
    result = subprocess.run([cli(), *map(str, args)], capture_output=True,
                            text=True, encoding="utf-8", errors="replace")
    if result.returncode not in codes:
        raise RuntimeError(f"KiCad {args[:3]} : code {result.returncode}\n"
                           + (result.stderr or result.stdout)[-1500:])
    return result


def projet(cible):
    cible = Path(cible).resolve()
    if cible.is_dir():
        candidats = list(cible.glob("*.kicad_pro"))
        if len(candidats) != 1:
            raise ValueError(f"{len(candidats)} projets dans {cible}. Indiquer le .kicad_pro exact.")
        cible = candidats[0]
    if cible.suffix != ".kicad_pro" or not cible.is_file():
        raise ValueError("Indiquer un .kicad_pro existant ou son dossier.")
    for suffix in (".kicad_sch", ".kicad_pcb"):
        if not cible.with_suffix(suffix).is_file():
            raise ValueError(f"Fichier absent : {cible.with_suffix(suffix)}")
    return cible


def sexp(texte):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', texte)
    stack, roots = [], []
    for token in tokens:
        if token == "(":
            node = []
            (stack[-1] if stack else roots).append(node)
            stack.append(node)
        elif token == ")":
            if not stack:
                raise ValueError("Parenthèse fermante inattendue.")
            stack.pop()
        else:
            value = re.sub(r'\\(["\\])', r'\1', token[1:-1]) if token.startswith('"') else token
            (stack[-1] if stack else roots).append(value)
    if stack:
        raise ValueError("Expression KiCad incomplète.")
    return roots[0] if len(roots) == 1 else roots


def enfants(node, nom):
    return [n for n in node if isinstance(n, list) and n and n[0] == nom]


def champ(node, nom, default=None):
    values = enfants(node, nom)
    return values[0][1] if values and len(values[0]) > 1 else default


def lire(cible):
    return sexp(Path(cible).read_text(encoding="utf-8-sig"))


def violations(rapport):
    data = json.loads(Path(rapport).read_text(encoding="utf-8-sig"))
    values = []
    for key in ("violations", "unconnected_items", "schematic_parity"):
        values.extend(data.get(key, []))
    for sheet in data.get("sheets", []):
        values.extend(sheet.get("violations", []))
    return values


def controles(pro, sortie):
    sortie = Path(sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    rapports = {}
    for nom, arguments, source in (
        ("ERC", ("sch", "erc"), pro.with_suffix(".kicad_sch")),
        ("DRC", ("pcb", "drc", "--schematic-parity", "--refill-zones"), pro.with_suffix(".kicad_pcb")),
    ):
        dest = sortie / f"{nom.lower()}.json"
        lancer(*arguments, "--format", "json", "--severity-all", "--exit-code-violations",
               "-o", dest, source, codes=(0, 5))
        values = violations(dest)
        rapports[nom] = {
            "erreurs": sum(v.get("severity") == "error" for v in values),
            "avertissements": sum(v.get("severity") == "warning" for v in values),
            "exclusions": sum(v.get("severity") == "exclusion" for v in values),
            "violations": values,
        }
    return rapports
