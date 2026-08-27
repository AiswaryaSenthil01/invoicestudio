"""
Customer management repository.
"""
from typing import List, Dict, Any, Optional
from src.database.db_manager import DatabaseManager


class CustomerRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_all(self, search_query: str = "") -> List[Dict[str, Any]]:
        """Fetch all customers or filter by search term."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            if search_query.strip():
                term = f"%{search_query.strip()}%"
                cursor.execute("""
                    SELECT * FROM customers 
                    WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? OR gstin LIKE ?
                    ORDER BY name ASC
                """, (term, term, term, term))
            else:
                cursor.execute("SELECT * FROM customers ORDER BY name ASC")
            
            return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single customer by ID."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def add(self, customer_data: Dict[str, Any]) -> int:
        """Insert a new customer."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO customers (name, address, phone, email, gstin, pan, state_code, shipping_address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                customer_data.get("name", "").strip(),
                customer_data.get("address", "").strip(),
                customer_data.get("phone", "").strip(),
                customer_data.get("email", "").strip(),
                customer_data.get("gstin", "").strip().upper(),
                customer_data.get("pan", "").strip().upper(),
                customer_data.get("state_code", "").strip(),
                customer_data.get("shipping_address", "").strip()
            ))
            conn.commit()
            return cursor.lastrowid

    def update(self, customer_id: int, customer_data: Dict[str, Any]) -> bool:
        """Update an existing customer."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE customers 
                SET name = ?, address = ?, phone = ?, email = ?, gstin = ?, pan = ?, state_code = ?, shipping_address = ?
                WHERE id = ?
            """, (
                customer_data.get("name", "").strip(),
                customer_data.get("address", "").strip(),
                customer_data.get("phone", "").strip(),
                customer_data.get("email", "").strip(),
                customer_data.get("gstin", "").strip().upper(),
                customer_data.get("pan", "").strip().upper(),
                customer_data.get("state_code", "").strip(),
                customer_data.get("shipping_address", "").strip(),
                customer_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, customer_id: int) -> bool:
        """Delete a customer."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
            conn.commit()
            return cursor.rowcount > 0

    def count(self) -> int:
        """Count total customers."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers")
            return cursor.fetchone()[0]
