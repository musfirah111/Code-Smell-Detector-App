"""
Unit tests for the CLI interface.
"""

import unittest
from unittest.mock import patch, mock_open
import tempfile
import os
from pathlib import Path
from backend.cli.cli import parse_arguments, validate_files, parse_smell_list

class TestCLI(unittest.TestCase):
    """Test the CLI functionality."""
    
    def test_parse_arguments_scan(self):
        """Test parsing scan command arguments."""
        with patch('sys.argv', ['cli.py', 'scan', 'test.py', '--format', 'table']):
            args = parse_arguments()
            
            self.assertEqual(args.command, 'scan')
            self.assertEqual(args.files, ['test.py'])
            self.assertEqual(args.format, 'table')
    
    def test_parse_arguments_config_generate(self):
        """Test parsing config generate command."""
        with patch('sys.argv', ['cli.py', 'config', 'generate', '--output', 'my_config.yaml']):
            args = parse_arguments()
            
            self.assertEqual(args.command, 'config')
            self.assertEqual(args.config_action, 'generate')
            self.assertEqual(args.output, 'my_config.yaml')
    
    def test_validate_files_success(self):
        """Test successful file validation."""
        # Create temporary Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('print("hello")')
            temp_path = f.name
        
        try:
            validated = validate_files([temp_path])
            self.assertEqual(len(validated), 1)
            self.assertEqual(str(validated[0]), temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_validate_files_nonexistent(self):
        """Test validation of non-existent files."""
        with self.assertRaises(SystemExit):
            validate_files(['nonexistent_file.py'])
    
    def test_parse_smell_list_valid(self):
        """Test parsing valid smell list."""
        smells = parse_smell_list('LongMethod,GodClass,FeatureEnvy')
        expected = {'LongMethod', 'GodClass', 'FeatureEnvy'}
        self.assertEqual(smells, expected)
    
    def test_parse_smell_list_invalid(self):
        """Test parsing invalid smell list."""
        with self.assertRaises(SystemExit):
            parse_smell_list('InvalidSmell,LongMethod')
    
    def test_parse_smell_list_empty(self):
        """Test parsing empty smell list."""
        smells = parse_smell_list('')
        self.assertEqual(smells, set())

if __name__ == '__main__':
    unittest.main()
