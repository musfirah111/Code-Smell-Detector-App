"""
Report generation for code smell detection results.
"""

import json
from typing import List, Dict, Any, Set
from datetime import datetime
from backend.detector.smell_detector import SmellResult

class ReportGenerator:
    """Generates reports from code smell detection results."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('report', {})
    
    def generate_report(self, results: List[SmellResult], file_path: str, active_smells: Set[str]) -> Dict[str, Any]:
        """Generate a comprehensive report from detection results."""
        
        # Group results by smell type
        smells_by_type = {}
        for result in results:
            if result.smell_type not in smells_by_type:
                smells_by_type[result.smell_type] = []
            smells_by_type[result.smell_type].append(result)
        
        # Calculate metrics
        total_smells = len(results)
        severity_counts = {'high': 0, 'medium': 0, 'low': 0, 'error': 0}
        
        for result in results:
            severity_counts[result.severity] += 1
        
        # Build report
        report = {
            'metadata': {
                'file_path': file_path,
                'scan_timestamp': datetime.now().isoformat(),
                'active_smells': list(active_smells),
                'detector_version': '1.0.0'
            },
            'summary': {
                'total_smells_detected': total_smells,
                'severity_breakdown': severity_counts,
                'smells_by_type': {smell_type: len(smell_list) for smell_type, smell_list in smells_by_type.items()}
            },
            'details': []
        }
        
        # Add detailed results
        for result in results:
            detail = {
                'smell_type': result.smell_type,
                'severity': result.severity,
                'message': result.message,
                'location': {
                    'file': result.file_path,
                    'line_start': result.line_start,
                    'line_end': result.line_end
                },
                'details': result.details
            }
            report['details'].append(detail)
        
        return report
    
    def format_report(self, report: Dict[str, Any], format_type: str = 'json') -> str:
        """Format report in the specified format."""
        if format_type.lower() == 'json':
            return json.dumps(report, indent=2, default=str)
        elif format_type.lower() == 'table':
            return self._format_as_table(report)
        else:
            return json.dumps(report, indent=2, default=str)
    
    def _format_as_table(self, report: Dict[str, Any]) -> str:
        """Format report as a readable table."""
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("CODE SMELL DETECTION REPORT")
        lines.append("=" * 80)
        lines.append(f"File: {report['metadata']['file_path']}")
        lines.append(f"Scan Time: {report['metadata']['scan_timestamp']}")
        lines.append(f"Active Detectors: {', '.join(report['metadata']['active_smells'])}")
        lines.append("")
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Total Smells: {report['summary']['total_smells_detected']}")
        
        severity = report['summary']['severity_breakdown']
        lines.append(f"High: {severity['high']}, Medium: {severity['medium']}, Low: {severity['low']}")
        lines.append("")
        
        # By type
        lines.append("SMELLS BY TYPE")
        lines.append("-" * 40)
        for smell_type, count in report['summary']['smells_by_type'].items():
            lines.append(f"{smell_type}: {count}")
        lines.append("")
        
        # Details
        if report['details']:
            lines.append("DETAILED RESULTS")
            lines.append("-" * 40)
            
            for i, detail in enumerate(report['details'], 1):
                lines.append(f"{i}. {detail['smell_type']} ({detail['severity'].upper()})")
                lines.append(f"   Location: Lines {detail['location']['line_start']}-{detail['location']['line_end']}")
                lines.append(f"   Message: {detail['message']}")
                lines.append("")
        
        lines.append("=" * 80)
        return "\n".join(lines)
