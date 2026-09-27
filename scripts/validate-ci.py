#!/usr/bin/env python3
"""
Validation script for Bollyarr CI/CD setup.
Run this script to check if your development environment is properly configured.
"""

import subprocess
import sys
import importlib.util
from pathlib import Path
from typing import List, Tuple, Optional

def run_command(cmd: str, cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd.split(),
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)

def check_python_version() -> bool:
    """Check if Python version is supported."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (supported)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires Python 3.10+)")
        return False

def check_dependencies() -> bool:
    """Check if required development dependencies are installed."""
    required_packages = [
        'pytest',
        'black',
        'flake8',
        'mypy',
        'isort',
        'bandit',
        'safety'
    ]
    
    missing = []
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages installed")
        return True

def check_code_formatting() -> bool:
    """Check code formatting with Black."""
    print("\n🔍 Checking code formatting...")
    code, stdout, stderr = run_command("black --check --diff src/ tests/")
    
    if code == 0:
        print("✅ Code formatting is correct")
        return True
    else:
        print("❌ Code formatting issues found:")
        print(stderr)
        print("   Run: black src/ tests/")
        return False

def check_linting() -> bool:
    """Check code with Flake8."""
    print("\n🔍 Running Flake8 linting...")
    code, stdout, stderr = run_command("flake8 src/ tests/")
    
    if code == 0:
        print("✅ No linting issues found")
        return True
    else:
        print("❌ Linting issues found:")
        print(stdout)
        return False

def check_type_checking() -> bool:
    """Check types with MyPy."""
    print("\n🔍 Running type checking...")
    code, stdout, stderr = run_command("mypy src/ --ignore-missing-imports --no-strict-optional")
    
    if code == 0:
        print("✅ No type checking issues found")
        return True
    else:
        print("❌ Type checking issues found:")
        print(stdout)
        return False

def check_import_sorting() -> bool:
    """Check import sorting with isort."""
    print("\n🔍 Checking import sorting...")
    code, stdout, stderr = run_command("isort --check-only --diff src/ tests/")
    
    if code == 0:
        print("✅ Import sorting is correct")
        return True
    else:
        print("❌ Import sorting issues found:")
        print(stdout)
        print("   Run: isort src/ tests/")
        return False

def check_security() -> bool:
    """Check security with Bandit."""
    print("\n🔍 Running security scan...")
    code, stdout, stderr = run_command("bandit -r src/ --severity-level medium")
    
    if code == 0:
        print("✅ No security issues found")
        return True
    else:
        print("❌ Security issues found:")
        print(stdout)
        return False

def check_tests() -> bool:
    """Run unit tests."""
    print("\n🔍 Running tests...")
    code, stdout, stderr = run_command("pytest tests/ -v")
    
    if code == 0:
        print("✅ All tests passed")
        return True
    else:
        print("❌ Tests failed:")
        print(stdout)
        print(stderr)
        return False

def check_docker() -> bool:
    """Check if Docker is available and can build the image."""
    print("\n🔍 Checking Docker setup...")
    
    # Check if Docker is installed
    code, stdout, stderr = run_command("docker --version")
    if code != 0:
        print("❌ Docker is not installed or not accessible")
        return False
    
    print(f"✅ Docker available: {stdout.strip()}")
    
    # Try to build the Docker image (but don't push)
    print("🔍 Testing Docker build...")
    code, stdout, stderr = run_command("docker build -t bollyarr:test .")
    
    if code == 0:
        print("✅ Docker build successful")
        
        # Test if the container starts
        print("🔍 Testing container startup...")
        code, stdout, stderr = run_command("docker run --rm -d --name bollyarr-validation-test -p 8889:8888 bollyarr:test")
        
        if code == 0:
            # Wait a moment and check if container is healthy
            import time
            time.sleep(5)
            
            health_code, health_stdout, health_stderr = run_command("curl -f http://localhost:8889/api/health")
            
            # Clean up container
            subprocess.run(["docker", "stop", "bollyarr-validation-test"], capture_output=True)
            
            if health_code == 0:
                print("✅ Container starts and responds to health checks")
                return True
            else:
                print("❌ Container starts but health check fails")
                return False
        else:
            print("❌ Container failed to start")
            print(stderr)
            return False
    else:
        print("❌ Docker build failed:")
        print(stderr)
        return False

def check_git_setup() -> bool:
    """Check Git configuration."""
    print("\n🔍 Checking Git setup...")
    
    # Check if we're in a git repo
    code, stdout, stderr = run_command("git status")
    if code != 0:
        print("❌ Not in a Git repository")
        return False
    
    # Check if GitHub workflows exist
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print("❌ GitHub workflows directory not found")
        return False
    
    required_workflows = ["ci.yml", "cd.yml"]
    missing_workflows = []
    
    for workflow in required_workflows:
        if not (workflows_dir / workflow).exists():
            missing_workflows.append(workflow)
    
    if missing_workflows:
        print(f"❌ Missing workflows: {', '.join(missing_workflows)}")
        return False
    
    print("✅ Git repository and GitHub workflows configured")
    return True

def main():
    """Run all validation checks."""
    print("🚀 Bollyarr CI/CD Validation")
    print("=" * 40)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Code Formatting", check_code_formatting),
        ("Linting", check_linting),
        ("Type Checking", check_type_checking),
        ("Import Sorting", check_import_sorting),
        ("Security Scan", check_security),
        ("Unit Tests", check_tests),
        ("Git Setup", check_git_setup),
        ("Docker Build", check_docker),
    ]
    
    passed = 0
    failed = 0
    
    for name, check_func in checks:
        try:
            if check_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {name} check failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All checks passed! Your CI/CD setup is ready.")
        sys.exit(0)
    else:
        print("⚠️  Some checks failed. Please address the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()