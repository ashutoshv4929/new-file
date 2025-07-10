# Smart File Converter

## Overview

Smart File Converter is a web-based application built with Flask that provides file conversion and OCR (Optical Character Recognition) services. The application allows users to upload documents and images, convert them between different formats, and extract text using Google Cloud Vision API. It features a modern dark-themed interface and integrates with Google Cloud services for enhanced functionality.

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
- `/` - Home dashboard with conversion statistics
- `/upload` - File upload interface with drag-and-drop support
- `/extract-text` - OCR text extraction interface
- `/my-files` - User file management
- `/history` - Conversion history tracking
- `/settings` - Application configuration

## Data Flow

1. **File Upload**: Users upload files through drag-and-drop or file picker
2. **Validation**: File type and size validation against allowed extensions
3. **Processing**: Files are processed based on conversion type (PDF conversion, OCR extraction)
4. **Storage**: Processed files stored locally, optionally backed up to Google Cloud Storage
5. **Database Recording**: Conversion history and results stored in database
6. **Result Delivery**: Users can download converted files or view extracted text

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

The application is designed to be easily deployable on cloud platforms with minimal configuration, while providing robust file conversion and OCR capabilities through Google Cloud services integration.