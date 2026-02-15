# Example: Using MTH5 Validator in Your CI/CD

This directory contains example workflows for integrating the MTH5 validator into your own projects.

## GitHub Actions Examples

### Basic Validation on Push

Create `.github/workflows/validate-mth5.yml` in your repository:

```yaml
name: Validate MTH5 Files

on:
  push:
    paths:
      - '**.mth5'
  pull_request:
    paths:
      - '**.mth5'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Download MTH5 Validator
        run: |
          wget https://github.com/MTgeophysics/mth5-validator/releases/latest/download/mth5-validator-linux-amd64
          chmod +x mth5-validator-linux-amd64
      
      - name: Validate all MTH5 files
        run: |
          for file in $(find . -name "*.mth5"); do
            echo "Validating: $file"
            ./mth5-validator-linux-amd64 validate "$file" --verbose || exit 1
          done
```

### Validation with Artifacts

Save validation reports as artifacts:

```yaml
name: Validate and Report

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Download MTH5 Validator
        run: |
          wget https://github.com/MTgeophysics/mth5-validator/releases/latest/download/mth5-validator-linux-amd64
          chmod +x mth5-validator-linux-amd64
      
      - name: Create reports directory
        run: mkdir -p reports
      
      - name: Validate and create reports
        run: |
          for file in data/*.mth5; do
            filename=$(basename "$file" .mth5)
            ./mth5-validator-linux-amd64 validate "$file" --json > "reports/${filename}_report.json"
          done
      
      - name: Upload validation reports
        uses: actions/upload-artifact@v4
        with:
          name: validation-reports
          path: reports/
```

### Matrix Validation (Multiple Platforms)

Test on multiple operating systems:

```yaml
name: Multi-Platform Validation

on: [push, pull_request]

jobs:
  validate:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        include:
          - os: ubuntu-latest
            validator: mth5-validator-linux-amd64
          - os: windows-latest
            validator: mth5-validator-windows-amd64.exe
          - os: macos-latest
            validator: mth5-validator-macos-amd64
    
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Download validator (Linux/macOS)
        if: runner.os != 'Windows'
        run: |
          wget https://github.com/MTgeophysics/mth5-validator/releases/latest/download/${{ matrix.validator }}
          chmod +x ${{ matrix.validator }}
      
      - name: Download validator (Windows)
        if: runner.os == 'Windows'
        run: |
          curl -L -o ${{ matrix.validator }} https://github.com/MTgeophysics/mth5-validator/releases/latest/download/${{ matrix.validator }}
      
      - name: Validate files
        shell: bash
        run: |
          for file in tests/data/*.mth5; do
            ./${{ matrix.validator }} validate "$file" --verbose
          done
```

## GitLab CI Example

`.gitlab-ci.yml`:

```yaml
stages:
  - validate

validate_mth5:
  stage: validate
  image: ubuntu:latest
  before_script:
    - apt-get update && apt-get install -y wget
    - wget https://github.com/MTgeophysics/mth5-validator/releases/latest/download/mth5-validator-linux-amd64
    - chmod +x mth5-validator-linux-amd64
  script:
    - |
      for file in data/*.mth5; do
        echo "Validating: $file"
        ./mth5-validator-linux-amd64 validate "$file" --verbose
      done
  artifacts:
    when: always
    paths:
      - "*.json"
```

## Jenkins Example

```groovy
pipeline {
    agent any
    
    stages {
        stage('Download Validator') {
            steps {
                sh '''
                    wget https://github.com/MTgeophysics/mth5-validator/releases/latest/download/mth5-validator-linux-amd64
                    chmod +x mth5-validator-linux-amd64
                '''
            }
        }
        
        stage('Validate') {
            steps {
                sh '''
                    for file in data/*.mth5; do
                        ./mth5-validator-linux-amd64 validate "$file" --json > "${file%.mth5}_report.json"
                    done
                '''
            }
        }
        
        stage('Archive Reports') {
            steps {
                archiveArtifacts artifacts: '*_report.json', fingerprint: true
            }
        }
    }
}
```

## Docker Example

```dockerfile
FROM ubuntu:22.04

# Install wget
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*

# Download validator
RUN wget https://github.com/MTgeophysics/mth5-validator/releases/latest/download/mth5-validator-linux-amd64 \
    && chmod +x mth5-validator-linux-amd64 \
    && mv mth5-validator-linux-amd64 /usr/local/bin/mth5-validator

# Validate files in mounted volume
ENTRYPOINT ["mth5-validator"]
CMD ["--help"]
```

Usage:
```bash
docker build -t mth5-validator .
docker run -v $(pwd)/data:/data mth5-validator validate /data/file.mth5
```

## Pre-commit Hook Example

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: validate-mth5
        name: Validate MTH5 files
        entry: ./scripts/validate-mth5-hook.sh
        language: script
        files: \.mth5$
```

`scripts/validate-mth5-hook.sh`:
```bash
#!/bin/bash

VALIDATOR="./mth5-validator-linux-amd64"

if [ ! -f "$VALIDATOR" ]; then
    echo "Downloading validator..."
    wget -q https://github.com/MTgeophysics/mth5-validator/releases/latest/download/mth5-validator-linux-amd64
    chmod +x mth5-validator-linux-amd64
fi

for file in "$@"; do
    if [[ $file == *.mth5 ]]; then
        echo "Validating: $file"
        $VALIDATOR validate "$file" || exit 1
    fi
done
```

## Tips

1. **Cache the validator**: Download once and cache to speed up workflows
2. **Pin versions**: Use specific release tags instead of `latest` for reproducibility
3. **Parallel validation**: Use job matrices to validate multiple files in parallel
4. **Conditional validation**: Only validate changed files to save time
5. **Fail fast**: Set `exit 1` on validation errors to stop workflows early

## Verification

Always verify downloaded executables using checksums:

```bash
# Download executable and checksum
wget https://github.com/MTgeophysics/mth5-validator/releases/latest/download/mth5-validator-linux-amd64
wget https://github.com/MTgeophysics/mth5-validator/releases/latest/download/mth5-validator-linux-amd64.sha256

# Verify
sha256sum -c mth5-validator-linux-amd64.sha256
```
