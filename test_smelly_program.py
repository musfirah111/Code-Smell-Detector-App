"""
Unit tests for the smelly bookstore program.
These tests pass despite the code smells.
"""

import unittest
from datetime import datetime
from smelly_program import BookstoreManager

class TestBookstoreManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.store = BookstoreManager()
        
    def test_add_book_to_inventory(self):
        """Test adding a book to inventory."""
        book_id = self.store.add_book_to_inventory(
            "Test Book", "Test Author", 19.99, 10,
            "978-1111111111", "fiction", "Test Publisher", 2023
        )
        self.assertEqual(book_id, 1)
        self.assertEqual(len(self.store.books), 1)
        self.assertEqual(self.store.books[0].title, "Test Book")
        
    def test_add_customer(self):
        """Test adding a customer."""
        customer_id = self.store.add_customer(
            "Test Customer", "test@email.com", "555-0000", "Test Address"
        )
        self.assertEqual(customer_id, 1)
        self.assertEqual(len(self.store.customers), 1)
        self.assertEqual(self.store.customers[0].name, "Test Customer")
        
    def test_validate_book_availability_success(self):
        """Test book availability validation with available books."""
        self.store.add_book_to_inventory(
            "Available Book", "Author", 25.99, 5,
            "978-2222222222", "fiction", "Publisher", 2023
        )
        result = self.store.validate_book_availability([1], [3])
        self.assertTrue(result)
        
    def test_validate_book_availability_failure(self):
        """Test book availability validation with insufficient stock."""
        self.store.add_book_to_inventory(
            "Limited Book", "Author", 25.99, 2,
            "978-3333333333", "fiction", "Publisher", 2023
        )
        result = self.store.validate_book_availability([1], [5])
        self.assertFalse(result)
        
    def test_calculate_shipping_cost_duplicate(self):
        """Test shipping cost calculation."""
        # Test low amount
        cost = self.store.calculate_shipping_cost_duplicate(30, 'basic')
        self.assertEqual(cost, 9.99)
        
        # Test medium amount
        cost = self.store.calculate_shipping_cost_duplicate(75, 'basic')
        self.assertEqual(cost, 4.99)
        
        # Test high amount
        cost = self.store.calculate_shipping_cost_duplicate(150, 'basic')
        self.assertEqual(cost, 0)
        
    def test_verify_large_transaction_success(self):
        """Test large transaction verification with valid customer."""
        customer_id = self.store.add_customer(
            "Rich Customer", "rich@email.com", "555-1111", "Rich Address"
        )
        # Manually set customer properties for test
        self.store.customers[0].credit_score = 750
        self.store.customers[0].account_age_days = 60
        self.store.customers[0].credit_limit = 5000
        
        result = self.store.verify_large_transaction(customer_id, 1500)
        self.assertTrue(result)
        
    def test_verify_large_transaction_failure(self):
        """Test large transaction verification with invalid customer."""
        customer_id = self.store.add_customer(
            "Poor Customer", "poor@email.com", "555-2222", "Poor Address"
        )
        # Manually set customer properties for test
        self.store.customers[0].credit_score = 500
        self.store.customers[0].account_age_days = 10
        self.store.customers[0].credit_limit = 1000
        
        result = self.store.verify_large_transaction(customer_id, 1500)
        self.assertFalse(result)
        
    def test_generate_customer_report(self):
        """Test customer report generation."""
        customer_id = self.store.add_customer(
            "Report Customer", "report@email.com", "555-3333", "Report Address"
        )
        
        report = self.store.generate_customer_report_with_detailed_analytics(customer_id)
        
        self.assertIsNotNone(report)
        self.assertEqual(report['customer_name'], "Report Customer")
        self.assertEqual(report['email'], "report@email.com")
        self.assertEqual(report['total_spent'], 0)
        self.assertEqual(report['order_count'], 0)

if __name__ == '__main__':
    unittest.main()
