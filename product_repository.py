"""
Product & Service catalog repository.
"""
from typing import List, Dict, Any, Optional
from src.database.db_manager import DatabaseManager


class ProductRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_all(self, search_query: str = "") -> List[Dict[str, Any]]:
        """Fetch all products or filter by search query."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            if search_query.strip():
                term = f"%{search_query.strip()}%"
                cursor.execute("""
                    SELECT * FROM products 
                    WHERE name LIKE ? OR description LIKE ? OR hsn_code LIKE ?
                    ORDER BY name ASC
                """, (term, term, term))
            else:
                cursor.execute("SELECT * FROM products ORDER BY name ASC")
            
            return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Fetch product by ID."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def add(self, product_data: Dict[str, Any]) -> int:
        """Add a new product or service."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (name, description, hsn_code, unit, default_rate, tax_rate)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                product_data.get("name", "").strip(),
                product_data.get("description", "").strip(),
                product_data.get("hsn_code", "").strip(),
                product_data.get("unit", "NOS").strip(),
                float(product_data.get("default_rate", 0.0) or 0.0),
                float(product_data.get("tax_rate", 18.0) or 18.0)
            ))
            conn.commit()
            return cursor.lastrowid

    def update(self, product_id: int, product_data: Dict[str, Any]) -> bool:
        """Update an existing product or service."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products 
                SET name = ?, description = ?, hsn_code = ?, unit = ?, default_rate = ?, tax_rate = ?
                WHERE id = ?
            """, (
                product_data.get("name", "").strip(),
                product_data.get("description", "").strip(),
                product_data.get("hsn_code", "").strip(),
                product_data.get("unit", "NOS").strip(),
                float(product_data.get("default_rate", 0.0) or 0.0),
                float(product_data.get("tax_rate", 18.0) or 18.0),
                product_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, product_id: int) -> bool:
        """Delete a product from the catalog."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            return cursor.rowcount > 0

    def count(self) -> int:
        """Count total products."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            return cursor.fetchone()[0]
