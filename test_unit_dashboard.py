import unittest
import sqlite3
import os
import tempfile
import sys
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

with patch.dict("sys.modules", {"PIL.Image": Mock(), "PIL.ImageTk": Mock()}):
    import dashboard


class TestDashboardConstants(unittest.TestCase):
    """Test suite for dashboard module constants and configuration."""

    def test_stat_colors_mapping(self):
        """Test that all stat categories have defined colors."""
        expected_keys = {"employee", "supplier", "category", "product", "sales"}
        self.assertEqual(set(dashboard.STAT_COLORS.keys()), expected_keys)

    def test_nav_items_structure(self):
        """Test that navigation items are correctly structured."""
        self.assertIsInstance(dashboard.IMS.NAV_ITEMS, list)
        self.assertEqual(len(dashboard.IMS.NAV_ITEMS), 5)

        for item in dashboard.IMS.NAV_ITEMS:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2)
            self.assertIsInstance(item[0], str)
            self.assertIsInstance(item[1], str)

    def test_nav_items_labels(self):
        """Test that navigation items have expected labels."""
        labels = {item[0] for item in dashboard.IMS.NAV_ITEMS}
        expected_labels = {"Employee", "Supplier", "Category", "Products", "Sales"}
        self.assertEqual(labels, expected_labels)


class TestDatabaseHelperMethods(unittest.TestCase):
    """Test suite for database-related helper methods."""

    def setUp(self):
        """Create a temporary test database."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.test_db.close()
        self.test_db_path = self.test_db.name

        self.conn = sqlite3.connect(self.test_db_path)
        self.cur = self.conn.cursor()
        self._create_test_tables()

    def _create_test_tables(self):
        """Create test tables with sample data."""
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
                cid INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        self.cur.execute("""
            CREATE TABLE product (
                pid INTEGER PRIMARY KEY,
                Category TEXT,
                Supplier TEXT,
                name TEXT,
                price TEXT,
                qty TEXT,
                status TEXT
            )
        """)
        self.conn.commit()

    def tearDown(self):
        """Close connection and remove test database."""
        self.conn.close()
        os.unlink(self.test_db_path)

    def test_count_records_returns_correct_count(self):
        """Test that _count_records returns correct count for each table."""
        self.cur.execute("INSERT INTO employee (eid, name) VALUES (1, 'Test')")
        self.cur.execute("INSERT INTO employee (eid, name) VALUES (2, 'Test2')")
        self.conn.commit()

        self.cur.execute("INSERT INTO category (cid, name) VALUES (1, 'Electronics')")
        self.conn.commit()

        self.cur.execute("INSERT INTO product (pid, name) VALUES (1, 'Laptop')")
        self.cur.execute("INSERT INTO product (pid, name) VALUES (2, 'Phone')")
        self.cur.execute("INSERT INTO product (pid, name) VALUES (3, 'Tablet')")
        self.conn.commit()

        self.assertEqual(dashboard.IMS._count_records(self, self.cur, "employee"), 2)
        self.assertEqual(dashboard.IMS._count_records(self, self.cur, "category"), 1)
        self.assertEqual(dashboard.IMS._count_records(self, self.cur, "product"), 3)
        self.assertEqual(dashboard.IMS._count_records(self, self.cur, "supplier"), 0)

    def test_count_records_empty_table(self):
        """Test that _count_records returns 0 for empty table."""
        result = dashboard.IMS._count_records(self, self.cur, "supplier")
        self.assertEqual(result, 0)

    def test_count_records_nonexistent_table_raises_error(self):
        """Test that _count_records raises error for nonexistent table."""
        with self.assertRaises(sqlite3.OperationalError):
            dashboard.IMS._count_records(self, self.cur, "nonexistent_table")


class TestModuleNavigation(unittest.TestCase):
    """Test suite for module navigation functionality."""

    def test_nav_items_count_matches_expected_modules(self):
        """Test that there are navigation items for all expected modules."""
        expected_modules = {"employee", "supplier", "category", "product", "sales"}
        nav_methods = {item[1] for item in dashboard.IMS.NAV_ITEMS}
        self.assertEqual(nav_methods, expected_modules)


if __name__ == "__main__":
    unittest.main()
