"""Environment: a tiny .env loader and accessors for the few settings we use.

Settings (see .env.example):
    GITHUB_TOKEN         classic PAT; without it we use the public fallback
    GITHUB_LOGIN         GitHub login to show (default SkyeNova)
    SITE_TZ              IANA zone for "today", streaks and the punch card
    GITHUB_HIDE_REPOS    comma list of owner/name to treat as private
    GITHUB_FIRST_YEAR    first year on the heatmap (default 2023)
    GITHUB_FORCE_FIXTURE 1 to render the committed sample data (read per request)
"""
import os
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "cache"
FIXTURE_PATH = ROOT / "data" / "github_fixture.json"
DOTENV_PATH = ROOT / ".env"

_TRUE = {"1", "true", "yes", "on"}


def load_dotenv(path=DOTENV_PATH):
    """KEY=value lines; existing environment wins. Quietly does nothing if absent."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key.startswith("export "):
            key = key[7:].strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key:
            os.environ.setdefault(key, value)


load_dotenv()


def token():
    return os.environ.get("GITHUB_TOKEN", "").strip() or None


def login():
    return os.environ.get("GITHUB_LOGIN", "").strip() or "SkyeNova"


def tz():
    name = os.environ.get("SITE_TZ", "").strip() or "Europe/London"
    try:
        return ZoneInfo(name)
    except Exception:
        return ZoneInfo("Europe/London")


def hidden_repos():
    raw = os.environ.get("GITHUB_HIDE_REPOS", "")
    return {part.strip().lower() for part in raw.split(",") if part.strip()}


def first_year():
    try:
        return int(os.environ.get("GITHUB_FIRST_YEAR", "2023"))
    except ValueError:
        return 2023


def force_fixture():
    return os.environ.get("GITHUB_FORCE_FIXTURE", "").strip().lower() in _TRUE


def mode():
    """Which fetch path applies right now."""
    return "token" if token() else "public"
