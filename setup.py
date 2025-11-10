#!/usr/bin/env python3
"""
Setup script for Payment Refund Investigations POC
"""

import os
import sys
import subprocess
import platform


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"[INFO] {description}...")
    try:
        result = subprocess.run(command, shell=True,
                                check=True, capture_output=True, text=True)
        print(f"[SUCCESS] {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(
            f"[ERROR] Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    print(
        f"[SUCCESS] Python version {version.major}.{version.minor} is compatible")
    return True


def setup_virtual_environment():
    """Create and activate virtual environment"""
    if not os.path.exists('.venv'):
        if not run_command('python -m venv .venv', 'Creating virtual environment'):
            return False

    print(f"[INFO] To activate virtual environment:")
    print(f"   (Windows)      .venv\\Scripts\\activate")
    print(f"   (macOS/Linux)  source .venv/bin/activate")

    return True


def install_dependencies():
    """Install required dependencies (cross-platform)"""
    if platform.system().lower().startswith('win'):
        pip_path = os.path.join('.venv', 'Scripts', 'pip')
    else:
        pip_path = os.path.join('.venv', 'bin', 'pip')
    return run_command(f'"{pip_path}" install -r requirements.txt', 'Installing dependencies')


def create_directories():
    """Create necessary directories"""
    directories = ['runs']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"[INFO] Created directory: {directory}")
    return True


def check_sample_files():
    """Check if sample files exist"""
    sample_files = ['samples/pacs004.xml',
                    'samples/pacs008.xml', 'customers.csv']
    missing_files = []

    for file in sample_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"[WARNING] Missing sample files: {', '.join(missing_files)}")
        print(
            "   Please ensure all sample files are present before running the application")
        return False

    print("[SUCCESS] All sample files are present")
    return True


def main():
    """Main setup function"""
    print("Payment Refund Investigations POC Setup")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Setup virtual environment
    if not setup_virtual_environment():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        sys.exit(1)

    # Create directories
    if not create_directories():
        sys.exit(1)

    # Check sample files
    if not check_sample_files():
        print("[WARNING] Setup completed with warnings")
    else:
        print("[SUCCESS] Setup completed successfully")

    print("\nSetup Complete!")
    print("=" * 50)
    print("Next Steps:")
    print("1. Activate virtual environment:")
    print("   (Windows)      .venv\\Scripts\\activate")
    print("   (macOS/Linux)  source .venv/bin/activate")
    print("2. Start the application:")
    print("   (Windows)      start.bat  (or: python -m app.web)")
    print("   (macOS/Linux)  python -m app.web")
    print("3. Open browser to: http://localhost:5000")
    print("\nEnjoy exploring the enhanced refund processing workflow!")


if __name__ == "__main__":
    main()
