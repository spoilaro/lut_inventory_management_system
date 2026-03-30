import unittest
import sqlite3
import os
import tempfile
import time

import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

with open("dashboard.py", "r") as f:
    exec(
        f.read()
        .replace("from PIL import Image, ImageTk", "")
        .replace("from employee import employeeClass", "")
        .replace("from supplier import supplierClass", "")
        .replace("from category import categoryClass", "")
        .replace("from product import productClass", "")
        .replace("from sales import salesClass", "")
    )


class TestDatabaseIntegration(unittest.TestCase):
    """Integration tests for database operations using real database."""

    def setUp(self):
        """Create a temporary database for testing."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.test_db.close()
        self.db_path = self.test_db.name
        self._create_tables()
        self._insert_test_data()

    def _create_tables(self):
        """Create all required tables."""
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()

        self.cur.execute("""
            CREATE TABLE employee (
                eid INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT,
                gender TEXT,
                contact TEXT,
                dob TEXT,
                doj TEXT,
                pass TEXT,
                utype TEXT,
                address TEXT,
                salary TEXT
            )
        """)

        self.cur.execute("""
            CREATE TABLE supplier (
                invoice INTEGER PRIMARY KEY,
                name TEXT,
                contact TEXT,
                desc TEXT
            )
        """)

        self.cur.execute("""
            CREATE TABLE category (
                cid INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        """)

        self.cur.execute("""
            CREATE TABLE product (
                pid INTEGER PRIMARY KEY AUTOINCREMENT,
                Category TEXT,
                Supplier TEXT,
                name TEXT,
                price TEXT,
                qty TEXT,
                status TEXT
            )
        """)

        self.conn.commit()

    def _insert_test_data(self):
        """Insert sample data into tables."""
        self.cur.execute(
            "INSERT INTO employee (eid, name, email, gender, contact, dob, doj, pass, utype, address, salary) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                1,
                "John Doe",
                "john@example.com",
                "Male",
                "1234567890",
                "1990-01-01",
                "2024-01-01",
                "pass123",
                "Admin",
                "123 Main St",
                "50000",
            ),
        )
        self.cur.execute(
            "INSERT INTO employee (eid, name, email, gender, contact, dob, doj, pass, utype, address, salary) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                2,
                "Jane Smith",
                "jane@example.com",
                "Female",
                "0987654321",
                "1992-05-15",
                "2024-02-01",
                "pass456",
                "Employee",
                "456 Oak Ave",
                "40000",
            ),
        )
        self.cur.execute(
            "INSERT INTO supplier (invoice, name, contact, desc) VALUES (?, ?, ?, ?)",
            (1001, "Acme Corp", "555-1234", "Office supplies"),
        )
        self.cur.execute(
            "INSERT INTO supplier (invoice, name, contact, desc) VALUES (?, ?, ?, ?)",
            (1002, "Tech Solutions", "555-5678", "Electronics"),
        )

        self.cur.execute("INSERT INTO category (name) VALUES (?)", ("Electronics",))
        self.cur.execute("INSERT INTO category (name) VALUES (?)", ("Furniture",))

        self.cur.execute(
            "INSERT INTO product (Category, Supplier, name, price, qty, status) VALUES (?, ?, ?, ?, ?, ?)",
            ("Electronics", "Tech Solutions", "Laptop", "999.99", "10", "Active"),
        )
        self.cur.execute(
            "INSERT INTO product (Category, Supplier, name, price, qty, status) VALUES (?, ?, ?, ?, ?, ?)",
            ("Electronics", "Tech Solutions", "Phone", "599.99", "25", "Active"),
        )
        self.cur.execute(
            "INSERT INTO product (Category, Supplier, name, price, qty, status) VALUES (?, ?, ?, ?, ?, ?)",
            ("Furniture", "Acme Corp", "Desk", "299.99", "5", "Active"),
        )

        self.conn.commit()
        self.conn.close()

    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_database_has_all_tables(self):
        """Integration test: Verify all required tables exist in database."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        tables = [row[0] for row in cur.fetchall()]
        conn.close()

        self.assertIn("employee", tables)
        self.assertIn("supplier", tables)
        self.assertIn("category", tables)
        self.assertIn("product", tables)
        self.assertEqual(len(tables), 4)

    def test_crud_operations_integration(self):
        """Integration test: Full CRUD workflow on employee table."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM employee")
        initial_count = cur.fetchone()[0]
        self.assertEqual(initial_count, 2)

        cur.execute(
            "INSERT INTO employee (eid, name, email, gender, contact, dob, doj, pass, utype, address, salary) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                3,
                "Bob Wilson",
                "bob@example.com",
                "Male",
                "1112223333",
                "1988-03-20",
                "2024-03-01",
                "pass789",
                "Employee",
                "789 Pine Rd",
                "45000",
            ),
        )
        conn.commit()

        cur.execute("SELECT COUNT(*) FROM employee")
        self.assertEqual(cur.fetchone()[0], 3)

        cur.execute("UPDATE employee SET salary='55000' WHERE eid=3")
        conn.commit()

        cur.execute("SELECT salary FROM employee WHERE eid=3")
        updated_salary = cur.fetchone()[0]
        self.assertEqual(updated_salary, "55000")

        cur.execute("DELETE FROM employee WHERE eid=3")
        conn.commit()

        cur.execute("SELECT COUNT(*) FROM employee")
        self.assertEqual(cur.fetchone()[0], 2)

        conn.close()

    def test_stat_counts_match_actual_data(self):
        """Integration test: Verify stat counts match actual database records."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM employee")
        employee_count = cur.fetchone()[0]
        self.assertEqual(employee_count, 2)

        cur.execute("SELECT COUNT(*) FROM supplier")
        supplier_count = cur.fetchone()[0]
        self.assertEqual(supplier_count, 2)

        cur.execute("SELECT COUNT(*) FROM category")
        category_count = cur.fetchone()[0]
        self.assertEqual(category_count, 2)

        cur.execute("SELECT COUNT(*) FROM product")
        product_count = cur.fetchone()[0]
        self.assertEqual(product_count, 3)

        conn.close()


class TestBillFileIntegration(unittest.TestCase):
    """Integration tests for bill file operations."""

    def setUp(self):
        """Create a temporary bill directory."""
        self.test_bill_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test bill directory."""
        for filename in os.listdir(self.test_bill_dir):
            file_path = os.path.join(self.test_bill_dir, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        os.rmdir(self.test_bill_dir)

    def _create_bill_file(
        self, invoice_number: int, customer_name: str, amount: float
    ) -> str:
        """Helper to create a test bill file."""
        filename = f"{invoice_number}.txt"
        filepath = os.path.join(self.test_bill_dir, filename)

        content = f"""
        XYZ-Inventory
        Phone No. 9899459288, Delhi-110053
        ==============================================
        Customer Name: {customer_name}
        Bill No. {invoice_number}           Date: {time.strftime("%d/%m/%Y")}
        ==============================================
        Total Amount: Rs.{amount}
        ==============================================
        """

        with open(filepath, "w") as f:
            f.write(content)

        return filepath

    def test_bill_file_creation_and_retrieval(self):
        """Integration test: Create bill files and verify they can be retrieved."""
        self._create_bill_file(1001, "Test Customer", 500.00)
        self._create_bill_file(1002, "Another Customer", 750.50)
        self._create_bill_file(1003, "Third Customer", 299.99)

        bill_files = [f for f in os.listdir(self.test_bill_dir) if f.endswith(".txt")]
        self.assertEqual(len(bill_files), 3)

        invoice_numbers = [f.replace(".txt", "") for f in bill_files]
        self.assertIn("1001", invoice_numbers)
        self.assertIn("1002", invoice_numbers)
        self.assertIn("1003", invoice_numbers)

    def test_bill_content_integrity(self):
        """Integration test: Verify bill file content matches what was written."""
        filepath = self._create_bill_file(2001, "John Doe", 1234.56)

        with open(filepath, "r") as f:
            content = f.read()

        self.assertIn("John Doe", content)
        self.assertIn("2001", content)
        self.assertIn("1234.56", content)
        self.assertIn("XYZ-Inventory", content)

    def test_bill_deletion_and_count_update(self):
        """Integration test: Simulate bill deletion and count update."""
        self._create_bill_file(3001, "Customer A", 100.00)
        self._create_bill_file(3002, "Customer B", 200.00)

        bill_count = len(os.listdir(self.test_bill_dir))
        self.assertEqual(bill_count, 2)

        file_to_delete = os.path.join(self.test_bill_dir, "3001.txt")
        os.unlink(file_to_delete)

        bill_count_after = len(os.listdir(self.test_bill_dir))
        self.assertEqual(bill_count_after, 1)

        remaining_files = os.listdir(self.test_bill_dir)
        self.assertIn("3002.txt", remaining_files)


if __name__ == "__main__":
    unittest.main()
