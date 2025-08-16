#!/usr/bin/env python3
"""
WSL Integration Test Script for HAL 9000 System Interface
Tests WSL functionality, environment, and Q CLI availability
"""

import subprocess
import sys
import os

def run_wsl_command_safe(command, timeout=10):
    """Run WSL command with proper encoding handling"""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        return result
    except UnicodeDecodeError:
        # Fallback to bytes mode and decode manually
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=False,
                timeout=timeout
            )
            # Try UTF-8 first, then fallback to latin-1
            try:
                stdout = result.stdout.decode('utf-8', errors='replace')
                stderr = result.stderr.decode('utf-8', errors='replace')
            except UnicodeDecodeError:
                stdout = result.stdout.decode('latin-1', errors='replace')
                stderr = result.stderr.decode('latin-1', errors='replace')
            
            # Create a mock result object
            class MockResult:
                def __init__(self, returncode, stdout, stderr):
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr
            
            return MockResult(result.returncode, stdout, stderr)
        except Exception as e:
            # Last resort - return error
            class ErrorResult:
                def __init__(self, error_msg):
                    self.returncode = 1
                    self.stdout = ""
                    self.stderr = f"Encoding error: {str(e)}"
            
            return ErrorResult(str(e))

def test_wsl_availability():
    """Test if WSL is available"""
    print("🔍 Testing WSL Availability...")
    try:
        result = run_wsl_command_safe(['wsl', '--status'], timeout=10)
        if result.returncode == 0:
            print("✅ WSL is available and running")
            print(f"   Status: {result.stdout.strip()}")
            return True
        else:
            print("❌ WSL status check failed")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        print("❌ WSL command not found - WSL not installed")
        return False
    except subprocess.TimeoutExpired:
        print("❌ WSL status check timed out")
        return False
    except Exception as e:
        print(f"❌ WSL test error: {e}")
        return False

def test_wsl_basic_commands():
    """Test basic WSL command execution"""
    print("\n🔍 Testing Basic WSL Commands...")
    
    tests = [
        ("Echo test", "echo 'Hello from WSL'"),
        ("Current directory", "pwd"),
        ("List files", "ls -la"),
        ("Environment", "env | head -5")
    ]
    
    for test_name, command in tests:
        try:
            result = run_wsl_command_safe(
                ['wsl', '--', 'bash', '-c', command],
                timeout=10
            )
            if result.returncode == 0:
                print(f"✅ {test_name}: OK")
                print(f"   Output: {result.stdout.strip()[:100]}...")
            else:
                print(f"❌ {test_name}: Failed")
                print(f"   Error: {result.stderr.strip()}")
        except Exception as e:
            print(f"❌ {test_name}: Exception - {e}")

def test_wsl_interactive_shell():
    """Test WSL interactive shell with profile loading"""
    print("\n🔍 Testing WSL Interactive Shell...")
    
    tests = [
        ("Login shell test", "bash -l -c 'echo $HOME'"),
        ("Profile loading", "bash -l -c 'echo $PATH | tr : \\\\n | head -5'"),
        ("SSH Agent", "bash -l -c 'echo SSH_AUTH_SOCK: $SSH_AUTH_SOCK'"),
        ("User info", "bash -l -c 'whoami && id'")
    ]
    
    for test_name, command in tests:
        try:
            result = run_wsl_command_safe(
                ['wsl', '--'] + command.split(),
                timeout=10
            )
            if result.returncode == 0:
                print(f"✅ {test_name}: OK")
                print(f"   Output: {result.stdout.strip()}")
            else:
                print(f"❌ {test_name}: Failed")
                print(f"   Error: {result.stderr.strip()}")
        except Exception as e:
            print(f"❌ {test_name}: Exception - {e}")

def test_q_cli_availability():
    """Test Q CLI availability in WSL"""
    print("\n🔍 Testing Q CLI in WSL...")
    
    # Test different Q CLI command variants
    q_commands = [
        ("q command", "bash -l -c 'which q'"),
        ("qchat command", "bash -l -c 'which qchat'"),
        ("amazon-q command", "bash -l -c 'which amazon-q'")
    ]
    
    found_q_cli = False
    working_command = None
    
    for test_name, command in q_commands:
        try:
            result = subprocess.run(
                ['wsl', '--'] + command.split(),
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print(f"✅ {test_name}: Found at {result.stdout.strip()}")
                if not found_q_cli:
                    found_q_cli = True
                    working_command = command.split()[-1].replace("'", "").replace("which ", "")
            else:
                print(f"❌ {test_name}: Not found")
        except Exception as e:
            print(f"❌ {test_name}: Exception - {e}")
    
    if found_q_cli and working_command:
        print(f"\n🔍 Testing {working_command} functionality...")
        
        # Test version
        try:
            result = subprocess.run(
                ['wsl', '--', 'bash', '-l', '-c', f'{working_command} --version'],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                print(f"✅ {working_command} version: {result.stdout.strip()}")
            else:
                print(f"❌ {working_command} version failed: {result.stderr.strip()}")
        except Exception as e:
            print(f"❌ {working_command} version: Exception - {e}")
        
        # Test help
        try:
            result = subprocess.run(
                ['wsl', '--', 'bash', '-l', '-c', f'{working_command} --help | head -3'],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                print(f"✅ {working_command} help: Available")
                print(f"   Sample: {result.stdout.strip()}")
            else:
                print(f"❌ {working_command} help failed")
        except Exception as e:
            print(f"❌ {working_command} help: Exception - {e}")
        
        # Test chat command (if it's qchat)
        if working_command == 'qchat':
            try:
                result = subprocess.run(
                    ['wsl', '--', 'bash', '-l', '-c', 'echo "test" | qchat chat --help | head -3'],
                    capture_output=True, text=True, timeout=15
                )
                if result.returncode == 0:
                    print("✅ qchat chat command: Available")
                else:
                    print("❌ qchat chat command: Issues detected")
                    print(f"   Error: {result.stderr.strip()}")
            except Exception as e:
                print(f"❌ qchat chat test: Exception - {e}")
    
    else:
        print("\n❌ No Q CLI variants found in WSL")
        print("💡 Install Amazon Q CLI with:")
        print("   curl -sSL https://d2eo22ngex1n9g.cloudfront.net/Documentation/SDK/amazon-q-developer-cli-install-linux.sh | bash")
        print("   source ~/.bashrc")

def test_file_operations():
    """Test file operations in WSL"""
    print("\n🔍 Testing WSL File Operations...")
    
    try:
        # Test file creation and deletion
        test_file = "/tmp/hal_wsl_test.txt"
        
        # Create file
        result = subprocess.run(
            ['wsl', '--', 'bash', '-l', '-c', f'echo "HAL WSL Test" > {test_file}'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            print("✅ File creation: OK")
            
            # Read file
            result = subprocess.run(
                ['wsl', '--', 'bash', '-l', '-c', f'cat {test_file}'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ File reading: OK - Content: {result.stdout.strip()}")
            else:
                print("❌ File reading: Failed")
            
            # Delete file
            subprocess.run(
                ['wsl', '--', 'bash', '-l', '-c', f'rm {test_file}'],
                capture_output=True, text=True, timeout=10
            )
            print("✅ File cleanup: OK")
            
        else:
            print("❌ File creation: Failed")
            print(f"   Error: {result.stderr.strip()}")
            
    except Exception as e:
        print(f"❌ File operations: Exception - {e}")

def test_tab_completion():
    """Test tab completion functionality"""
    print("\n🔍 Testing Tab Completion...")
    
    try:
        # Test compgen availability
        result = subprocess.run(
            ['wsl', '--', 'bash', '-l', '-c', 'compgen -f /usr/bin/ba | head -3'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Tab completion (compgen): OK")
            print(f"   Sample completions: {result.stdout.strip()}")
        else:
            print("❌ Tab completion: Failed")
            print(f"   Error: {result.stderr.strip()}")
            
    except Exception as e:
        print(f"❌ Tab completion: Exception - {e}")

def provide_recommendations():
    """Provide recommendations based on test results"""
    print("\n💡 Recommendations:")
    print("1. If WSL is not available:")
    print("   - Install WSL: wsl --install")
    print("   - Restart your computer")
    print("   - Install a Linux distribution from Microsoft Store")
    print()
    print("2. If Q CLI is not found:")
    print("   - Open WSL terminal")
    print("   - Run: curl -sSL https://d2eo22ngex1n9g.cloudfront.net/Documentation/SDK/amazon-q-developer-cli-install-linux.sh | bash")
    print("   - Run: source ~/.bashrc")
    print()
    print("3. If SSH agent is not working:")
    print("   - In WSL, add to ~/.bashrc:")
    print("     eval $(ssh-agent -s)")
    print("     ssh-add ~/.ssh/id_rsa  # or your key file")
    print()
    print("4. If PATH issues persist:")
    print("   - Check ~/.bashrc, ~/.bash_profile, ~/.profile")
    print("   - Ensure Q CLI installation added to PATH")
    print("   - Try: echo $PATH in WSL to verify")

def main():
    """Run all WSL tests"""
    print("HAL 9000 System Interface - WSL Integration Test")
    print("=" * 50)
    
    # Test WSL availability
    if not test_wsl_availability():
        print("\n❌ WSL is not available. Cannot proceed with further tests.")
        provide_recommendations()
        return 1
    
    # Run all tests
    test_wsl_basic_commands()
    test_wsl_interactive_shell()
    test_q_cli_availability()
    test_file_operations()
    test_tab_completion()
    
    # Provide recommendations
    provide_recommendations()
    
    print("\n✅ WSL Integration Test Complete!")
    print("If issues persist, check the recommendations above.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
