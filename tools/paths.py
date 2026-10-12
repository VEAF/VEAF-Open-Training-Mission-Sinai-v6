"""Où sont le dossier de mission et le code Python de VMCT, pour tous les scripts de tools/.

Par défaut le dépôt voisin `../VEAF-Mission-Creation-Tools` ; la variable d'environnement VMCT_PY
désigne un autre dossier `src/python/veaf-tools` (un worktree, un export de develop).
"""
import os
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
VMCT_PY = Path(os.environ.get("VMCT_PY", ROOT.parent / "VEAF-Mission-Creation-Tools" / "src" / "python" / "veaf-tools"))

VMCT = VMCT_PY.parent.parent.parent   # racine du checkout (scripts Lua, données)

if not VMCT_PY.is_dir():
    raise SystemExit(f"[tools] code VMCT introuvable : {VMCT_PY}\n"
                     f"        indiquez-le avec la variable d'environnement VMCT_PY")
if str(VMCT_PY) not in sys.path:
    sys.path.insert(0, str(VMCT_PY))
