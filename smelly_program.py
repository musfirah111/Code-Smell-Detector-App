"""
A deliberately smelly inventory management system for a bookstore.
This program intentionally contains all 6 required code smells.
"""

import math
import random
from datetime import datetime
from typing import List, Dict, Any

class Customer:
    """
    Customer class - intentionally kept simple to demonstrate Feature Envy
    """
    def __init__(self, name, email, phone, address, membership_level='basic'):
        self.id = 0  # Will be set by BookstoreManager
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.membership_level = membership_level
        self.total_spent = 0
        self.order_count = 0
        self.account_age_days = 0
        self.credit_score = random.randint(300, 850)  # Magic Numbers smell
        self.credit_limit = random.randint(1000, 10000)  # Magic Numbers smell
        self.preferred_categories = []

class Book:
    """
    Book class - intentionally kept simple to demonstrate Feature Envy
    """
    def __init__(self, title, author, price, quantity, isbn, category, publisher, year):
        self.id = 0  # Will be set by BookstoreManager
        self.title = title
        self.author = author
        self.price = price
        self.quantity = quantity
        self.isbn = isbn
        self.category = category
        self.publisher = publisher
        self.year = year

class Order:
    """
    Order class - intentionally kept simple to demonstrate Feature Envy
    """
    def __init__(self, order_id, customer_id, items, subtotal, tax, shipping, total, 
                 payment_method, shipping_address, billing_address, special_instructions, 
                 coupon_code, order_date, status):
        self.id = order_id
        self.customer_id = customer_id
        self.items = items
        self.subtotal = subtotal
        self.tax = tax
        self.shipping = shipping
        self.total = total
        self.payment_method = payment_method
        self.shipping_address = shipping_address
        self.billing_address = billing_address
        self.special_instructions = special_instructions
        self.coupon_code = coupon_code
        self.order_date = order_date
        self.status = status

class BookstoreManager:
    """
    CODE SMELL: God Class (Blob) - This class handles everything: inventory, sales, customers, reports, etc.
    It has too many responsibilities and methods.
    """
    
    def __init__(self):
        self.books = []  # List of Book objects
        self.customers = []  # List of Customer objects
        self.sales = []  # List of Order objects
        self.total_revenue = 0
        self.discount_rate = 0.1
        self.tax_rate = 0.08
        self.shipping_cost = 5.99
        self.premium_threshold = 100
        self.bulk_discount = 0.15
        
    def add_book_to_inventory(self, title, author, price, quantity, isbn, category, publisher, year):
        """
        CODE SMELL: Large Parameter List - This method takes 8 parameters, which is excessive.
        """
        book = Book(title, author, price, quantity, isbn, category, publisher, year)
        book.id = len(self.books) + 1
        self.books.append(book)
        return book.id
    
    def process_customer_order_with_complex_calculations_and_validations_and_inventory_updates(self, customer_id, book_ids, quantities, payment_method, shipping_address, billing_address, special_instructions, coupon_code):
        """
        CODE SMELL: Long Method - This method is excessively long with high cyclomatic complexity.
        It handles order processing, inventory updates, payment, shipping, and more.
        """
        # CODE SMELL: Magic Numbers throughout this method
        if customer_id < 1 or customer_id > 9999:
            return None
            
        customer = None
        for c in self.customers:
            if c.id == customer_id:
                customer = c
                break
                
        if not customer:
            return None
            
        # CODE SMELL: Duplicated Code - validation logic (similar to validate_book_availability)
        for i, book_id in enumerate(book_ids):
            book_found = False
            for book in self.books:
                if book.id == book_id:
                    if book.quantity < quantities[i]:
                        return None
                    book_found = True
                    break
            if not book_found:
                return None
        
        total_cost = 0
        order_items = []
        
        # Complex calculation logic
        for i, book_id in enumerate(book_ids):
            for book in self.books:
                if book.id == book_id:
                    item_cost = book.price * quantities[i]
                    
                    # CODE SMELL: Magic Numbers for discount calculations
                    if quantities[i] >= 5:
                        item_cost *= 0.9  # 10% bulk discount
                    elif quantities[i] >= 3:
                        item_cost *= 0.95  # 5% bulk discount
                        
                    # CODE SMELL: More Magic Numbers
                    if book.category == 'textbook' and quantities[i] >= 2:
                        item_cost *= 0.85  # 15% textbook discount
                        
                    if customer.membership_level == 'premium':
                        item_cost *= 0.92  # 8% premium discount
                    elif customer.membership_level == 'gold':
                        item_cost *= 0.88  # 12% gold discount
                        
                    total_cost += item_cost
                    order_items.append({
                        'book_id': book_id,
                        'quantity': quantities[i],
                        'unit_price': book.price,
                        'total_price': item_cost
                    })
                    break
        
        # Apply coupon if provided
        if coupon_code:
            if coupon_code == 'SAVE10':
                total_cost *= 0.9
            elif coupon_code == 'SAVE20':
                total_cost *= 0.8
            elif coupon_code == 'NEWCUSTOMER':
                total_cost *= 0.85
                
        # Add tax and shipping
        tax_amount = total_cost * 0.08  # CODE SMELL: Magic number
        if total_cost < 50:  # CODE SMELL: Magic number
            shipping_cost = 9.99  # CODE SMELL: Magic number
        elif total_cost < 100:  # CODE SMELL: Magic number
            shipping_cost = 4.99  # CODE SMELL: Magic number
        else:
            shipping_cost = 0
            
        final_total = total_cost + tax_amount + shipping_cost
        
        # Process payment
        if payment_method == 'credit':
            if final_total > 1000:  # CODE SMELL: Magic number
                # Additional verification needed
                if not self.verify_large_transaction(customer_id, final_total):
                    return None
        elif payment_method == 'debit':
            if final_total > 500:  # CODE SMELL: Magic number
                return None
        
        # Update inventory
        for i, book_id in enumerate(book_ids):
            for book in self.books:
                if book.id == book_id:
                    book.quantity -= quantities[i]
                    break
        
        # Create order record
        order = Order(
            order_id=len(self.sales) + 1,
            customer_id=customer_id,
            items=order_items,
            subtotal=total_cost,
            tax=tax_amount,
            shipping=shipping_cost,
            total=final_total,
            payment_method=payment_method,
            shipping_address=shipping_address,
            billing_address=billing_address,
            special_instructions=special_instructions,
            coupon_code=coupon_code,
            order_date=datetime.now(),
            status='confirmed'
        )
        
        self.sales.append(order)
        self.total_revenue += final_total
        
        # Update customer stats
        customer.total_spent += final_total
        customer.order_count += 1
        
        # Check for membership upgrade
        if customer.membership_level == 'basic' and customer.total_spent > 200:  # CODE SMELL: Magic number
            customer.membership_level = 'premium'
        elif customer.membership_level == 'premium' and customer.total_spent > 500:  # CODE SMELL: Magic number
            customer.membership_level = 'gold'
            
        return order.id
    
    def validate_book_availability(self, book_ids, quantities):
        """
        CODE SMELL: Duplicated Code - This validation logic is very similar to the one in process_customer_order
        """
        for i, book_id in enumerate(book_ids):
            book_found = False
            for book in self.books:
                if book.id == book_id:
                    if book.quantity < quantities[i]:
                        return False
                    book_found = True
                    break
            if not book_found:
                return False
        return True
    
    def calculate_shipping_cost_duplicate(self, total_amount, customer_type):
        """
        CODE SMELL: Duplicated Code - Similar shipping calculation logic as in process_customer_order
        """
        if total_amount < 50:  # CODE SMELL: Magic number
            shipping_cost = 9.99  # CODE SMELL: Magic number
        elif total_amount < 100:  # CODE SMELL: Magic number
            shipping_cost = 4.99  # CODE SMELL: Magic number
        else:
            shipping_cost = 0
            
        if customer_type == 'premium':
            shipping_cost *= 0.5  # CODE SMELL: Magic number
            
        return shipping_cost
    
    def verify_large_transaction(self, customer_id, amount):
        """
        CODE SMELL: Feature Envy - This method uses customer data more than its own class data
        """
        customer = None
        for c in self.customers:
            if c.id == customer_id:
                customer = c
                break
                
        if not customer:
            return False
            
        # CODE SMELL: Feature Envy - Using customer data extensively
        if customer.credit_score < 600:  # CODE SMELL: Magic number
            return False
            
        if customer.account_age_days < 30:  # CODE SMELL: Magic number
            return False
            
        if amount > customer.credit_limit:
            return False
            
        # CODE SMELL: Feature Envy - More customer data usage
        recent_orders = 0
        for sale in self.sales:
            if sale.customer_id == customer_id:
                days_ago = (datetime.now() - sale.order_date).days
                if days_ago <= 7:  # CODE SMELL: Magic number
                    recent_orders += 1
                    
        if recent_orders > 3:  # CODE SMELL: Magic number
            return False
            
        return True
    
    def generate_customer_report_with_detailed_analytics(self, customer_id):
        """
        CODE SMELL: Feature Envy - Another method that primarily works with customer data
        """
        customer = None
        for c in self.customers:
            if c.id == customer_id:
                customer = c
                break
                
        if not customer:
            return None
            
        # CODE SMELL: Feature Envy - Extensive use of customer data
        report = {
            'customer_name': customer.name,
            'email': customer.email,
            'membership_level': customer.membership_level,
            'total_spent': customer.total_spent,
            'order_count': customer.order_count,
            'average_order_value': customer.total_spent / max(customer.order_count, 1),
            'account_age': customer.account_age_days,
            'credit_score': customer.credit_score,
            'preferred_categories': customer.preferred_categories
        }
        
        # CODE SMELL: Feature Envy - Calculate customer-specific metrics
        customer_orders = [s for s in self.sales if s.customer_id == customer_id]
        
        if customer_orders:
            report['last_order_date'] = max(order.order_date for order in customer_orders)
            report['first_order_date'] = min(order.order_date for order in customer_orders)
            
            # CODE SMELL: Feature Envy - More customer data manipulation
            total_books_bought = sum(
                sum(item['quantity'] for item in order.items) 
                for order in customer_orders
            )
            report['total_books_purchased'] = total_books_bought
            
        return report
    
    def add_customer(self, name, email, phone, address, membership_level='basic'):
        """
        CODE SMELL: Large Parameter List - This method takes 5 parameters, which is excessive.
        CODE SMELL: Magic Numbers - Random ranges without explanation
        """
        customer = Customer(name, email, phone, address, membership_level)
        customer.id = len(self.customers) + 1
        self.customers.append(customer)
        return customer.id

def main():
    """
    Main function demonstrating the smelly bookstore system
    """
    store = BookstoreManager()
    
    # Add some books with magic numbers
    store.add_book_to_inventory(
        "Python Programming", "John Doe", 29.99, 50, 
        "978-1234567890", "programming", "Tech Books", 2023
    )
    
    store.add_book_to_inventory(
        "Data Structures", "Jane Smith", 45.99, 30,
        "978-0987654321", "textbook", "Academic Press", 2022
    )
    
    # Add customers
    customer1_id = store.add_customer(
        "Alice Johnson", "alice@email.com", "555-0123", 
        "123 Main St", "premium"
    )
    
    customer2_id = store.add_customer(
        "Bob Wilson", "bob@email.com", "555-0456",
        "456 Oak Ave", "basic"
    )
    
    # Process orders with magic numbers and complex parameters
    order_id = store.process_customer_order_with_complex_calculations_and_validations_and_inventory_updates(
        customer1_id, [1, 2], [2, 1], "credit",
        "123 Main St", "123 Main St", "Leave at door", "SAVE10"
    )
    
    if order_id:
        print(f"Order {order_id} processed successfully")
        
        # Generate report using customer data extensively
        report = store.generate_customer_report_with_detailed_analytics(customer1_id)
        if report:
            print(f"Customer report generated for {report['customer_name']}")
    
    print(f"Total books in inventory: {len(store.books)}")
    print(f"Total customers: {len(store.customers)}")
    print(f"Total revenue: ${store.total_revenue:.2f}")

if __name__ == "__main__":
    main()
