# Code Smells Documentation

This document identifies the six intentional code smells in `smelly_program.py` and their locations.

## 1. Long Method
**Location:** `smelly_program.py`, lines 92-223
**Method:** `process_customer_order_with_complex_calculations_and_validations_and_inventory_updates`
**Justification:** This method contains 130+ lines of code with high cyclomatic complexity, handling multiple responsibilities including validation, calculation, payment processing, inventory updates, and customer management.

## 2. God Class (Blob)
**Location:** `smelly_program.py`, lines 66-343
**Class:** `BookstoreManager`
**Justification:** This class handles too many responsibilities including inventory management, customer management, order processing, payment handling, reporting, and business logic calculations. It has 8+ methods and manages multiple data structures.

## 3. Duplicated Code
**Location 1:** `smelly_program.py`, lines 110-120 (inside `process_customer_order...`)
**Location 2:** `smelly_program.py`, lines 225-239 (`validate_book_availability` method)
**Location 3:** `smelly_program.py`, lines 241-255 (`calculate_shipping_cost_duplicate` method)
**Justification:** Similar validation logic for book availability appears in multiple places, and shipping cost calculation is duplicated with slight variations.

## 4. Large Parameter List
**Location:** `smelly_program.py`, line 83
**Method:** `add_book_to_inventory`
**Parameters:** 8 parameters (title, author, price, quantity, isbn, category, publisher, year)
**Justification:** This method takes 8 parameters, making it difficult to call and maintain. Should use a Book object or builder pattern instead.

## 5. Magic Numbers
**Locations:** Throughout the file, particularly:
- Lines 25, 26 (Customer class random ranges)
- Lines 98, 131, 137, 141, 144, 165, 166, 167, 168, 169, 177, 182 (discount percentages and thresholds)
- Lines 218, 219, 220, 221 (membership upgrade thresholds)
- Lines 245, 246, 247, 248, 253 (shipping cost calculations)
- Lines 271, 274, 285, 288 (credit score and transaction limits)
**Justification:** Hard-coded numeric values like 0.9, 0.85, 50, 100, 1000, 500, 600, 30, etc. appear without explanation, reducing code readability and maintainability.

## 6. Feature Envy
**Location 1:** `smelly_program.py`, lines 257-291
**Method:** `verify_large_transaction`
**Location 2:** `smelly_program.py`, lines 293-333
**Method:** `generate_customer_report_with_detailed_analytics`
**Justification:** These methods primarily use data and methods from the Customer objects rather than the BookstoreManager class itself, indicating they might belong in a Customer class instead. The methods extensively access Customer object properties like `customer.credit_score`, `customer.account_age_days`, `customer.credit_limit`, `customer.name`, `customer.email`, etc., making them "envious" of the Customer class's data and functionality.
