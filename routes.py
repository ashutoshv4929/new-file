import os
import uuid
import subprocess
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
from app import app, db
from models import ConversionHistory, ExtractedText, AppSettings
from services.ocr_service import OCRService
from services.cloud_storage import CloudStorageService
from sqlalchemy import func

# Initialize services
ocr_service = OCRService()
cloud_storage_service = CloudStorageService()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_stats():
    """Get conversion statistics"""
    today = datetime.utcnow().date()
    today_count = ConversionHistory.query.filter(
        func.date(ConversionHistory.created_at) == today
    ).count()
    
    total_count = ConversionHistory.query.count()
    saved_count = ConversionHistory.query.filter_by(status='completed').count()
    
    return {
        'today': today_count,
        'total': total_count,
        'saved': saved_count
    }

@app.route('/')
def index():
    """Home page with conversion options"""
    stats = get_stats()
    return render_template('index.html', stats=stats)

@app.route('/upload')
def upload_page():
    """File upload page"""
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload to Google Cloud Storage"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            # Ensure upload directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)
            
            # Upload to Google Cloud Storage
            if cloud_storage_service.is_configured():
                try:
                    cloud_storage_service.upload_file(filepath, filename)
                    flash('File uploaded to Google Cloud Storage successfully!', 'success')
                    
                    # Save to database
                    conversion = ConversionHistory(
                        filename=filename,
                        original_filename=file.filename,
                        file_type=file.filename.rsplit('.', 1)[1].lower(),
                        conversion_type='cloud_upload',
                        file_size=os.path.getsize(filepath),
                        status='completed',
                        processed_at=datetime.utcnow()
                    )
                    db.session.add(conversion)
                    db.session.commit()
                    
                except Exception as e:
                    app.logger.error(f'Cloud storage upload error: {str(e)}')
                    flash(f'Error uploading to cloud: {str(e)}', 'error')
                    
                    # Save locally as fallback
                    conversion = ConversionHistory(
                        filename=filename,
                        original_filename=file.filename,
                        file_type=file.filename.rsplit('.', 1)[1].lower(),
                        conversion_type='local_upload',
                        file_size=os.path.getsize(filepath),
                        status='completed',
                        processed_at=datetime.utcnow()
                    )
                    db.session.add(conversion)
                    db.session.commit()
            else:
                flash('Google Cloud Storage not configured. File saved locally.', 'warning')
                
                # Save to database
                conversion = ConversionHistory(
                    filename=filename,
                    original_filename=file.filename,
                    file_type=file.filename.rsplit('.', 1)[1].lower(),
                    conversion_type='local_upload',
                    file_size=os.path.getsize(filepath),
                    status='completed',
                    processed_at=datetime.utcnow()
                )
                db.session.add(conversion)
                db.session.commit()
            
            return redirect(url_for('my_files'))
            
        except Exception as e:
            flash(f'Error uploading file: {str(e)}', 'error')
            return redirect(request.url)
    
    flash('Invalid file type. Please upload PDF, DOC, DOCX, TXT, or image files.', 'error')
    return redirect(request.url)

@app.route('/extract-text')
def extract_text_page():
    """OCR text extraction page"""
    return render_template('extract_text.html')

@app.route('/extract-text', methods=['POST'])
def extract_text():
    """Handle OCR text extraction"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(request.url)
    
    if file and file.filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'gif', 'pdf']:
        # Generate unique filename
        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            # Ensure upload directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)
            
            # Extract text using OCR
            extracted_text, confidence = ocr_service.extract_text(filepath)
            
            if extracted_text:
                # Save extracted text to database
                text_record = ExtractedText(
                    filename=filename,
                    original_filename=file.filename,
                    extracted_text=extracted_text,
                    confidence_score=confidence
                )
                db.session.add(text_record)
                
                # Save to conversion history
                conversion = ConversionHistory(
                    filename=filename,
                    original_filename=file.filename,
                    file_type=file.filename.rsplit('.', 1)[1].lower(),
                    conversion_type='ocr_extraction',
                    file_size=os.path.getsize(filepath),
                    status='completed',
                    processed_at=datetime.utcnow()
                )
                db.session.add(conversion)
                db.session.commit()
                
                return render_template('extract_text.html', 
                                     extracted_text=extracted_text, 
                                     confidence=confidence,
                                     filename=file.filename)
            else:
                flash('No text could be extracted from the image', 'warning')
                return redirect(request.url)
                
        except Exception as e:
            app.logger.error(f'OCR extraction error: {str(e)}')
            flash(f'Error extracting text: {str(e)}', 'error')
            return redirect(request.url)
    
    flash('Invalid file type. Please upload an image or PDF file.', 'error')
    return redirect(request.url)

@app.route('/save-text', methods=['POST'])
def save_text():
    """Save extracted text to file"""
    text_content = request.form.get('text_content')
    original_filename = request.form.get('original_filename', 'extracted_text')
    
    if not text_content:
        flash('No text to save', 'error')
        return redirect(url_for('extract_text_page'))
    
    try:
        # Generate filename for text file
        text_filename = f"{original_filename.rsplit('.', 1)[0]}_extracted.txt"
        text_filepath = os.path.join(app.config['PROCESSED_FOLDER'], text_filename)
        
        # Ensure processed directory exists
        os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
        
        # Save text to file
        with open(text_filepath, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        flash('Text saved successfully!', 'success')
        return send_file(text_filepath, as_attachment=True, download_name=text_filename)
        
    except Exception as e:
        app.logger.error(f'Error saving text: {str(e)}')
        flash(f'Error saving text: {str(e)}', 'error')
        return redirect(url_for('extract_text_page'))

@app.route('/my-files')
def my_files():
    """Display user's uploaded files"""
    files = ConversionHistory.query.order_by(ConversionHistory.created_at.desc()).all()
    return render_template('my_files.html', files=files)

@app.route('/history')
def history():
    """Display conversion history"""
    history_records = ConversionHistory.query.order_by(ConversionHistory.created_at.desc()).all()
    return render_template('history.html', history=history_records)

@app.route('/convert')
def convert_page():
    """File conversion page"""
    return render_template('convert.html')

@app.route('/convert', methods=['POST'])
def convert_file():
    """Handle file conversion using LibreOffice"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(request.url)
    
    conversion_type = request.form.get('conversion_type', 'pdf')
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            # Ensure directories exist
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
            file.save(filepath)
            
            # Convert file using LibreOffice
            output_filename = convert_with_libreoffice(filepath, conversion_type)
            
            if output_filename:
                # Save to database
                conversion = ConversionHistory(
                    filename=output_filename,
                    original_filename=file.filename,
                    file_type=file.filename.rsplit('.', 1)[1].lower(),
                    conversion_type=f'convert_to_{conversion_type}',
                    file_size=os.path.getsize(os.path.join(app.config['PROCESSED_FOLDER'], output_filename)),
                    status='completed',
                    processed_at=datetime.utcnow()
                )
                db.session.add(conversion)
                db.session.commit()
                
                flash(f'File converted to {conversion_type.upper()} successfully!', 'success')
                
                # Return converted file
                return send_file(
                    os.path.join(app.config['PROCESSED_FOLDER'], output_filename),
                    as_attachment=True,
                    download_name=f"{file.filename.rsplit('.', 1)[0]}.{conversion_type}"
                )
            else:
                flash('Error converting file', 'error')
                return redirect(request.url)
                
        except Exception as e:
            app.logger.error(f'File conversion error: {str(e)}')
            flash(f'Error converting file: {str(e)}', 'error')
            return redirect(request.url)
    
    flash('Invalid file type. Please upload PDF, DOC, DOCX, or TXT files.', 'error')
    return redirect(request.url)

def convert_with_libreoffice(input_file, output_format):
    """Convert file using LibreOffice"""
    try:
        output_dir = app.config['PROCESSED_FOLDER']
        
        # LibreOffice command
        cmd = [
            'libreoffice',
            '--headless',
            '--convert-to', output_format,
            '--outdir', output_dir,
            input_file
        ]
        
        # Run conversion
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            # Generate output filename
            base_name = os.path.basename(input_file).rsplit('.', 1)[0]
            output_filename = f"{base_name}.{output_format}"
            
            # Check if file was created
            output_path = os.path.join(output_dir, output_filename)
            if os.path.exists(output_path):
                return output_filename
            else:
                app.logger.error(f'Output file not found: {output_path}')
                return None
        else:
            app.logger.error(f'LibreOffice conversion failed: {result.stderr}')
            return None
            
    except subprocess.TimeoutExpired:
        app.logger.error('LibreOffice conversion timed out')
        return None
    except Exception as e:
        app.logger.error(f'LibreOffice conversion error: {str(e)}')
        return None

@app.route('/settings')
def settings():
    """Display settings page"""
    return render_template('settings.html')

@app.route('/api/stats')
def api_stats():
    """API endpoint for getting statistics"""
    stats = get_stats()
    return jsonify(stats)

@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum file size is 16MB.', 'error')
    return redirect(url_for('upload_page'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    app.logger.error(f'Internal server error: {str(e)}')
    return render_template('500.html'), 500
