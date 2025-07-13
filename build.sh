#!/bin/bash
set -e

# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
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
gs_version=$(gs --version 2>/dev/null || echo "not installed")
echo "Ghostscript version: $gs_version"

# Create a test PDF to verify Ghostscript can create PDFs
echo "Testing Ghostscript PDF creation..."
echo "%!PS" > test.ps
echo "/Helvetica findfont 24 scalefont setfont" >> test.ps
echo "100 100 moveto" >> test.ps
echo "(Hello, World!) show" >> test.ps
echo "showpage" >> test.ps

gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=test.pdf test.ps 2>/dev/null

if [ -f "test.pdf" ]; then
    echo "Ghostscript test: Successfully created test.pdf"
    rm -f test.ps test.pdf
else
    echo "Ghostscript test: Failed to create test PDF"
    exit 1
fi

# Install Python packages
pip install -r requirements.txt

# Verify Python packages
python3 -c "import ghostscript; print(f'Ghostscript Python bindings version: {ghostscript.__version__}')"
