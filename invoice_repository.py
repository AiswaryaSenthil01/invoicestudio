"""
Invoice and Invoice Items repository with transaction management, filtering, and reporting.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.database.db_manager import DatabaseManager


class InvoiceRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def create(self, invoice_data: Dict[str, Any], items: List[Dict[str, Any]]) -> int:
        """Create a new invoice and its associated line items in an atomic transaction."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO invoices (
                    invoice_no, invoice_date, due_date, po_no, po_date, vehicle_no,
                    copy_type, customer_id, billed_to_name, billed_to_address,
                    billed_to_phone, billed_to_email, billed_to_gstin, billed_to_state_code,
                    shipped_to_name, shipped_to_address, shipped_to_phone, shipped_to_email,
                    shipped_to_gstin, shipped_to_state_code, subtotal, cgst_rate, cgst_amount,
                    sgst_rate, sgst_amount, igst_rate, igst_amount, total_tax, grand_total,
                    total_in_words, payment_status, payment_method, notes, terms,
                    pdf_path, docx_path
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                invoice_data.get("invoice_no", "").strip(),
                invoice_data.get("invoice_date", "").strip(),
                invoice_data.get("due_date", ""),
                invoice_data.get("po_no", "").strip(),
                invoice_data.get("po_date", "").strip(),
                invoice_data.get("vehicle_no", "").strip(),
                invoice_data.get("copy_type", "Original Copy"),
                invoice_data.get("customer_id"),
                invoice_data.get("billed_to_name", "").strip(),
                invoice_data.get("billed_to_address", "").strip(),
                invoice_data.get("billed_to_phone", "").strip(),
                invoice_data.get("billed_to_email", "").strip(),
                invoice_data.get("billed_to_gstin", "").strip().upper(),
                invoice_data.get("billed_to_state_code", "").strip(),
                invoice_data.get("shipped_to_name", "").strip(),
                invoice_data.get("shipped_to_address", "").strip(),
                invoice_data.get("shipped_to_phone", "").strip(),
                invoice_data.get("shipped_to_email", "").strip(),
                invoice_data.get("shipped_to_gstin", "").strip().upper(),
                invoice_data.get("shipped_to_state_code", "").strip(),
                float(invoice_data.get("subtotal", 0.0)),
                float(invoice_data.get("cgst_rate", 0.0)),
                float(invoice_data.get("cgst_amount", 0.0)),
                float(invoice_data.get("sgst_rate", 0.0)),
                float(invoice_data.get("sgst_amount", 0.0)),
                float(invoice_data.get("igst_rate", 0.0)),
                float(invoice_data.get("igst_amount", 0.0)),
                float(invoice_data.get("total_tax", 0.0)),
                float(invoice_data.get("grand_total", 0.0)),
                invoice_data.get("total_in_words", ""),
                invoice_data.get("payment_status", "Unpaid"),
                invoice_data.get("payment_method", ""),
                invoice_data.get("notes", ""),
                invoice_data.get("terms", ""),
                invoice_data.get("pdf_path", ""),
                invoice_data.get("docx_path", "")
            ))
            
            invoice_id = cursor.lastrowid

            for idx, item in enumerate(items, start=1):
                cursor.execute("""
                    INSERT INTO invoice_items (
                        invoice_id, s_no, description, hsn_code, quantity, unit, rate, amount
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    invoice_id,
                    item.get("s_no", idx),
                    item.get("description", "").strip(),
                    item.get("hsn_code", "").strip(),
                    float(item.get("quantity", 1.0)),
                    item.get("unit", "NOS").strip(),
                    float(item.get("rate", 0.0)),
                    float(item.get("amount", 0.0))
                ))

            conn.commit()
            return invoice_id

    def update(self, invoice_id: int, invoice_data: Dict[str, Any], items: List[Dict[str, Any]]) -> bool:
        """Update existing invoice and replace its items."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE invoices SET
                    invoice_no = ?, invoice_date = ?, due_date = ?, po_no = ?, po_date = ?, vehicle_no = ?,
                    copy_type = ?, customer_id = ?, billed_to_name = ?, billed_to_address = ?,
                    billed_to_phone = ?, billed_to_email = ?, billed_to_gstin = ?, billed_to_state_code = ?,
                    shipped_to_name = ?, shipped_to_address = ?, shipped_to_phone = ?, shipped_to_email = ?,
                    shipped_to_gstin = ?, shipped_to_state_code = ?, subtotal = ?, cgst_rate = ?, cgst_amount = ?,
                    sgst_rate = ?, sgst_amount = ?, igst_rate = ?, igst_amount = ?, total_tax = ?, grand_total = ?,
                    total_in_words = ?, payment_status = ?, payment_method = ?, notes = ?, terms = ?,
                    pdf_path = ?, docx_path = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                invoice_data.get("invoice_no", "").strip(),
                invoice_data.get("invoice_date", "").strip(),
                invoice_data.get("due_date", ""),
                invoice_data.get("po_no", "").strip(),
                invoice_data.get("po_date", "").strip(),
                invoice_data.get("vehicle_no", "").strip(),
                invoice_data.get("copy_type", "Original Copy"),
                invoice_data.get("customer_id"),
                invoice_data.get("billed_to_name", "").strip(),
                invoice_data.get("billed_to_address", "").strip(),
                invoice_data.get("billed_to_phone", "").strip(),
                invoice_data.get("billed_to_email", "").strip(),
                invoice_data.get("billed_to_gstin", "").strip().upper(),
                invoice_data.get("billed_to_state_code", "").strip(),
                invoice_data.get("shipped_to_name", "").strip(),
                invoice_data.get("shipped_to_address", "").strip(),
                invoice_data.get("shipped_to_phone", "").strip(),
                invoice_data.get("shipped_to_email", "").strip(),
                invoice_data.get("shipped_to_gstin", "").strip().upper(),
                invoice_data.get("shipped_to_state_code", "").strip(),
                float(invoice_data.get("subtotal", 0.0)),
                float(invoice_data.get("cgst_rate", 0.0)),
                float(invoice_data.get("cgst_amount", 0.0)),
                float(invoice_data.get("sgst_rate", 0.0)),
                float(invoice_data.get("sgst_amount", 0.0)),
                float(invoice_data.get("igst_rate", 0.0)),
                float(invoice_data.get("igst_amount", 0.0)),
                float(invoice_data.get("total_tax", 0.0)),
                float(invoice_data.get("grand_total", 0.0)),
                invoice_data.get("total_in_words", ""),
                invoice_data.get("payment_status", "Unpaid"),
                invoice_data.get("payment_method", ""),
                invoice_data.get("notes", ""),
                invoice_data.get("terms", ""),
                invoice_data.get("pdf_path", ""),
                invoice_data.get("docx_path", ""),
                invoice_id
            ))

            # Replace items
            cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
            for idx, item in enumerate(items, start=1):
                cursor.execute("""
                    INSERT INTO invoice_items (
                        invoice_id, s_no, description, hsn_code, quantity, unit, rate, amount
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    invoice_id,
                    item.get("s_no", idx),
                    item.get("description", "").strip(),
                    item.get("hsn_code", "").strip(),
                    float(item.get("quantity", 1.0)),
                    item.get("unit", "NOS").strip(),
                    float(item.get("rate", 0.0)),
                    float(item.get("amount", 0.0))
                ))

            conn.commit()
            return True

    def get_by_id(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        """Fetch invoice with its associated line items."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
            inv_row = cursor.fetchone()
            if not inv_row:
                return None

            inv_dict = dict(inv_row)
            cursor.execute("SELECT * FROM invoice_items WHERE invoice_id = ? ORDER BY s_no ASC", (invoice_id,))
            inv_dict["items"] = [dict(r) for r in cursor.fetchall()]
            return inv_dict

    def get_by_invoice_no(self, invoice_no: str) -> Optional[Dict[str, Any]]:
        """Fetch invoice by invoice number."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM invoices WHERE invoice_no = ?", (invoice_no,))
            inv_row = cursor.fetchone()
            if not inv_row:
                return None
            inv_dict = dict(inv_row)
            cursor.execute("SELECT * FROM invoice_items WHERE invoice_id = ? ORDER BY s_no ASC", (inv_dict["id"],))
            inv_dict["items"] = [dict(r) for r in cursor.fetchall()]
            return inv_dict

    def get_all(
        self,
        search_query: str = "",
        status_filter: str = "All",
        date_from: str = "",
        date_to: str = "",
        sort_by: str = "created_at",
        sort_order: str = "DESC"
    ) -> List[Dict[str, Any]]:
        """Query invoices with multi-field search and filters."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM invoices WHERE 1=1"
            params = []

            if search_query.strip():
                term = f"%{search_query.strip()}%"
                query += " AND (invoice_no LIKE ? OR billed_to_name LIKE ? OR po_no LIKE ? OR vehicle_no LIKE ?)"
                params.extend([term, term, term, term])

            if status_filter and status_filter != "All":
                query += " AND payment_status = ?"
                params.append(status_filter)

            if date_from.strip():
                query += " AND invoice_date >= ?"
                params.append(date_from.strip())

            if date_to.strip():
                query += " AND invoice_date <= ?"
                params.append(date_to.strip())

            valid_sort_cols = ["id", "invoice_no", "invoice_date", "billed_to_name", "grand_total", "payment_status", "created_at"]
            sort_col = sort_by if sort_by in valid_sort_cols else "id"
            order = "DESC" if sort_order.upper() == "DESC" else "ASC"

            query += f" ORDER BY {sort_col} {order}"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def delete(self, invoice_id: int) -> bool:
        """Delete an invoice."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
            conn.commit()
            return cursor.rowcount > 0

    def update_payment_status(self, invoice_id: int, status: str) -> bool:
        """Quickly update payment status (Paid, Unpaid, Pending)."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE invoices SET payment_status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (status, invoice_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Aggregate high-level business metrics for the dashboard."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()

            # Total invoices & total billed revenue
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(grand_total), 0) FROM invoices")
            total_count, total_revenue = cursor.fetchone()

            # Paid amount & count
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(grand_total), 0) FROM invoices WHERE payment_status = 'Paid'")
            paid_count, paid_amount = cursor.fetchone()

            # Unpaid / Pending amount & count
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(grand_total), 0) FROM invoices WHERE payment_status IN ('Unpaid', 'Pending')")
            unpaid_count, unpaid_amount = cursor.fetchone()

            # Customers count
            cursor.execute("SELECT COUNT(*) FROM customers")
            customer_count = cursor.fetchone()[0]

            # Products count
            cursor.execute("SELECT COUNT(*) FROM products")
            product_count = cursor.fetchone()[0]

            # Recent 5 invoices
            cursor.execute("SELECT * FROM invoices ORDER BY id DESC LIMIT 5")
            recent_invoices = [dict(r) for r in cursor.fetchall()]

            return {
                "total_invoices": total_count,
                "total_revenue": total_revenue,
                "paid_count": paid_count,
                "paid_amount": paid_amount,
                "unpaid_count": unpaid_count,
                "unpaid_amount": unpaid_amount,
                "customer_count": customer_count,
                "product_count": product_count,
                "recent_invoices": recent_invoices
            }
