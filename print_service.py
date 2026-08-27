"""
System Print and File Launcher service.
"""
import os
import sys
import subprocess
from pathlib import Path


class PrintService:
    @staticmethod
    def open_file(file_path: Path | str) -> bool:
        """Open a file in its default system viewer."""
        try:
            path_str = str(file_path)
            if sys.platform.startswith("win"):
                os.startfile(path_str)
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", path_str])
            else:
                subprocess.Popen(["xdg-open", path_str])
            return True
        except Exception as e:
            print(f"Error opening file {file_path}: {e}")
            return False

    @staticmethod
    def print_file(file_path: Path | str) -> bool:
        """Send the file directly to the system default printer or print dialog."""
        try:
            path_str = str(file_path)
            if sys.platform.startswith("win"):
                try:
                    os.startfile(path_str, "print")
                except Exception:
                    # Fallback to opening file if print verb is not configured
                    os.startfile(path_str)
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["lp", path_str])
            else:
                subprocess.Popen(["lpr", path_str])
            return True
        except Exception as e:
            print(f"Error printing file {file_path}: {e}")
            return False
