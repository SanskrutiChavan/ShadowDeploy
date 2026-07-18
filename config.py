from dotenv import load_dotenv
import os

load_dotenv()  # reads .env file automatically

# ── Kubernetes ────────────────────────────────────────────
NAMESPACE = os.getenv("KUBE_NAMESPACE", "default")
WATCH_INTERVAL = int(os.getenv("WATCH_INTERVAL", "10"))

# ── Ollama (Phase 5) ──────────────────────────────────────
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

# ── Telegram (Phase 7) ────────────────────────────────────
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ── Database (Phase 6) ────────────────────────────────────
DB_PATH = os.getenv("DB_PATH", "database/incidents.db")

# ── Email (Phase 6) ───────────────────────────────────────

EMAIL_SENDER = os.getenv(
    "EMAIL_SENDER",
    ""
)

EMAIL_APP_PASSWORD = os.getenv(
    "EMAIL_APP_PASSWORD",
    ""
)

EMAIL_RECEIVER = os.getenv(
    "EMAIL_RECEIVER",
    ""
)

SMTP_HOST = os.getenv(
    "SMTP_HOST",
    "smtp.gmail.com"
)

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "587"
    )
)