"""
Unit tests for the code smell detector engine.
"""

import unittest
import ast
from backend.detector.smell_detector import (
    CodeSmellDetector, LongMethodDetector, GodClassDetector,
    DuplicatedCodeDetector, LargeParameterListDetector,
    MagicNumbersDetector, FeatureEnvyDetector
)
from backend.detector.config_manager import ConfigManager

class TestLongMethodDetector(unittest.TestCase):
    """Test the Long Method detector."""
    
    def setUp(self):
        self.detector = LongMethodDetector({'sloc': 10, 'cyclomatic': 5})
    
    def test_detect_long_method_by_sloc(self):
        """Test detection of methods that are too long by line count."""
        source_code = '''
def long_method():
    # This method has many lines
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    f = 9
    g = 10
    h = 11
    return x + y + z + a + b + c + d + e + f + g + h
'''
        tree = ast.parse(source_code)
        results = self.detector.detect('test.py', source_code, tree)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].smell_type, 'LongMethod')
        self.assertEqual(results[0].details['method_name'], 'long_method')
    
    def test_detect_complex_method(self):
        """Test detection of methods with high cyclomatic complexity."""
        source_code = '''
def complex_method(x):
    if x > 0:
        if x > 10:
            if x > 20:
                if x > 30:
                    if x > 40:
                        return "very high"
                    return "high"
                return "medium high"
            return "medium"
        return "low"
    return "negative"
'''
        tree = ast.parse(source_code)
        results = self.detector.detect('test.py', source_code, tree)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].smell_type, 'LongMethod')
        self.assertGreater(results[0].details['cyclomatic_complexity'], 5)
    
    def test_normal_method_not_detected(self):
        """Test that normal methods are not flagged."""
        source_code = '''
def normal_method():
    x = 1
    y = 2
    return x + y
'''
        tree = ast.parse(source_code)
        results = self.detector.detect('test.py', source_code, tree)
        
        self.assertEqual(len(results), 0)

class TestGodClassDetector(unittest.TestCase):
    """Test the God Class detector."""
    
    def setUp(self):
        self.detector = GodClassDetector({
            'atfd_few': 1,
            'wmc_very_high': 1,
            'tcc_one_third': 1.1
        })
    
    def test_detect_god_class_by_methods(self):
        """Test detection of classes with too many methods."""
        source_code = '''
class GodClass:
    def method1(self, other):
        # High complexity and foreign access
        if other.field1 > 0:
            if other.field2 > 0:
                if other.field3 > 0:
                    if other.field4 > 0:
                        if other.field5 > 0:
                            if other.field6 > 0:
                                if other.field7 > 0:
                                    if other.field8 > 0:
                                        if other.field9 > 0:
                                            if other.field10 > 0:
                                                return other.field11
        return other.field12
    
    def method2(self, other):
        return other.field13 + other.field14
    
    def method3(self, other):
        return other.field15 * other.field16
'''
        tree = ast.parse(source_code)
        results = self.detector.detect('test.py', source_code, tree)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].smell_type, 'GodClass')
        self.assertEqual(results[0].details['class_name'], 'GodClass')
    
    def test_detect_god_class_by_fields(self):
        """Test detection of classes with too many fields."""
        source_code = '''
class GodClass:
    def __init__(self, other):
        self.field1 = 1
        self.field2 = 2
        self.field3 = 3
        self.field4 = 4
        self.field5 = 5
        self.field6 = 6
        self.field7 = 7
        # High complexity method with foreign access
        if other.field1 > 0:
            if other.field2 > 0:
                if other.field3 > 0:
                    if other.field4 > 0:
                        if other.field5 > 0:
                            if other.field6 > 0:
                                if other.field7 > 0:
                                    if other.field8 > 0:
                                        if other.field9 > 0:
                                            if other.field10 > 0:
                                                return other.field11
        return other.field12
'''
        tree = ast.parse(source_code)
        results = self.detector.detect('test.py', source_code, tree)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].smell_type, 'GodClass')
    
    def test_normal_class_not_detected(self):
        """Test that normal classes are not flagged."""
        source_code = '''
class NormalClass:
    def __init__(self):
        self.field1 = 1
        self.field2 = 2
    
    def method1(self): pass
    def method2(self): pass
'''
        tree = ast.parse(source_code)
        results = self.detector.detect('test.py', source_code, tree)
        
        self.assertEqual(len(results), 0)

class TestLargeParameterListDetector(unittest.TestCase):
    """Test the Large Parameter List detector."""
    
    def setUp(self):
        self.detector = LargeParameterListDetector({'params': 4})
    
    def test_detect_large_parameter_list(self):
        """Test detection of methods with too many parameters."""
        source_code = '''
def method_with_many_params(self, a, b, c, d, e, f):
    return a + b + c + d + e + f
'''
        tree = ast.parse(source_code)
        results = self.detector.detect('test.py', source_code, tree)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].smell_type, 'LargeParameterList')
        self.assertEqual(results[0].details['method_name'], 'method_with_many_params')
        self.assertGreater(results[0].details['parameter_count'], 4)
    
    def test_normal_parameter_list_not_detected(self):
        """Test that methods with normal parameter counts are not flagged."""
        source_code = '''
def normal_method(self, a, b):
    return a + b
'''
        tree = ast.parse(source_code)
        results = self.detector.detect('test.py', source_code, tree)
        
        self.assertEqual(len(results), 0)

class TestMagicNumbersDetector(unittest.TestCase):
    """Test the Magic Numbers detector."""
    
    def setUp(self):
        self.detector = MagicNumbersDetector({
            'min_occurrences': 2,
            'whitelist': [0, 1, -1]
        })
    
    def test_detect_magic_numbers(self):
        """Test detection of repeated magic numbers."""
        source_code = '''
def calculate():
    x = 42
    y = 42
    z = 42
    return x + y + z
'''
        tree = ast.parse(source_code)
        results = self.detector.detect('test.py', source_code, tree)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].smell_type, 'MagicNumbers')
        self.assertEqual(results[0].details['number'], 42)
        self.assertEqual(results[0].details['occurrences'], 3)
    
    def test_whitelisted_numbers_not_detected(self):
        """Test that whitelisted numbers are not flagged."""
        source_code = '''
def calculate():
    x = 0
    y = 1
    z = -1
    return x + y + z
'''
        tree = ast.parse(source_code)
        results = self.detector.detect('test.py', source_code, tree)
        
        self.assertEqual(len(results), 0)

class TestFeatureEnvyDetector(unittest.TestCase):
    """Test the Feature Envy detector."""
    
    def setUp(self):
        self.detector = FeatureEnvyDetector({
            'min_sloc': 5,
            'atfd_threshold': 2,
            'laa_threshold': 0.5,
            'fdp_threshold': 1
        })
    
    def test_detect_feature_envy(self):
        """Test detection of methods that access other objects more than self."""
        source_code = '''
class MyClass:
    def envious_method(self, other):
        # This method uses 'other' more than 'self'
        result = other.field1
        result += other.field2
        result += other.field3
        result += other.field4
        result += self.field1  # Only one self access
        return result
'''
        tree = ast.parse(source_code)
        results = self.detector.detect('test.py', source_code, tree)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].smell_type, 'FeatureEnvy')
        self.assertEqual(results[0].details['method_name'], 'envious_method')
    
    def test_normal_method_not_detected(self):
        """Test that methods with normal access patterns are not flagged."""
        source_code = '''
class MyClass:
    def normal_method(self, other):
        result = self.field1
        result += self.field2
        result += other.field1
        return result
'''
        tree = ast.parse(source_code)
        results = self.detector.detect('test.py', source_code, tree)
        
        self.assertEqual(len(results), 0)

class TestCodeSmellDetector(unittest.TestCase):
    """Test the main CodeSmellDetector class."""
    
    def setUp(self):
        config = ConfigManager().to_dict()
        self.detector = CodeSmellDetector(config)
    
    def test_detect_multiple_smells(self):
        """Test detection of multiple different smells in one file."""
        source_code = '''
class BigClass:
    def __init__(self):
        self.field1 = 42
        self.field2 = 42
        self.field3 = 42
    
    def long_method_with_many_params(self, a, b, c, d, e, f, g, h):
        # This method is long and has many parameters
        x = 42  # Magic number
        y = 42  # Magic number again
        z = 42  # Magic number again
        if a > 0:
            if b > 0:
                if c > 0:
                    if d > 0:
                        if e > 0:
                            return x + y + z
        return 0
    
    def another_long_method(self):
        # Another long method
        line1 = 1
        line2 = 2
        line3 = 3
        line4 = 4
        line5 = 5
        line6 = 6
        line7 = 7
        line8 = 8
        line9 = 9
        line10 = 10
        return sum([line1, line2, line3, line4, line5, line6, line7, line8, line9, line10])
'''
        results = self.detector.detect_smells('test.py', source_code)
        
        # Should detect multiple types of smells
        smell_types = {result.smell_type for result in results}
        self.assertGreater(len(smell_types), 1)
    
    def test_syntax_error_handling(self):
        """Test handling of files with syntax errors."""
        source_code = '''
def broken_function(
    # Missing closing parenthesis
    return "broken"
'''
        results = self.detector.detect_smells('test.py', source_code)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].smell_type, 'SyntaxError')

if __name__ == '__main__':
    unittest.main()
