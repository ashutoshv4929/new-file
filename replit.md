# Smart File Converter

## Overview

Smart File Converter is a simplified web-based application built with Flask that focuses on three core features:
1. **Upload to Google Cloud Storage**: Upload PDF and image files directly to Google Cloud Storage
2. **OCR Text Extraction**: Extract text from PDF and image files using Google Cloud Vision API  
3. **File Conversion**: Convert documents between formats (PDF, DOC, DOCX, TXT) using LibreOffice

The application features a modern dark-themed interface and integrates with Google Cloud services for cloud storage and OCR functionality.

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
- `/` - Home dashboard with three main features
- `/upload` - Upload files to Google Cloud Storage
- `/extract-text` - OCR text extraction using Google Cloud Vision API
- `/convert` - File conversion using LibreOffice
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
- **Pillow**: Image processing
- **pdf2image**: PDF to image conversion for OCR
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

**July 10, 2025**: Simplified application to focus on three core features:
- Streamlined interface with three main options: Upload to Cloud, Extract Text, Convert Files
- Added LibreOffice integration for real document conversion (PDF, DOCX, TXT, ODT)
- Updated navigation and UI to focus on the three core features
- Removed unnecessary settings and complexity

The application is designed to be easily deployable on cloud platforms with minimal configuration, while providing robust file conversion and OCR capabilities through Google Cloud services integration.