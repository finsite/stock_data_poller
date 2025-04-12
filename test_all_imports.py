"""Check that all modules in the src directory can be imported without errors.

This script helps ensure that there are no circular imports or other issues that
prevent importing the modules in the src directory.

Imports:
    os: Provides functions for interacting with the operating system.
    traceback: Provides utilities for extracting, formatting, and printing stack traces.

"""

import os
import traceback


SRC_DIR = "src"


def import_path(path: str) -> str:
    """Convert a file path to a module path.

    Takes a file path (e.g., "src/utils/thing.py") and converts it to a
    module path (e.g., "src.utils.thing").

    Args:
        path (str): The file path to convert.

    Returns:
        str: The module path corresponding to the given file path.
    """
    rel_path: str = os.path.relpath(path, ".").replace(os.sep, ".")
    if rel_path.endswith(".py"):
        rel_path = rel_path[:-3]
    return rel_path


failures = []

for root, _, files in os.walk(SRC_DIR):
    for file in files:
        if file.endswith(".py") and not file.startswith("__init__"):
            full_path = os.path.join(root, file)
            module = import_path(full_path)

            try:
                print(f"🔍 Importing {module}...")
                __import__(module)
            except Exception:
                print(f"❌ FAILED: {module}")
                traceback.print_exc()
                failures.append(module)

print("\n✅ Import test complete.")
if failures:
    print("\n❌ The following modules failed to import:")
    for mod in failures:
        print(f"  - {mod}")
else:
    print("🎉 All modules imported successfully!")
