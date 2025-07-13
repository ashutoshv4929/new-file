#!/bin/bash
# Install system dependencies
apt-get update
apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libopenjp2-tools \
    poppler-utils \
    qpdf \
    libqpdf-dev

# Install Python packages
pip install -r requirements.txt
