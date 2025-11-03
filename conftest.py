import os
import sys

# Añade la carpeta `src` al sys.path para que pytest pueda importar los paquetes
# ubicados en `src/` (ej.: import src.etl...)
ROOT = os.path.abspath(os.path.dirname(__file__))
SRC = os.path.join(ROOT, "src")

if SRC not in sys.path:
    sys.path.insert(0, SRC)

# También añadir el root por si hay imports relativos desde la raíz del repo
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
