#!/usr/bin/env python3
"""
Generate API Documentation using pdoc.

Usage:
    python generate_docs.py

This will generate HTML documentation in docs/api/
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Generate API documentation."""
    # Paths
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src" / "asr_mp"
    output_path = project_root / "docs" / "api"

    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    print("Generating API documentation...")
    print(f"Source: {src_path}")
    print(f"Output: {output_path}")

    # Run pdoc
    cmd = [
        sys.executable,
        "-m",
        "pdoc",
        "--html",
        "--output-dir",
        str(output_path),
        "--force",
        str(src_path),
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ Documentation generated at: {output_path}")
        print(f"   Open {output_path / 'asr_mp' / 'index.html'} in a browser")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to generate documentation: {e}")
        print("   Make sure pdoc is installed: pip install pdoc")
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ pdoc not found. Install with: pip install pdoc")
        sys.exit(1)


if __name__ == "__main__":
    main()
