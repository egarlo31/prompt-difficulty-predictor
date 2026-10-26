from pathlib import Path
import sys
import pandas as pd


class TacoDatasetBuilder:
    def __init__(self, data_dir: Path | None = None):
        self.data_dir = (
            Path(data_dir)
            if data_dir is not None
            else Path(__file__).resolve().parents[2] / "data"
        )

    def load_candidates(self) -> pd.DataFrame:
        path = self.data_dir / "interim" / "candidate_ids.csv"
        candidates = pd.read_csv(path)
        return self._validate_candidates(candidates)

    @staticmethod
    def _validate_candidates(df: pd.DataFrame) -> pd.DataFrame:
        required = {"split", "idx"}
        if missing := (required - set(df.columns)):
            raise ValueError(f"Missing columns: {missing}")

        df = df.copy()
        
        try:
            df["idx"] = df["idx"].astype("int64")
        except (ValueError, TypeError):
            raise ValueError("Invalid candidate indices")

        if (df["idx"] < 0).any():
            raise ValueError("Invalid candidate indices: negative values found")

        if not df["split"].isin({"train", "test"}).all():
            raise ValueError("Invalid dataset split")

        if df[["split", "idx"]].isna().any().any():
            raise ValueError("Missing candidate identifiers")

        if df.duplicated(subset=["split", "idx"]).any():
            raise ValueError("Duplicate candidates")

        return df

    @staticmethod
    def configure_imports() -> None:
        """Añade la raíz del proyecto al sys.path buscando el directorio 'modeling/src'."""
        current = Path.cwd()
        for parent in (current, *current.parents):
            if (parent / "modeling" / "src").is_dir():
                path_str = str(parent)
                if path_str not in sys.path:
                    sys.path.insert(0, path_str)
                return

        raise FileNotFoundError("Project root containing 'modeling/src' not found")