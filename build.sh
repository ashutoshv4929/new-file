#!/bin/bash
set -e

# Set up logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Install system dependencies
log "Updating package lists..."
apt-get update

log "Installing system dependencies..."
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3-dev \
    python3-pip \
    ghostscript \
    poppler-utils \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    qpdf \
    libqpdf-dev \
    libjpeg-dev \
    zlib1g-dev

# Verify Ghostscript installation
log "Verifying Ghostscript installation..."
gs_version=$(gs --version 2>/dev/null || echo "not installed")
log "Ghostscript version: $gs_version"

# Install Python packages
log "Installing Python packages..."
pip install --no-cache-dir -r requirements.txt

# Verify Python packages
log "Verifying Python packages..."
python3 -c "
import sys
import pkg_resources

required = {
    'flask',
    'ghostscript',
    'pdf2image',
    'pillow',
    'gunicorn'
}

installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    print(f'Error: Missing packages: {missing}', file=sys.stderr)
    sys.exit(1)
else:
    print('All required packages are installed')
"

log "Build completed successfully!"
exit 0
