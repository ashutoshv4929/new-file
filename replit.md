# Smart File Converter

## Overview

Smart File Converter is a PDF-focused web application built with Flask that provides comprehensive PDF tools and OCR functionality:

## PDF Tools (iLovePDF-style):
1. **Merge PDF**: Combine multiple PDF files into one
2. **Split PDF**: Split PDF into individual pages  
3. **Compress PDF**: Reduce PDF file size (coming soon)
4. **PDF to Images**: Convert PDF pages to PNG images
5. **Images to PDF**: Create PDF from multiple images

## OCR Feature:
6. **Extract Text**: Extract text from PDF and image files using Google Cloud Vision API

The application features a modern dark-themed interface similar to iLovePDF with comprehensive PDF manipulation tools.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite (default) or PostgreSQL via DATABASE_URL
- **Session Management**: Flask sessions with configurable secret key
- **File Handling**: Werkzeug secure file uploads with 16MB size limit
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap 5.3.0
- **Icons**: Feather Icons
- **JavaScript**: Vanilla JavaScript with modern ES6+ features
- **Theme**: Dark theme with CSS custom properties
- **Responsive Design**: Mobile-first approach using Bootstrap grid system

### Data Storage
- **Primary Database**: SQLite (development) / PostgreSQL (production)
- **File Storage**: Local filesystem with configurable upload/processed folders
- **Cloud Storage**: Google Cloud Storage integration for file backups
- **Session Storage**: Flask session management

## Key Components

### Database Models
1. **ConversionHistory**: Tracks file conversion operations with status, timestamps, and error handling
2. **ExtractedText**: Stores OCR results with confidence scores and metadata
3. **AppSettings**: Configuration storage for application preferences

### Services
1. **OCRService**: Google Cloud Vision API integration for text extraction from images and PDFs
2. **CloudStorageService**: Google Cloud Storage integration for file backup and retrieval

### Core Routes
- `/` - Home dashboard with PDF tools
- `/merge-pdf` - Merge multiple PDF files
- `/split-pdf` - Split PDF into individual pages
- `/compress-pdf` - Compress PDF files (coming soon)
- `/pdf-to-images` - Convert PDF pages to images
- `/images-to-pdf` - Create PDF from images
- `/extract-text` - OCR text extraction using Google Cloud Vision API
- `/my-files` - User file management
- `/history` - Conversion history tracking

## Data Flow

### Upload to Cloud Storage
1. **File Upload**: Users upload files through drag-and-drop interface
2. **Local Save**: File temporarily saved locally
3. **Cloud Upload**: File uploaded to Google Cloud Storage
4. **Database Recording**: Upload history stored in database

### OCR Text Extraction  
1. **File Upload**: Users upload PDF or image files
2. **Google Cloud Vision**: Text extracted using Cloud Vision API
3. **Display Results**: Extracted text displayed on screen
4. **Save Option**: Users can save extracted text as .txt file

### File Conversion
1. **File Upload**: Users upload document files
2. **LibreOffice Processing**: Files converted using LibreOffice headless mode
3. **Format Conversion**: Convert between PDF, DOCX, TXT, ODT formats
4. **Download**: Converted file automatically downloaded

## External Dependencies

### Google Cloud Services
- **Vision API**: OCR text extraction from images and PDFs
- **Cloud Storage**: File backup and retrieval (optional)
- **Authentication**: Service account or default credentials

### Python Libraries
- **Flask**: Web framework and extensions (SQLAlchemy, etc.)
- **Werkzeug**: WSGI utilities and security
- **Pillow**: Image processing and PDF creation
- **PyPDF2**: PDF manipulation (merge, split)
- **pdf2image**: PDF to image conversion
- **google-cloud-vision**: Google Cloud Vision API client
- **google-cloud-storage**: Google Cloud Storage client

### System Dependencies
- **LibreOffice**: Document conversion engine (headless mode)
- **unoconv**: Universal Office Converter for LibreOffice

### Frontend Libraries
- **Bootstrap 5.3.0**: CSS framework via CDN
- **Feather Icons**: Icon library via CDN

## Deployment Strategy

### Environment Configuration
- **Development**: SQLite database, local file storage, debug mode enabled
- **Production**: PostgreSQL via DATABASE_URL, Google Cloud integration, secure session keys

### Required Environment Variables
- `DATABASE_URL`: Database connection string
- `SESSION_SECRET`: Flask session secret key
- `GOOGLE_CLOUD_PROJECT`: Google Cloud project ID
- `GOOGLE_CLOUD_STORAGE_BUCKET`: Cloud Storage bucket name
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account credentials

### File Structure
- `static/uploads/`: Temporary uploaded files
- `static/processed/`: Converted/processed files
- `templates/`: Jinja2 HTML templates
- `services/`: External service integrations

### Security Considerations
- Secure filename handling with Werkzeug
- File type validation and size limits
- Session management with configurable secrets
- Proxy-aware deployment with ProxyFix middleware

## Recent Changes

**July 10, 2025**: Transformed into iLovePDF-style PDF tools application:
- Added comprehensive PDF tools: Merge, Split, Compress, PDF↔Images conversion
- Implemented PyPDF2 for PDF manipulation operations
- Created dedicated pages for each PDF tool with intuitive interfaces
- Maintained OCR text extraction functionality
- Removed file conversion feature as requested
- Updated navigation to focus on PDF tools and OCR

The application is designed to be easily deployable on cloud platforms with minimal configuration, while providing robust file conversion and OCR capabilities through Google Cloud services integration.