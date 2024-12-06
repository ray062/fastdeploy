# src/presentation/cli.py
from pathlib import Path
from typing import List

def select_profile(available_profiles: List[str]) -> str:
    print("\nAvailable profiles:")
    for i, profile in enumerate(available_profiles, 1):
        print(f"{i}. {profile}")
    
    while True:
        try:
            choice = int(input("\nSelect profile number: ")) - 1
            if 0 <= choice < len(available_profiles):
                return available_profiles[choice]
        except ValueError:
            pass
        print("Invalid selection. Please try again.")
