#!/usr/bin/env python3
"""
Genera y guarda *_distances.pkl en ia_ml/src/data para una localidad o un graphml local.
"""
import os
import sys
from pathlib import Path
import argparse

IA_ML_DIR = str(Path(__file__).parent.parent.resolve()) 
if IA_ML_DIR not in sys.path:
    sys.path.insert(0, IA_ML_DIR)

from src.data.download_graph import (
    download_and_save_graph,
    load_graph_from_graphml,
    precompute_and_save_distances,
)

def safe_name_from_locality(locality: str) -> str:
    return locality.replace(",", "").replace(" ", "_")

def main():
    parser = argparse.ArgumentParser(description="Precompute all-pairs distances and save as *_distances.pkl")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--locality", "-l", type=str, help="Locality name to download via OSMnx (e.g. 'Río Cuarto, Córdoba, Argentina')")
    group.add_argument("--graph-file", "-g", type=str, help="Path to existing .graphml file")
    parser.add_argument("--weight", "-w", default="length", help="Edge attribute to use as weight (default: length)")
    args = parser.parse_args()

    SCRIPTDIR = Path(__file__).parent.resolve()
    DATA_DIR = (SCRIPTDIR / ".." / "src" / "data").resolve()
    os.makedirs(DATA_DIR, exist_ok=True)

    if args.graph_file:
        graph_path = Path(args.graph_file)
        if not graph_path.exists():
            print(f"[ERROR] graph-file not found: {graph_path}")
            sys.exit(1)
        G = load_graph_from_graphml(str(graph_path))
        safe_name = graph_path.stem
    else:
        locality = args.locality
        safe_name = safe_name_from_locality(locality)
        graph_filename = f"{safe_name}.graphml"
        graph_path = DATA_DIR / graph_filename
        if not graph_path.exists():
            print(f"[INFO] Graph not found locally. Downloading '{locality}' to '{graph_path}' ...")
            G = download_and_save_graph(locality, str(graph_path))
        else:
            print(f"[INFO] Loading existing graph from '{graph_path}' ...")
            G = load_graph_from_graphml(str(graph_path))

    out_path = DATA_DIR / f"{safe_name}_distances.pkl"
    if out_path.exists():
        print(f"[WARN] Output file already exists: {out_path}")
        resp = input("Overwrite? [y/N]: ").strip().lower()
        if resp != "y":
            print("Aborting.")
            return

    print(f"[INFO] Computing all-pairs shortest path lengths (weight='{args.weight}').")
    precompute_and_save_distances(G, str(out_path), weight=args.weight)
    print("[OK] Distances saved to:", out_path)

if __name__ == "__main__":
    main()