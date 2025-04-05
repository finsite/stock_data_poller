"""
Script to bump the version number in the repository.

The script takes two arguments from the command line. The first argument is the current
version string, and the second argument is the part of the version to increment. The
parts of the version are 'major', 'minor', and 'patch'.

The script will exit with a status code of 1 if there is an error.
"""

import sys

from packaging.version import Version  # Import Version class for version handling

# Example usage:
# python bump_version.py 1.0.0 patch


def next_version(current: str, part: str) -> str:
    """
    Increment a version.

    This function takes a version string and a part ('major', 'minor', or 'patch'),
    and returns a new version string with the specified part incremented.

    Args:
    ----
        current (str): The current version string.
        part (str): The part of the version to increment ('major', 'minor', or 'patch').

    Returns:
    -------
        str: A new version string with the specified part incremented.

    Raises:
    ------
        ValueError: If the part is not 'major', 'minor', or 'patch'.
    """
    v = Version(current)  # Parse the current version string
    if part == "major":  # Increment the major version
        return f"{v.major + 1}.0.0"
    elif part == "minor":  # Increment the minor version
        return f"{v.major}.{v.minor + 1}.0"
    elif part == "patch":  # Increment the patch version
        return f"{v.major}.{v.minor}.{v.micro + 1}"
    else:
        raise ValueError("Specify 'major', 'minor', or 'patch'.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python setup.py <current_version> <major|minor|patch>")
        sys.exit(1)
    current_version, part = sys.argv[1], sys.argv[2]
    try:
        print(next_version(current_version, part))
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
