#!/usr/bin/env python3
"""
V2 Task Runner - Centralized Task Management
Single script to manage all v2 running tasks and services
"""

import os
import sys
import subprocess
import argparse
from typing import Dict, List, Any

# Add to path
sys.path.insert(0, os.path.abspath('.'))

def activate_venv():
    """Activate virtual environment"""
    venv_path = os.path.join(os.getcwd(), '.venv', 'bin', 'activate')
    return f"source {venv_path}"

def run_command(command: str, description: str) -> bool:
    """Run a command and return success status"""
    print(f"🚀 {description}")
    print(f"Command: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Success")
            if result.stdout:
                print(result.stdout)
        else:
            print("✅ Success (no output)")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_status():
    """Check current status of v2 system"""
    print("📊 V2 System Status Check")
    print("=" * 50)
    
    # Check virtual environment
    venv_exists = os.path.exists('.venv')
    print(f"Virtual Environment: {'✅' if venv_exists else '❌'} .venv/")
    
    # Check repositories
    brick_repo = os.path.exists('brick_repositories')
    schema_repo = os.path.exists('schema_repositories')
    print(f"Brick Repository: {'✅' if brick_repo else '❌'} brick_repositories/")
    print(f"Schema Repository: {'✅' if schema_repo else '❌'} schema_repositories/")
    
    # Check dependencies
    try:
        from schema_app_v2.core.brick_integration import BrickIntegration
        from schema_app_v2.core.schema_core import SchemaCore
        bi = BrickIntegration('brick_repositories')
        sc = SchemaCore('schema_repositories')
        bricks = bi.get_available_bricks()
        schemas = sc.get_all_schemas()
        print(f"Available Bricks: ✅ {len(bricks)} bricks")
        print(f"Available Schemas: ✅ {len(schemas)} schemas")
    except Exception as e:
        print(f"Dependencies Check: ❌ {e}")
    
    # Check running processes
    try:
        result = subprocess.run("ps aux | grep python | grep -v grep", 
                           shell=True, capture_output=True, text=True)
        processes = [line for line in result.stdout.split('\n') if 'python' in line]
        print(f"Running Python Processes: {len(processes)}")
        for proc in processes[:3]:  # Show first 3
            print(f"  - {proc.strip()}")
    except:
        print("Process Check: ❌ Failed")

def launch_interface(interface_type: str):
    """Launch specific interface"""
    activate_cmd = activate_venv()
    
    if interface_type == "qt" or interface_type == "pyqt6":
        command = f"{activate_cmd} && python3 run_schema_app_v2.py"
        description = "PyQt6 Desktop Interface"
    elif interface_type == "flask":
        command = f"{activate_cmd} && python3 -m schema_app_v2.interfaces.web.flask_app"
        description = "Flask Web Interface"
    elif interface_type == "dash":
        command = f"{activate_cmd} && python3 -m schema_app_v2.interfaces.web.dash_app"
        description = "DASH Interactive Web Interface"
    else:
        print(f"❌ Unknown interface: {interface_type}")
        print("Available: qt, flask, dash")
        return False
    
    return run_command(command, description)

def manage_processes(action: str):
    """Manage running processes"""
    if action == "stop":
        command = "pkill -f python"
        description = "Stop all Python processes"
    elif action == "status":
        command = "ps aux | grep python | grep -v grep"
        description = "Check running Python processes"
    elif action == "ports":
        command = "netstat -tlnp 2>/dev/null | grep -E ':(8050|5000)' || echo 'No web services running'"
        description = "Check web service ports"
    else:
        print(f"❌ Unknown action: {action}")
        print("Available: stop, status, ports")
        return False
    
    return run_command(command, description)

def run_tests():
    """Run v2 tests"""
    activate_cmd = activate_venv()
    command = f"{activate_cmd} && python3 -c "
    from schema_app_v2.core.brick_integration import BrickIntegration
    from schema_app_v2.core.schema_core import SchemaCore
    bi = BrickIntegration('brick_repositories')
    sc = SchemaCore('schema_repositories')
    print(f'Bricks: {len(bi.get_available_bricks())}')
    print(f'Schemas: {len(sc.get_all_schemas())}')
    ""
    description = "Run v2 system tests"
    return run_command(command, description)

def setup_environment():
    """Setup and verify environment"""
    commands = [
        ("echo 'Checking virtual environment...'", "Environment Check"),
        ("ls -la .venv/", "Venv Directory"),
        ("echo 'Checking dependencies...'", "Dependencies Check"),
        (f"{activate_venv()} && pip list", "Installed Packages"),
        ("echo 'Checking repositories...'", "Repository Check"),
        ("ls -la brick_repositories/", "Brick Repository"),
        ("ls -la schema_repositories/", "Schema Repository")
    ]
    
    for cmd, desc in commands:
        run_command(cmd, desc)

def main():
    """Main task runner"""
    parser = argparse.ArgumentParser(description="V2 Task Manager")
    parser.add_argument('command', choices=[
        'status', 'qt', 'pyqt6', 'flask', 'dash', 
        'stop', 'ps', 'ports', 'test', 'setup'
    ], help='Command to run')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        check_status()
    elif args.command in ['qt', 'pyqt6']:
        launch_interface('qt')
    elif args.command == 'flask':
        launch_interface('flask')
    elif args.command == 'dash':
        launch_interface('dash')
    elif args.command == 'stop':
        manage_processes('stop')
    elif args.command == 'ps':
        manage_processes('status')
    elif args.command == 'ports':
        manage_processes('ports')
    elif args.command == 'test':
        run_tests()
    elif args.command == 'setup':
        setup_environment()
    else:
        print(f"❌ Unknown command: {args.command}")

if __name__ == "__main__":
    main()
