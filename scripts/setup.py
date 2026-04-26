"""
Install Python dependencies for the resume-customiser plugin.
Run once before first use: python setup.py
"""
import subprocess
import sys


PACKAGES = [
    "python-docx",
    "pdfplumber",
    "requests",
    "beautifulsoup4",
    "lxml",
]


def main():
    print("Installing resume-customiser dependencies...\n")
    for pkg in PACKAGES:
        print(f"  Installing {pkg}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", pkg, "--quiet"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"  OK: {pkg}")
        else:
            print(f"  FAILED: {pkg}")
            print(result.stderr)

    print("\nSetup complete. Run /resume-customise in Claude Code to start.")


if __name__ == "__main__":
    main()
