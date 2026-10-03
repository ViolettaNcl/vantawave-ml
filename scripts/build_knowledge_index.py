from __future__ import annotations

import argparse
from pathlib import Path

from vantawave.ai.rag.index import KnowledgeIndex


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "paths",
        nargs="*",
        default=["docs"],
        help="Files/directories containing .md/.txt/.rst knowledge documents.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/ai/knowledge_manifest.json"),
    )
    args = parser.parse_args()

    index = KnowledgeIndex.from_paths(args.paths)
    output = index.save_manifest(args.out)

    print("VantaWave knowledge index built")
    print(f"documents: {len(index.documents)}")
    print(f"chunks: {len(index.chunks)}")
    print(f"manifest: {output}")


if __name__ == "__main__":
    main()
