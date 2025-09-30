"""
Environment setup script for the Code Smell Detector.
Installs required dependencies and sets up the project.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"Error: {e.stderr}")
        return None

def install_python_dependencies():
    """Install required Python packages."""
    requirements = [
        "pyyaml>=6.0",
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0"
    ]
    
    print("Installing Python dependencies...")
    for package in requirements:
        run_command(f"pip install {package}", f"Installing {package}")

def setup_cli_executable():
    """Make the CLI script executable."""
    script_path = Path(__file__).parent.parent / "smelldet"
    
    if script_path.exists():
        os.chmod(script_path, 0o755)
        print("✓ Made CLI script executable")
    else:
        print("✗ CLI script not found")

def create_sample_files():
    """Create sample configuration and test files."""
    project_root = Path(__file__).parent.parent
    
    # Create examples directory if it doesn't exist
    examples_dir = project_root / "examples"
    examples_dir.mkdir(exist_ok=True)
    
    print("✓ Created examples directory")

def run_tests():
    """Run the test suite to verify installation."""
    print("Running tests to verify installation...")
    result = run_command("python -m pytest test_smelly_program.py -v", "Running unit tests")
    
    if result:
        print("✓ All tests passed - installation verified")
    else:
        print("⚠ Some tests failed - check the output above")

def main():
    """Main setup function."""
    print("=" * 60)
    print("Code Smell Detector - Environment Setup")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("✗ Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install dependencies
    install_python_dependencies()
    
    # Setup CLI
    setup_cli_executable()
    
    # Create sample files
    create_sample_files()
    
    # Run tests
    run_tests()
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("You can now use the Code Smell Detector:")
    print("1. CLI: ./smelldet scan your_file.py")
    print("2. Web: python scripts/run_backend_server.py (then visit localhost:3000)")
    print("3. Direct: python -c 'from cli import main; main()' scan your_file.py")
    print("\nFor help: ./smelldet --help")

if __name__ == "__main__":
    main()
