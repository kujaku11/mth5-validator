# MTH5 Validator Package Setup Guide

## Summary

Your mth5-validator package is now set up as a standalone package with automated GitHub Actions builds for Windows, Linux, and macOS!

## What Was Created

### 1. **pyproject.toml**
- Package metadata and configuration
- Minimal dependencies (only h5py)
- Scripts entry point for command-line usage
- Python version compatibility (3.8+)

### 2. **requirements.txt**
- Runtime dependency: h5py
- Build dependency: pyinstaller

### 3. **.github/workflows/build-executables.yml**
- Automated builds on push to main/develop
- Matrix strategy for Windows, Linux, and macOS
- Automatic artifact uploads
- Automatic GitHub release creation on tags
- Checksums (SHA256) for each executable

### 4. **.gitignore**
- Standard Python ignores
- Build artifacts
- IDE files
- Test data exclusions

### 5. **README.md** (Updated)
- Standalone package focus
- Pre-built executable download instructions
- Installation options
- GitHub Actions integration examples
- Updated troubleshooting

## How to Use the GitHub Actions Workflow

### On Every Push

When you push to `main` or `develop` branches:
1. GitHub Actions automatically builds executables for all 3 platforms
2. Artifacts are uploaded and available in the Actions tab
3. Each artifact includes the executable and a SHA256 checksum

To download artifacts:
1. Go to your repository's Actions tab
2. Click on the latest workflow run
3. Scroll down to "Artifacts"
4. Download the executable for your platform

### On Tagged Releases

When you create a release tag (e.g., `v0.1.0`):
```bash
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

GitHub Actions will:
1. Build all executables
2. Create a GitHub Release automatically  
3. Attach all executables and checksums to the release
4. Generate release notes

Users can then download pre-built executables directly from the Releases page!

## Next Steps

### 1. Push to GitHub

```bash
cd mth5-validator

# If not already initialized
git init
git add .
git commit -m "Initial commit: standalone validator package"

# Add remote (use your actual GitHub URL)
git remote add origin https://github.com/MTgeophysics/mth5-validator.git
git branch -M main
git push -u origin main
```

### 2. Test the GitHub Actions

After pushing, check:
1. Go to Actions tab in your GitHub repository
2. Watch the "Build Executables" workflow run
3. Verify all 3 builds complete successfully
4. Download and test the artifacts

### 3. Create Your First Release

```bash
# Tag a release
git tag -a v0.1.0 -m "Initial release"
git push origin v0.1.0
```

This will trigger the workflow and create a release with all executables attached.

### 4. Optional: Publish to PyPI

If you want users to `pip install mth5-validator`:

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Upload to PyPI (you'll need PyPI credentials)
python -m twine upload dist/*
```

## Repository Settings

### Secrets (if needed)

The workflow uses `GITHUB_TOKEN` which is automatically provided. No secrets setup needed!

### Branch Protection (Optional)

Consider protecting your main branch:
1. Go to Settings → Branches
2. Add rule for `main`
3. Require status checks to pass (including the build workflow)

## Testing Locally

Before pushing, test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Build executable
cd src
python build_standalone_validator.py

# Test the executable
dist/mth5-validator --help
dist/mth5-validator validate path/to/test.mth5
```

## File Sizes

Expected executable sizes:
- Windows: ~20-30 MB
- Linux: ~20-30 MB
- macOS: ~20-30 MB

Much smaller than full mth5 package (~150+ MB) because it only includes h5py!

## Advantages of This Setup

✓ **Automated**: Builds happen automatically on every push  
✓ **Multi-platform**: Windows, Linux, and macOS supported  
✓ **Lightweight**: ~20-30 MB executables vs 150+ MB for full mth5  
✓ **No dependencies**: Users don't need Python installed  
✓ **Easy distribution**: Download from GitHub Releases  
✓ **CI/CD ready**: Perfect for automated pipelines  
✓ **Checksums**: SHA256 hashes for security verification  

## Workflow Triggers

The workflow runs on:
- **Push** to main or develop branches
- **Pull requests** to main or develop
- **Tags** starting with 'v' (for releases)
- **Manual dispatch** (can trigger from Actions tab)

## Customization

You can modify the workflow file to:
- Change which branches trigger builds
- Add tests before building
- Upload to other services (S3, etc.)
- Add code signing (for Windows/macOS)
- Customize artifact names

## Support

If you have issues:
1. Check the Actions tab for build logs
2. Ensure src/mth5_validator_standalone.py exists
3. Verify requirements.txt has h5py and pyinstaller
4. Check that Python 3.11 is compatible with your code

Happy validating! 🎉
