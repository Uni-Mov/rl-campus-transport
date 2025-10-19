import json
import yaml
from pathlib import Path

def load_config(path: str | Path) -> dict:
    """Carga configuración desde un archivo YAML o JSON."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de configuración: {path}")

    if path.suffix in [".yaml", ".yml"]:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    elif path.suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise ValueError("Formato no soportado (usa .yaml o .json)")
