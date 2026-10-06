"""Caminhos do projeto, relativos à raiz: funcionam de qualquer pasta (inclusive de notebooks/)."""
from pathlib import Path

from dotenv import load_dotenv

PROJ_ROOT = Path(__file__).resolve().parents[1]

# Credenciais da AISWEB (AISWEB_API_KEY e AISWEB_API_PASS)
load_dotenv(PROJ_ROOT / ".env")

DATA_DIR = PROJ_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

MODELS_DIR = PROJ_ROOT / "models"

REPORTS_DIR = PROJ_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
