from pathlib import Path
import os

PRACTICE_DATA_DIR = Path(os.environ["PRACTICE_DATA_DIR"])
ENV = os.getenv("ENV", "local")
