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

# Install Python packages
pip install -r requirements.txt
