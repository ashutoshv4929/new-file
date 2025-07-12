# Smart File Converter - Complete Application

## Overview
A professional PDF tools application similar to iLovePDF with OCR functionality, featuring a modern dark theme interface.

## Features
- **Merge PDF**: Combine multiple PDF files into one
- **Split PDF**: Split PDF into individual pages
- **Compress PDF**: Reduce PDF file size (coming soon)
- **PDF to Images**: Convert PDF pages to PNG images
- **Images to PDF**: Create PDF from multiple images
- **Extract Text**: OCR text extraction using Google Cloud Vision API

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables (Optional)
Create a `.env` file with:
```
DATABASE_URL=sqlite:///smart_converter.db
SESSION_SECRET=your-secret-key-here
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_STORAGE_BUCKET=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

### 3. Run the Application
```bash
python main.py
```

Or with Gunicorn:
```bash
gunicorn --bind 0.0.0.0:5000 --reload main:app
```

## File Structure
```
smart_file_converter/
├── app.py              # Flask application setup
├── main.py             # Application entry point
├── models.py           # Database models
├── routes.py           # Application routes
├── pyproject.toml      # Project dependencies
├── templates/          # HTML templates
│   ├── base.html       # Base template
│   ├── index.html      # Home page
│   ├── extract_text.html # OCR page
│   └── pdf_tools/      # PDF tool pages
├── static/             # Static assets
│   ├── css/style.css   # Main stylesheet
│   ├── js/app.js       # JavaScript functionality
│   ├── uploads/        # Upload directory
│   └── processed/      # Processed files
└── services/           # External services
    ├── cloud_storage.py # Google Cloud Storage
    └── ocr_service.py   # Google Cloud Vision OCR
```

## Key Features Implemented
- ✅ Dark theme UI with excellent text visibility
- ✅ Mobile-friendly responsive design
- ✅ PDF manipulation tools (merge, split, convert)
- ✅ OCR text extraction with Google Cloud Vision
- ✅ File upload with drag-and-drop support
- ✅ Progress indicators and user feedback
- ✅ Professional navigation and layout
- ✅ Error handling and validation

## Technology Stack
- **Backend**: Flask, SQLAlchemy, PyPDF2, Pillow
- **Frontend**: Bootstrap 5, Feather Icons, Vanilla JavaScript
- **Database**: SQLite (default) / PostgreSQL
- **Cloud Services**: Google Cloud Storage, Google Cloud Vision API
- **Deployment**: Gunicorn WSGI server

## Notes
- The application works perfectly with local file storage
- Google Cloud services are optional for enhanced functionality
- All text visibility issues have been resolved
- Professional UI with consistent dark theme
- Ready for production deployment

## Support
The application is fully functional with all PDF tools and OCR features working properly.