#!/usr/bin/env python3
"""
Auto-detect and install missing dependencies for article-generator skill
"""
import subprocess
import sys
import os

def check_and_install_dependencies():
    """Check if required packages are installed, install if missing"""

    required_packages = {
        'google.genai': 'google-genai>=0.1.0',
        'PIL': 'Pillow>=10.0.0',
        'dotenv': 'python-dotenv>=1.0.0'
    }

    missing_packages = []

    print("🔍 Checking dependencies for article-generator skill...")

    # Check each required package
    for import_name, pip_name in required_packages.items():
        try:
            if import_name == 'google.genai':
                from google import genai
            elif import_name == 'PIL':
                import PIL
            elif import_name == 'dotenv':
                import dotenv
            print(f"  ✅ {pip_name.split('>=')[0]} is installed")
        except ImportError:
            print(f"  ❌ {pip_name.split('>=')[0]} is missing")
            missing_packages.append(pip_name)

    # Install missing packages
    if missing_packages:
        print(f"\n📦 Installing {len(missing_packages)} missing package(s)...")

        # Get the skill directory
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        requirements_file = os.path.join(skill_dir, 'requirements.txt')

        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-q',
                '-r', requirements_file
            ])
            print("✅ All dependencies installed successfully!\n")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            print(f"Please manually run: pip install -r {requirements_file}")
            return False
    else:
        print("\n✅ All dependencies are already installed!\n")
        return True

if __name__ == '__main__':
    success = check_and_install_dependencies()
    sys.exit(0 if success else 1)
