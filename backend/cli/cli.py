#!/usr/bin/env python3
"""
Command Line Interface for the Code Smell Detector
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Set, Optional, List

from backend.detector.smell_detector import CodeSmellDetector
from backend.detector.config_manager import ConfigManager
from backend.detector.report_generator import ReportGenerator

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Code Smell Detector - Analyze Python code for quality issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default scan using config.yaml
  smelldet scan my_app.py --config config.yaml --format json
  
  # Focus on specific smells
  smelldet scan my_app.py --only LongMethod,FeatureEnvy
  
  # Run all except specific smells
  smelldet scan my_app.py --exclude MagicNumbers --format table
  
  # Scan multiple files
  smelldet scan file1.py file2.py --format json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan Python files for code smells')
    scan_parser.add_argument('files', nargs='+', help='Python files to analyze')
    scan_parser.add_argument('--config', '-c', help='Configuration file path (YAML)')
    scan_parser.add_argument('--format', '-f', choices=['json', 'table'], default='json',
                           help='Output format (default: json)')
    scan_parser.add_argument('--output', '-o', help='Output file path (default: stdout)')
    scan_parser.add_argument('--only', help='Comma-separated list of smells to check only')
    scan_parser.add_argument('--exclude', help='Comma-separated list of smells to exclude')
    scan_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_subparsers = config_parser.add_subparsers(dest='config_action')
    
    # Generate default config
    generate_parser = config_subparsers.add_parser('generate', help='Generate default config file')
    generate_parser.add_argument('--output', '-o', default='config.yaml',
                               help='Output config file path (default: config.yaml)')
    
    # Show current config
    show_parser = config_subparsers.add_parser('show', help='Show current configuration')
    show_parser.add_argument('--config', '-c', help='Configuration file path')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show version information')
    
    return parser.parse_args()

def validate_files(file_paths: List[str]) -> List[Path]:
    """Validate that all provided files exist and are Python files."""
    validated_files = []
    
    for file_path in file_paths:
        path = Path(file_path)
        
        if not path.exists():
            print(f"Error: File '{file_path}' does not exist.", file=sys.stderr)
            sys.exit(1)
        
        if not path.is_file():
            print(f"Error: '{file_path}' is not a file.", file=sys.stderr)
            sys.exit(1)
        
        if not file_path.endswith('.py'):
            print(f"Warning: '{file_path}' is not a Python file.", file=sys.stderr)
        
        validated_files.append(path)
    
    return validated_files

def parse_smell_list(smell_string: str) -> Set[str]:
    """Parse comma-separated smell list."""
    if not smell_string:
        return set()
    
    valid_smells = {
        'LongMethod', 'GodClass', 'DuplicatedCode', 
        'LargeParameterList', 'MagicNumbers', 'FeatureEnvy'
    }
    
    smells = {smell.strip() for smell in smell_string.split(',')}
    
    # Validate smell names
    invalid_smells = smells - valid_smells
    if invalid_smells:
        print(f"Error: Invalid smell names: {', '.join(invalid_smells)}", file=sys.stderr)
        print(f"Valid smells: {', '.join(sorted(valid_smells))}", file=sys.stderr)
        sys.exit(1)
    
    return smells

def scan_files(args: argparse.Namespace) -> None:
    """Scan files for code smells."""
    # Validate files
    files = validate_files(args.files)
    
    # Load configuration
    config_manager = ConfigManager(args.config)
    
    # Parse CLI overrides
    only_smells = parse_smell_list(args.only) if args.only else None
    exclude_smells = parse_smell_list(args.exclude) if args.exclude else None
    
    # Get enabled smells
    enabled_smells = config_manager.get_enabled_smells(only_smells, exclude_smells)
    
    if not enabled_smells:
        print("Error: No smells enabled for detection.", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"Enabled detectors: {', '.join(sorted(enabled_smells))}", file=sys.stderr)
        print(f"Analyzing {len(files)} file(s)...", file=sys.stderr)
    
    # Initialize detector and report generator
    detector = CodeSmellDetector(config_manager.to_dict())
    report_generator = ReportGenerator(config_manager.to_dict())
    
    all_results = []
    
    # Process each file
    for file_path in files:
        if args.verbose:
            print(f"Scanning {file_path}...", file=sys.stderr)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Detect smells
            results = detector.detect_smells(str(file_path), source_code, enabled_smells)
            
            # Generate report for this file
            report = report_generator.generate_report(results, str(file_path), enabled_smells)
            all_results.append(report)
            
            if args.verbose:
                print(f"Found {len(results)} smell(s) in {file_path}", file=sys.stderr)
        
        except Exception as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)
            continue
    
    # Combine results if multiple files
    if len(all_results) == 1:
        final_report = all_results[0]
    else:
        # Combine multiple file reports
        final_report = combine_reports(all_results, enabled_smells)
    
    # Format and output report
    formatted_report = report_generator.format_report(final_report, args.format)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(formatted_report)
        if args.verbose:
            print(f"Report saved to {args.output}", file=sys.stderr)
    else:
        print(formatted_report)

def combine_reports(reports: List[dict], enabled_smells: Set[str]) -> dict:
    """Combine multiple file reports into a single report."""
    combined_details = []
    total_smells = 0
    severity_counts = {'high': 0, 'medium': 0, 'low': 0, 'error': 0}
    smells_by_type = {}
    
    for report in reports:
        combined_details.extend(report['details'])
        total_smells += report['summary']['total_smells_detected']
        
        # Combine severity counts
        for severity, count in report['summary']['severity_breakdown'].items():
            severity_counts[severity] += count
        
        # Combine smells by type
        for smell_type, count in report['summary']['smells_by_type'].items():
            smells_by_type[smell_type] = smells_by_type.get(smell_type, 0) + count
    
    return {
        'metadata': {
            'file_path': f"{len(reports)} files",
            'scan_timestamp': reports[0]['metadata']['scan_timestamp'],
            'active_smells': list(enabled_smells),
            'detector_version': '1.0.0'
        },
        'summary': {
            'total_smells_detected': total_smells,
            'severity_breakdown': severity_counts,
            'smells_by_type': smells_by_type
        },
        'details': combined_details
    }

def generate_config(args: argparse.Namespace) -> None:
    """Generate default configuration file."""
    config_manager = ConfigManager()
    config_manager.save_config(args.output)
    print(f"Default configuration saved to {args.output}")

def show_config(args: argparse.Namespace) -> None:
    """Show current configuration."""
    config_manager = ConfigManager(args.config)
    config_dict = config_manager.to_dict()
    
    print("Current Configuration:")
    print("=" * 50)
    print(json.dumps(config_dict, indent=2))

def show_version() -> None:
    """Show version information."""
    print("Code Smell Detector v1.0.0")
    print("Python code quality analysis tool")
    print("Detects: Long Method, God Class, Duplicated Code, Large Parameter List, Magic Numbers, Feature Envy")

def main() -> None:
    """Main CLI entry point."""
    args = parse_arguments()
    
    if not args.command:
        print("Error: No command specified. Use --help for usage information.", file=sys.stderr)
        sys.exit(1)
    
    try:
        if args.command == 'scan':
            scan_files(args)
        elif args.command == 'config':
            if args.config_action == 'generate':
                generate_config(args)
            elif args.config_action == 'show':
                show_config(args)
            else:
                print("Error: No config action specified.", file=sys.stderr)
                sys.exit(1)
        elif args.command == 'version':
            show_version()
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.command == 'scan' and hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
