import os
import traceback

SRC_DIR = "src"

def import_path(path):
    # Convert file path to module path (e.g. src/utils/thing.py → src.utils.thing)
    rel_path = os.path.relpath(path, ".").replace(os.sep, ".")
    if rel_path.endswith(".py"):
        rel_path = rel_path[:-3]  # strip .py
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
            except Exception as e:
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
