"""
Simple Flask backend server to integrate with the Next.js frontend.
This provides the API endpoint that the web interface calls.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

from detector.smell_detector import CodeSmellDetector
from detector.config_manager import ConfigManager
from detector.report_generator import ReportGenerator

app = Flask(__name__)
CORS(app)  # Enable CORS for Next.js frontend

@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    """Analyze Python code for smells."""
    try:
        data = request.get_json()
        
        source_code = data.get('source_code', '')
        file_name = data.get('file_name', 'uploaded_file.py')
        frontend_config = data.get('config', {})
        
        if not source_code.strip():
            return jsonify({'error': 'No source code provided'}), 400
        
        # Convert frontend config to backend format
        config_manager = ConfigManager()
        
        # Update enabled smells
        if 'smells' in frontend_config:
            for smell, enabled in frontend_config['smells'].items():
                config_manager.config['smells'][smell] = enabled
        
        # Update thresholds
        if 'thresholds' in frontend_config:
            thresholds = frontend_config['thresholds']
            if 'longMethodSloc' in thresholds:
                config_manager.config['long_method']['sloc'] = thresholds['longMethodSloc']
            if 'longMethodCyclomatic' in thresholds:
                config_manager.config['long_method']['cyclomatic'] = thresholds['longMethodCyclomatic']
            if 'godClassMethods' in thresholds:
                config_manager.config['god_class']['max_methods'] = thresholds['godClassMethods']
            if 'godClassFields' in thresholds:
                config_manager.config['god_class']['max_fields'] = thresholds['godClassFields']
            if 'largeParameterList' in thresholds:
                config_manager.config['large_parameter_list']['params'] = thresholds['largeParameterList']
            if 'magicNumberOccurrences' in thresholds:
                config_manager.config['magic_numbers']['min_occurrences'] = thresholds['magicNumberOccurrences']
        
        # Get enabled smells
        enabled_smells = config_manager.get_enabled_smells()
        
        # Initialize detector and analyze
        detector = CodeSmellDetector(config_manager.to_dict())
        results = detector.detect_smells(file_name, source_code, enabled_smells)
        
        # Generate report
        report_generator = ReportGenerator(config_manager.to_dict())
        report = report_generator.generate_report(results, file_name, enabled_smells)
        
        return jsonify(report)
    
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/config/default', methods=['GET'])
def get_default_config():
    """Get default configuration."""
    config_manager = ConfigManager()
    return jsonify(config_manager.to_dict())

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'version': '1.0.0'})

if __name__ == '__main__':
    print("Starting Code Smell Detector Backend Server...")
    print("Frontend should be available at: http://localhost:3000")
    print("Backend API available at: http://localhost:5000")
    print("Use Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
