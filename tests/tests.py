import pytest
from datetime import datetime
from examples.smelly_program import BookstoreManager 

# ---------- TEST 1 ----------
def test_add_book_to_inventory():
    store = BookstoreManager()
    book_id = store.add_book_to_inventory(
        "Test Book", "Author A", 25.50, 10, "123-456", "fiction", "Publisher A", 2021
    )
    assert book_id == 1
    assert len(store.books) == 1
    assert store.books[0].title == "Test Book"

# ---------- TEST 2 ----------
def test_add_customer():
    store = BookstoreManager()
    customer_id = store.add_customer(
        "Alice", "alice@example.com", "555-1111", "123 Elm St", "basic"
    )
    assert customer_id == 1
    assert len(store.customers) == 1
    assert store.customers[0].membership_level == "basic"

# ---------- TEST 3 ----------
def test_validate_book_availability_true():
    store = BookstoreManager()
    store.add_book_to_inventory("Book1", "Author", 20, 5, "111", "fiction", "Pub", 2022)
    result = store.validate_book_availability([1], [2])
    assert result is True

# ---------- TEST 4 ----------
def test_validate_book_availability_false():
    store = BookstoreManager()
    store.add_book_to_inventory("Book1", "Author", 20, 1, "111", "fiction", "Pub", 2022)
    result = store.validate_book_availability([1], [5])
    assert result is False

# ---------- TEST 5 ----------
def test_process_customer_order_success():
    store = BookstoreManager()
    store.add_book_to_inventory("Book A", "Author", 10, 10, "111", "fiction", "Pub", 2023)
    cust_id = store.add_customer("Bob", "bob@mail.com", "555-1234", "456 Main St", "premium")
    
    order_id = store.process_customer_order_with_complex_calculations_and_validations_and_inventory_updates(
        cust_id, [1], [2], "credit", "456 Main St", "456 Main St", "", ""
    )
    assert order_id == 1
    assert len(store.sales) == 1
    assert store.books[0].quantity == 8  # inventory reduced

# ---------- TEST 6 ----------
def test_process_customer_order_invalid_customer():
    store = BookstoreManager()
    store.add_book_to_inventory("Book A", "Author", 10, 10, "111", "fiction", "Pub", 2023)
    result = store.process_customer_order_with_complex_calculations_and_validations_and_inventory_updates(
        999, [1], [2], "credit", "456 Main St", "456 Main St", "", ""
    )
    assert result is None

# ---------- TEST 7 ----------
def test_calculate_shipping_cost_duplicate():
    store = BookstoreManager()
    cost_basic = store.calculate_shipping_cost_duplicate(40, "basic")
    cost_premium = store.calculate_shipping_cost_duplicate(40, "premium")
    assert cost_basic == 9.99
    assert cost_premium == 4.995  # 50% discount for premium

# ---------- TEST 8 ----------
def test_generate_customer_report_with_detailed_analytics():
    store = BookstoreManager()
    cust_id = store.add_customer("Alice", "alice@mail.com", "555-6789", "123 Lane", "basic")
    store.add_book_to_inventory("Book B", "Writer", 15, 10, "222", "fiction", "Pub", 2022)
    store.process_customer_order_with_complex_calculations_and_validations_and_inventory_updates(
        cust_id, [1], [1], "credit", "123 Lane", "123 Lane", "", ""
    )
    report = store.generate_customer_report_with_detailed_analytics(cust_id)
    assert report["customer_name"] == "Alice"
    assert "total_books_purchased" in report 
