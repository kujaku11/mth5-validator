#!/usr/bin/env python
"""
Build Standalone MTH5 Validator Executable
===========================================

Builds a lightweight executable (~20-30 MB) that only depends on h5py.

Much smaller and simpler than the full mth5-based validator because:
- No scipy/numpy/obspy dependencies
- No matplotlib/pandas dependencies
- No mth5 I/O stack
- Just h5py + standard library

Usage:
    python build_standalone_validator.py

Output:
    dist/mth5-validator.exe (Windows) - ~20-30 MB
    dist/mth5-validator (Linux/Mac)

Author: MTH5 Development Team
Date: February 9, 2026
"""

import os
import platform
import shutil
import sys
from pathlib import Path


def safe_print(message):
    """Print with fallback for encoding issues (Windows CP1252)."""
    try:
        print(message)
    except UnicodeEncodeError:
        # Fallback: replace problematic Unicode chars
        message = message.replace('✓', '[OK]').replace('✗', '[X]')
        print(message.encode('ascii', 'replace').decode('ascii'))


def check_dependencies():
    """Check that required dependencies are installed."""
    safe_print("Checking dependencies...")

    # Check h5py
    try:
        import h5py

        safe_print(f"  [OK] h5py {h5py.__version__}")
    except ImportError:
        safe_print("  [X] h5py not found - installing...")
        os.system(f"{sys.executable} -m pip install h5py")

    # Check PyInstaller
    try:
        import PyInstaller

        safe_print(f"  [OK] PyInstaller {PyInstaller.__version__}")
        return True
    except ImportError:
        safe_print("  [X] PyInstaller not found - installing...")
        os.system(f"{sys.executable} -m pip install pyinstaller")
        try:
            import PyInstaller

            safe_print(f"  [OK] PyInstaller {PyInstaller.__version__} installed")
            return True
        except ImportError:
            safe_print("  [X] Failed to install PyInstaller")
            return False


def clean_build_dirs():
    """Clean previous build artifacts."""
    import stat
    import time

    def handle_remove_readonly(func, path, exc):
        """Error handler for Windows read-only files."""
        if func in (os.rmdir, os.remove, os.unlink):
            try:
                os.chmod(path, stat.S_IWRITE)
                func(path)
            except Exception:
                pass

    dirs_to_clean = ["build", "dist"]
    files_to_clean = ["*.spec"]

    safe_print("\nCleaning previous build artifacts...")

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                time.sleep(0.1)
                shutil.rmtree(dir_name, onerror=handle_remove_readonly)
                safe_print(f"  Removed {dir_name}/")
            except Exception as e:
                safe_print(f"  Warning: Could not fully remove {dir_name}/ ({e})")

    for pattern in files_to_clean:
        for file in Path(".").glob(pattern):
            try:
                file.unlink()
                safe_print(f"  Removed {file}")
            except Exception as e:
                safe_print(f"  Warning: Could not remove {file} ({e})")


def build_executable():
    """Build the standalone validator executable."""
    import PyInstaller.__main__

    system = platform.system()
    exe_name = "mth5-validator"
    if system == "Windows":
        exe_name += ".exe"

    safe_print(f"\nBuilding Standalone MTH5 Validator for {system}...")
    safe_print("=" * 80)

    # Simple PyInstaller arguments - h5py + minimal numpy
    args = [
        "mth5_validator_standalone.py",  # Standalone entry point
        "--onefile",  # Single executable
        f'--name={exe_name.replace(".exe", "")}',  # Output name
        "--console",  # Console application
        "--clean",  # Clean cache
        # Collect h5py completely (includes numpy automatically)
        "--collect-all=h5py",
        "--hidden-import=h5py.defs",
        "--hidden-import=h5py.utils",
        "--hidden-import=h5py._proxy",
        "--hidden-import=h5py.h5ac",
        "--copy-metadata=h5py",
        "--copy-metadata=numpy",
        # Exclude heavy packages we don't need
        "--exclude-module=matplotlib",
        "--exclude-module=scipy",
        "--exclude-module=pandas",
        "--exclude-module=tkinter",
        "--exclude-module=PyQt5",
        "--exclude-module=PyQt6",
        "--exclude-module=jupyter",
        "--exclude-module=IPython",
        "--exclude-module=pytest",
        "--exclude-module=obspy",
        "--exclude-module=mt_metadata",
        "--exclude-module=mth5",
        # Logging
        "--log-level=WARN",
    ]

    safe_print("\nPyInstaller configuration:")
    safe_print(f"  Entry point: mth5_validator_standalone.py")
    safe_print(f"  Output name: {exe_name}")
    safe_print(f"  Mode: Single file")
    safe_print(f"  Dependencies: h5py only")
    safe_print(f"  Platform: {system}")

    try:
        PyInstaller.__main__.run(args)
        safe_print("\n" + "=" * 80)
        safe_print("[OK] Build completed successfully!")
        return True
    except Exception as e:
        safe_print("\n" + "=" * 80)
        safe_print(f"[X] Build failed: {e}")
        return False


def test_executable():
    """Test the built executable."""
    system = platform.system()
    exe_path = Path("dist") / (
        "mth5-validator.exe" if system == "Windows" else "mth5-validator"
    )

    if not exe_path.exists():
        safe_print(f"\n[X] Executable not found: {exe_path}")
        return False

    safe_print(f"\nTesting executable: {exe_path}")
    safe_print("=" * 80)

    # Get file size
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    safe_print(f"  Size: {size_mb:.1f} MB")

    # Test help command
    safe_print("\n  Running: mth5-validator --help")
    safe_print("-" * 80)
    result = os.system(f'"{exe_path}" --help')

    if result == 0:
        safe_print("-" * 80)
        safe_print("[OK] Executable test passed!")
        return True
    else:
        safe_print("[X] Executable test failed")
        return False


def print_summary():
    """Print build summary and usage instructions."""
    system = platform.system()
    exe_name = "mth5-validator.exe" if system == "Windows" else "mth5-validator"
    exe_path = Path("dist") / exe_name

    safe_print("\n" + "=" * 80)
    safe_print("BUILD SUMMARY")
    safe_print("=" * 80)

    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        safe_print(f"\n[OK] Standalone executable created: {exe_path.absolute()}")
        safe_print(f"  Size: {size_mb:.1f} MB (lightweight - h5py only!)")
        safe_print(f"  Platform: {system}")

        safe_print("\n" + "-" * 80)
        safe_print("USAGE")
        safe_print("-" * 80)
        safe_print(f"\n  Basic validation:")
        safe_print(f"    {exe_path} validate data.mth5")
        safe_print(f"\n  Verbose output:")
        safe_print(f"    {exe_path} validate data.mth5 --verbose")
        safe_print(f"\n  Check data integrity:")
        safe_print(f"    {exe_path} validate data.mth5 --check-data")
        safe_print(f"\n  JSON output:")
        safe_print(f"    {exe_path} validate data.mth5 --json")

        safe_print("\n" + "-" * 80)
        safe_print("ADVANTAGES")
        safe_print("-" * 80)
        safe_print(f"\n  + Small size: ~20-30 MB (vs 150+ MB for full mth5)")
        safe_print(f"  + Simple dependencies: h5py only")
        safe_print(f"  + No scipy/obspy/matplotlib bloat")
        safe_print(f"  + Fast startup and execution")
        safe_print(f"  + Standalone - no Python install needed")

        safe_print("\n" + "-" * 80)
        safe_print("DISTRIBUTION")
        safe_print("-" * 80)
        safe_print(f"\n  The executable in dist/ can be distributed standalone.")
        safe_print(f"  Users do NOT need Python or any dependencies installed.")
        safe_print(f"  Copy {exe_name} to any system and run it directly.")
    else:
        safe_print(f"\n[X] Build failed - executable not found")

    safe_print("\n" + "=" * 80)


def main():
    """Main build process."""
    safe_print("=" * 80)
    safe_print("MTH5 Standalone Validator - Executable Builder")
    safe_print("=" * 80)
    safe_print(f"\nPlatform: {platform.system()} {platform.machine()}")
    safe_print(f"Python: {sys.version.split()[0]}")

    # Check standalone script exists
    if not Path("mth5_validator_standalone.py").exists():
        safe_print("\n[X] Error: mth5_validator_standalone.py not found!")
        safe_print("  Make sure you're running this from the mth5 repository root.")
        sys.exit(1)

    # Check dependencies
    if not check_dependencies():
        safe_print("\n[X] Cannot proceed without required dependencies")
        sys.exit(1)

    # Clean previous builds
    clean_build_dirs()

    # Build executable
    if not build_executable():
        safe_print("\n[X] Build failed")
        sys.exit(1)

    # Test executable
    test_executable()

    # Print summary
    print_summary()

    return 0


if __name__ == "__main__":
    sys.exit(main())
