from pathlib import Path
import pandas as pd

def load_dataset(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".parquet", ".pq"}:
        try:
            return pd.read_parquet(path)
        except ImportError as exc:
            raise RuntimeError(
                "Parquet support requires: pip install -e \".[parquet]\""
            ) from exc
    raise ValueError(f"Unsupported dataset format: {suffix}")
