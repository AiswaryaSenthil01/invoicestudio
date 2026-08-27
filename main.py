"""
Invoice Studio - Desktop Invoice Management System
Entry point for launching the CustomTkinter desktop application.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.gui.app import InvoiceApp


def main():
    try:
        app = InvoiceApp()
        app.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
