SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# moverse al directorio raíz del proyecto si no estamos ya
if [ -d "ia_ml/src" ]; then
  cd ia_ml
fi
python -m src.training.main