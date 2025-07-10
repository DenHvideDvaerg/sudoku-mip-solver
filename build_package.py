"""
Build script for the sudoku-mip-solver package.
This script builds the package for distribution.
"""

import os
import shutil
import subprocess
import sys

def clean_previous_builds():
    """Remove previous build artifacts."""
    print("Cleaning previous builds...")
    
    # Directories to clean
    build_dirs = ["build", "dist", "sudoku_mip_solver.egg-info"]
    
    for directory in build_dirs:
        if os.path.exists(directory):
            print(f"Removing {directory}")
            shutil.rmtree(directory)

def run_command(command):
    """Run a shell command and handle errors."""
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        return False

def build_package():
    """Build the package using setuptools."""
    print("\nBuilding package...")
    if not run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"]):
        return False
        
    if not run_command([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools", "wheel", "build"]):
        return False
        
    if not run_command([sys.executable, "-m", "build"]):
        return False
        
    print("\nBuild successful! Distribution files created in the 'dist' directory.")
    
    # List the created files
    print("\nGenerated distribution files:")
    dist_files = os.listdir("dist")
    for file in dist_files:
        file_path = os.path.join("dist", file)
        size = os.path.getsize(file_path) / 1024  # Convert to KB
        print(f"  - {file} ({size:.1f} KB)")
    
    return True

def validate_package():
    """Validate the built package using twine."""
    print("\nValidating package...")
    if not run_command([sys.executable, "-m", "pip", "install", "--upgrade", "twine"]):
        return False
        
    if not run_command([sys.executable, "-m", "twine", "check", "dist/*"]):
        return False
    
    print("\nPackage validation successful!")
    return True

def main():
    """Main entry point."""
    print("Sudoku MIP Solver - Build Script")
    print("=" * 40)
    
    clean_previous_builds()
    
    if build_package() and validate_package():
        print("\nPackage is ready for distribution!")
        print("\nTo upload to PyPI, run:")
        print("  python -m twine upload dist/*")
        print("\nTo install locally for testing, run:")
        print("  pip install --user dist/*.whl")
        return 0
    else:
        print("\nPackage build or validation failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())