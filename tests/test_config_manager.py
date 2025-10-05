"""
Unit tests for the configuration manager.
"""

import unittest
import tempfile
import os
from pathlib import Path
from backend.detector.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    """Test the ConfigManager class."""
    
    def test_default_config_loading(self):
        """Test loading default configuration."""
        config_manager = ConfigManager()
        config = config_manager.to_dict()
        
        # Check that all required sections exist
        self.assertIn('smells', config)
        self.assertIn('long_method', config)
        self.assertIn('god_class', config)
        self.assertIn('large_parameter_list', config)
        self.assertIn('duplicated_code', config)
        self.assertIn('magic_numbers', config)
        self.assertIn('feature_envy', config)
        self.assertIn('report', config)
    
    def test_yaml_config_loading(self):
        """Test loading configuration from YAML file."""
        # Create temporary config file
        config_content = '''
smells:
  LongMethod: false
  GodClass: true
  
long_method:
  sloc: 25
  cyclomatic: 10
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            temp_path = f.name
        
        try:
            config_manager = ConfigManager(temp_path)
            config = config_manager.to_dict()
            
            # Check that custom values were loaded
            self.assertFalse(config['smells']['LongMethod'])
            self.assertTrue(config['smells']['GodClass'])
            self.assertEqual(config['long_method']['sloc'], 25)
            self.assertEqual(config['long_method']['cyclomatic'], 10)
        finally:
            os.unlink(temp_path)
    
    def test_get_enabled_smells_default(self):
        """Test getting enabled smells with default config."""
        config_manager = ConfigManager()
        enabled = config_manager.get_enabled_smells()
        
        # All smells should be enabled by default
        expected_smells = {
            'LongMethod', 'GodClass', 'DuplicatedCode',
            'LargeParameterList', 'MagicNumbers', 'FeatureEnvy'
        }
        self.assertEqual(enabled, expected_smells)
    
    def test_get_enabled_smells_with_only(self):
        """Test getting enabled smells with 'only' filter."""
        config_manager = ConfigManager()
        only_smells = {'LongMethod', 'GodClass'}
        enabled = config_manager.get_enabled_smells(only=only_smells)
        
        self.assertEqual(enabled, only_smells)
    
    def test_get_enabled_smells_with_exclude(self):
        """Test getting enabled smells with 'exclude' filter."""
        config_manager = ConfigManager()
        exclude_smells = {'MagicNumbers', 'FeatureEnvy'}
        enabled = config_manager.get_enabled_smells(exclude=exclude_smells)
        
        expected_smells = {
            'LongMethod', 'GodClass', 'DuplicatedCode', 'LargeParameterList'
        }
        self.assertEqual(enabled, expected_smells)
    
    def test_get_smell_config(self):
        """Test getting configuration for specific smells."""
        config_manager = ConfigManager()
        
        long_method_config = config_manager.get_smell_config('LongMethod')
        self.assertIn('sloc', long_method_config)
        self.assertIn('cyclomatic', long_method_config)
        
        god_class_config = config_manager.get_smell_config('GodClass')
        self.assertIn('atfd_few', god_class_config)
        self.assertIn('wmc_very_high', god_class_config)
    
    def test_save_config(self):
        """Test saving configuration to file."""
        config_manager = ConfigManager()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name
        
        try:
            config_manager.save_config(temp_path)
            
            # Verify file was created and can be loaded
            self.assertTrue(Path(temp_path).exists())
            
            # Load the saved config and verify it matches
            new_config_manager = ConfigManager(temp_path)
            self.assertEqual(
                config_manager.to_dict(),
                new_config_manager.to_dict()
            )
        finally:
            if Path(temp_path).exists():
                os.unlink(temp_path)

if __name__ == '__main__':
    unittest.main()
