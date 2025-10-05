"""
Configuration management for the code smell detector.
"""
import yaml
import json
from typing import Dict, Any, Set, Optional
from pathlib import Path

class ConfigManager:
    """Manages configuration for code smell detection."""
    
    DEFAULT_CONFIG = {
        'smells': {
            'LongMethod': True,
            'GodClass': True,
            'DuplicatedCode': True,
            'LargeParameterList': True,
            'MagicNumbers': True,
            'FeatureEnvy': True
        },
        'long_method': {
            'sloc': 20,
            'cyclomatic': 12
        },
        'god_class': {
            'atfd_few': 2,
            'wmc_very_high': 10,
            'tcc_one_third': 0.6
        },
        'large_parameter_list': {
            'params': 5
        },
        'duplicated_code': {
            'min_block_lines': 3
        },
        'magic_numbers': {
            'min_occurrences': 3,
            'whitelist': [0, 1, -1]
        },
        'feature_envy': {
            'min_sloc': 10,
            'atfd_threshold': 5,
            'laa_threshold': 0.33,
            'fdp_threshold': 2
        },
        'report': {
            'format': 'json',
            'include_metrics': True,
            'show_active_smells': True
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_path and Path(config_path).exists():
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                self._merge_config(self.config, user_config)
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
            print("Using default configuration.")
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Recursively merge configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get_enabled_smells(self, only: Optional[Set[str]] = None, exclude: Optional[Set[str]] = None) -> Set[str]:
        """Get the set of enabled smells based on config and CLI overrides."""
        # Start with config-enabled smells
        enabled = {smell for smell, enabled in self.config['smells'].items() if enabled}
        
        # Apply CLI overrides
        if only:
            enabled = enabled.intersection(only)
        
        if exclude:
            enabled = enabled - exclude
        
        return enabled
    
    def get_smell_config(self, smell_name: str) -> Dict[str, Any]:
        """Get configuration for a specific smell detector."""
        smell_key = smell_name.lower().replace('class', '_class')
        return self.config.get(smell_key, {})
    
    def save_config(self, output_path: str) -> None:
        """Save current configuration to YAML file."""
        with open(output_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, indent=2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self.config.copy()
