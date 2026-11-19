"""Aperçu Gerber/Excellon par Gerbonara, avec arcs, macros et polarités."""
import argparse
import json
import re
import sys
from pathlib import Path


def generer(dossier, sortie):
    from gerbonara import LayerStack
    from gerbonara.graphic_objects import Flash, Region
    import resvg_py

    fichiers = [p for p in Path(dossier).iterdir() if p.is_file()]
    mapping = {}
    for fichier in fichiers:
        name = fichier.name.lower()
        if name.endswith((".gbrjob", ".zip")):
            continue
        if name.endswith(".drl"):
            couche = "drill unknown"
        elif "edge_cuts" in name or name.endswith(".gko"):
            couche = "mechanical outline"
        elif "b_cu" in name or name.endswith(".gbl"):
            couche = "bottom copper"
        elif "f_cu" in name or name.endswith(".gtl"):
            couche = "top copper"
        else:
            raise ValueError(f"Couche non reconnue dans cet export IUT : {fichier.name}")
        mapping[re.escape(fichier.name)] = couche
    stack = LayerStack.from_files(fichiers, autoguess=False, overrides=mapping)
    if ("mechanical", "outline") not in stack.graphic_layers:
        raise ValueError("Contour Gerber non identifié. Contrôler les noms et les attributs X2.")
    colors = {"bottom copper": "#285adc", "top copper": "#dc3c3c",
              "mechanical outline": "#111111", "drill pth": "white",
              "drill npth": "white", "drill unknown": "white"}
    svg = str(stack.to_svg(margin=3, colors=colors))
    sortie = Path(sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.with_suffix(".svg").write_text(svg, encoding="utf-8")
    sortie.write_bytes(resvg_py.svg_to_bytes(svg_string=svg, width=1800, dpi=96,
                                            background="white", skip_system_fonts=True))
    stats = {}
    for (side, usage), layer in stack.graphic_layers.items():
        stats[f"{side} {usage}"] = {
            "flashes": sum(isinstance(o, Flash) for o in layer.objects),
            "regions": sum(isinstance(o, Region) for o in layer.objects),
            "objets": len(layer.objects),
        }
    stats["percages"] = sum(len(layer.objects) for layer in stack.drill_layers)
    stats["vue"] = "Vue par transparence depuis le dessus ; aucun miroir horizontal ajouté."
    sortie.with_suffix(".json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    return stats


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gerber", type=Path)
    parser.add_argument("sortie", type=Path)
    options = parser.parse_args()
    print(json.dumps(generer(options.gerber, options.sortie), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
