import os
import sys
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ASSETS_DIR = PROJECT_ROOT / "assets"
INVOICES_DIR = PROJECT_ROOT / "Invoices"
DATABASE_PATH = DATA_DIR / "invoice_manager.db"

# Ensure essential directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
INVOICES_DIR.mkdir(parents=True, exist_ok=True)

# App Info
APP_NAME = "Namura Invoice Studio"
APP_SUBTITLE = "Professional GST Invoice Management System"
APP_VERSION = "1.0.0"

# Theme & Colors (Modern Executive Palette)
THEME_MODE = "Dark"  # "System", "Dark", "Light"
COLOR_PRIMARY = "#2563EB"       # Royal Blue
COLOR_PRIMARY_HOVER = "#1D4ED8"
COLOR_SECONDARY = "#475569"     # Slate Gray
COLOR_SECONDARY_HOVER = "#334155"
COLOR_ACCENT = "#0EA5E9"        # Sky Blue
COLOR_SUCCESS = "#10B981"       # Emerald Green
COLOR_WARNING = "#F59E0B"       # Amber
COLOR_DANGER = "#EF4444"        # Crimson Red
COLOR_INFO = "#6366F1"          # Indigo

# Dark Theme Backgrounds & Surfaces
BG_DARK = "#0F172A"             # Dark Slate Base
CARD_DARK = "#1E293B"           # Card Container Surface
SIDEBAR_DARK = "#0B1120"        # Sidebar Deep Navy
BORDER_DARK = "#334155"         # Subtle Border
TEXT_LIGHT = "#F8FAFC"          # Crisp White Text
TEXT_MUTED = "#94A3B8"          # Secondary Text

# Light Theme Surfaces
BG_LIGHT = "#F8FAFC"
CARD_LIGHT = "#FFFFFF"
SIDEBAR_LIGHT = "#F1F5F9"
BORDER_LIGHT = "#E2E8F0"
TEXT_DARK = "#0F172A"
TEXT_MUTED_LIGHT = "#64748B"

# Default GST Rates (percentage)
GST_RATES = [0.0, 5.0, 12.0, 18.0, 28.0]
DEFAULT_CGST_RATE = 9.0
DEFAULT_SGST_RATE = 9.0
DEFAULT_IGST_RATE = 0.0

# Predefined standard copy options matching reference invoice
COPY_TYPES = [
    "Original Copy",
    "Duplicate Copy",
    "Triplicate Copy",
    "Extra Copy"
]

PAYMENT_STATUSES = [
    "Paid",
    "Unpaid",
    "Pending",
    "Partially Paid"
]

PAYMENT_METHODS = [
    "Cash",
    "Bank Transfer / NEFT / RTGS",
    "UPI / GPay / PhonePe",
    "Cheque",
    "Credit / Debit Card",
    "Online Gateway"
]
