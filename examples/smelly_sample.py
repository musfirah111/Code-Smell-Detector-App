"""
Small, intentionally smelly Python code for testing the detector.
Smells present:
- DuplicatedCode: two near-identical functions (>=5 lines each)
- LargeParameterList: function with many parameters
- MagicNumbers: repeated constants (>=3 occurrences, not whitelisted)
- FeatureEnvy: method accessing other object far more than self
"""

# --- DuplicatedCode (two similar blocks) ---
def compute_average_a(values):
    total = 0
    count = 0
    for v in values:
        if v is not None:
            total += v
            count += 1
    if count == 0:
        return 0
    return total / count


def compute_average_b(items):
    total = 0
    count = 0
    for v in items:
        if v is not None:
            total += v
            count += 1
    if count == 0:
        return 0
    return total / count


# --- LargeParameterList ---
def configure_system(a, b, c, d, e, f, g):  # 7 params (> default 6)
    return (a, b, c, d, e, f, g)


# --- MagicNumbers (>=3 occurrences, not in whitelist {0,1,-1}) ---
def apply_discounts(prices):
    result = []
    for p in prices:
        # 0.9 used multiple times; 100 used multiple times
        if p > 100:
            result.append(p * 0.9)
        elif p == 100:
            result.append(100 * 0.9)
        else:
            result.append(p + 100)
    return result


# --- FeatureEnvy ---
class Wallet:
    def __init__(self, balance):
        self.balance = balance

    def analyze_other(self, other):
        # Ensure enough SLOC and at least one self access
        self_is_positive = self.balance >= 0
        foreign_sum = 0
        # Access attributes on "other" many times (foreign accesses >= 3)
        foreign_sum += other.balance
        if hasattr(other, "pending"):
            foreign_sum += other.pending
        if hasattr(other, "credit_limit"):
            foreign_sum += other.credit_limit
        if hasattr(other, "rewards"):
            foreign_sum += other.rewards
        # Some extra lines to meet min_sloc
        note = "ok" if self_is_positive else "risk"
        threshold = 100
        if foreign_sum > threshold:
            note = "high"
        return foreign_sum, note


class Account:
    def __init__(self, balance, pending=0, credit_limit=0, rewards=0):
        self.balance = balance
        self.pending = pending
        self.credit_limit = credit_limit
        self.rewards = rewards


