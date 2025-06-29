#!/usr/bin/env python3
"""
Attack Test Runner

This script provides an easy way to run the attack simulation with different configurations.
"""

import subprocess
import sys
import os
from typing import Optional

def run_attack_test(
    target_url: str,
    api_key: str,
    test_type: str = "all",
    interval: float = 0.5
) -> None:
    """Run the attack simulation test.
    
    Args:
        target_url: Target URL for the VESSA API
        api_key: API key for authentication
        test_type: Type of test to run (all, attacks, threat-intel, analytics)
        interval: Interval between requests in seconds
    """
    script_path = os.path.join(os.path.dirname(__file__), "attack.py")
    
    cmd = [
        sys.executable,
        script_path,
        "--target", target_url,
        "--api-key", api_key,
        "--test-type", test_type,
        "--interval", str(interval)
    ]
    
    print(f"Running attack test with command: {' '.join(cmd)}")
    print(f"Target URL: {target_url}")
    print(f"Test Type: {test_type}")
    print(f"Interval: {interval}s")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print("\n" + "-" * 60)
        print("Attack test completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\nAttack test failed with exit code {e.returncode}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAttack test interrupted by user")
        sys.exit(1)

def main():
    """Main entry point with interactive configuration."""
    print("VESSA Attack Simulation Test Runner")
    print("=" * 50)
    
    # Get configuration from user
    target_url = input("Enter target URL (e.g., http://localhost:8000): ").strip()
    if not target_url:
        print("Error: Target URL is required")
        sys.exit(1)
    
    api_key = input("Enter API key: ").strip()
    if not api_key:
        print("Error: API key is required")
        sys.exit(1)
    
    print("\nAvailable test types:")
    print("1. all - Run all tests (attacks + threat intelligence + analytics)")
    print("2. attacks - Run only attack simulations")
    print("3. threat-intel - Test threat intelligence endpoints only")
    print("4. analytics - Test analytics endpoints only")
    
    test_type_choice = input("\nSelect test type (1-4, default: 1): ").strip()
    
    test_type_map = {
        "1": "all",
        "2": "attacks", 
        "3": "threat-intel",
        "4": "analytics"
    }
    
    test_type = test_type_map.get(test_type_choice, "all")
    
    interval_input = input("Enter interval between requests in seconds (default: 0.5): ").strip()
    try:
        interval = float(interval_input) if interval_input else 0.5
    except ValueError:
        interval = 0.5
    
    print(f"\nConfiguration:")
    print(f"  Target URL: {target_url}")
    print(f"  Test Type: {test_type}")
    print(f"  Interval: {interval}s")
    
    confirm = input("\nProceed with attack test? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Attack test cancelled")
        sys.exit(0)
    
    # Run the test
    run_attack_test(target_url, api_key, test_type, interval)

if __name__ == "__main__":
    main() 