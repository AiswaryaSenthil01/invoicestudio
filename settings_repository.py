"""
Company settings repository.
"""
from typing import Dict, Any, Optional
from src.database.db_manager import DatabaseManager


class SettingsRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_settings(self) -> Dict[str, Any]:
        """Fetch company settings."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM company_settings WHERE id = 1")
            row = cursor.fetchone()
            if row:
                return dict(row)
            return {}

    def update_settings(self, settings_data: Dict[str, Any]) -> bool:
        """Update company settings."""
        fields = [
            "company_name", "address", "phone", "email", "gstin", "pan",
            "state_code", "logo_path", "invoice_prefix", "next_invoice_num",
            "invoice_num_padding", "default_cgst_rate", "default_sgst_rate",
            "default_igst_rate", "bank_name", "bank_acc_no", "bank_ifsc",
            "bank_branch", "upi_id", "default_terms", "declaration"
        ]
        
        updates = []
        values = []
        for field in fields:
            if field in settings_data:
                updates.append(f"{field} = ?")
                values.append(settings_data[field])

        if not updates:
            return False

        query = f"UPDATE company_settings SET {', '.join(updates)} WHERE id = 1"
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0

    def get_next_invoice_number(self, increment: bool = False) -> str:
        """
        Generate the next sequential invoice number (e.g. INV-001).
        If increment is True, bumps the sequence counter in the database.
        """
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT invoice_prefix, next_invoice_num, invoice_num_padding FROM company_settings WHERE id = 1")
            row = cursor.fetchone()
            
            prefix = row["invoice_prefix"] if row and row["invoice_prefix"] is not None else "INV-"
            next_num = row["next_invoice_num"] if row and row["next_invoice_num"] is not None else 1
            padding = row["invoice_num_padding"] if row and row["invoice_num_padding"] is not None else 3

            # Check if this invoice number already exists, bump if necessary to prevent duplicates
            while True:
                candidate = f"{prefix}{str(next_num).zfill(padding)}"
                cursor.execute("SELECT COUNT(*) FROM invoices WHERE invoice_no = ?", (candidate,))
                if cursor.fetchone()[0] == 0:
                    break
                next_num += 1

            if increment:
                cursor.execute("UPDATE company_settings SET next_invoice_num = ? WHERE id = 1", (next_num + 1,))
                conn.commit()

            return candidate
