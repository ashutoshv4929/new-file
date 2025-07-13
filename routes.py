import os
import uuid
import subprocess
import shutil
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
from app import app
from models import ConversionHistory, ExtractedText, AppSettings
from extensions import db

# Import services
try:
    from services.ocr_service import OCRService
except ImportError:
    OCRService = None

try:
    from services.cloud_storage import CloudStorageService
except ImportError:
    CloudStorageService = None
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

# PDF Tools Routes

@app.route('/merge-pdf')
def merge_pdf_page():
    """Merge PDF page"""
    return render_template('pdf_tools/merge.html')

@app.route('/split-pdf')
def split_pdf_page():
    """Split PDF page"""
    return render_template('pdf_tools/split.html')

@app.route('/compress-pdf')
def compress_pdf_page():
    """Compress PDF page"""
    return render_template('pdf_tools/compress.html')

def check_ghostscript_installed():
    """Check if Ghostscript is installed and accessible"""
    gs_path = shutil.which('gs')
    if not gs_path:
        return False, "Ghostscript (gs) is not installed or not in PATH"
    
    try:
        result = subprocess.run(
            ['gs', '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return True, f"Ghostscript version: {result.stdout.strip()}"
        return False, f"Ghostscript check failed: {result.stderr or 'Unknown error'}"
    except Exception as e:
        return False, f"Error checking Ghostscript: {str(e)}"

@app.route('/compress-pdf', methods=['POST'])
def compress_pdf():
    """Handle PDF compression with quality level using Ghostscript"""
    import os
    import tempfile
    import subprocess
    import shutil
    import sys
    from io import BytesIO
    
    if 'file' not in request.files:
        flash('No PDF file selected', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    if not file or not file.filename.lower().endswith('.pdf'):
        flash('Please select a valid PDF file', 'error')
        return redirect(request.url)
    
    # Get compression level (1-100)
    try:
        compression_level = int(request.form.get('compression_level', 50))
        compression_level = max(1, min(100, compression_level))
    except (ValueError, TypeError):
        compression_level = 50
    
    # Check if Ghostscript is installed and accessible
    gs_installed, gs_message = check_ghostscript_installed()
    if not gs_installed:
        app.logger.error(f"Ghostscript check failed: {gs_message}")
        flash('PDF compression is not available: Ghostscript is not properly installed', 'error')
        return redirect(request.url)
    
    app.logger.info(gs_message)  # Log the Ghostscript version
    
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_input:
            file.save(temp_input.name)
            input_path = temp_input.name
        
        # Create a temporary output file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_output:
            output_path = temp_output.name
        
        try:
            # Map compression level to Ghostscript settings
            # Higher compression level = more aggressive compression
            if compression_level > 80:  # High compression (smaller file, lower quality)
                pdf_settings = '/screen'  # 72 dpi - lowest quality, smallest size
            elif compression_level > 50:  # Medium compression
                pdf_settings = '/ebook'   # 150 dpi - good balance
            else:  # Low compression (better quality, larger file)
                pdf_settings = '/printer' # 300 dpi - high quality
            
            # Build Ghostscript command
            gs_command = [
                'gs',
                '-sDEVICE=pdfwrite',
                f'-dPDFSETTINGS={pdf_settings}',
                '-dCompatibilityLevel=1.5',
                '-dNOPAUSE',
                '-dQUIET',
                '-dBATCH',
                '-dAutoRotatePages=/None',
                '-sColorConversionStrategy=/RGB',
                '-sProcessColorModel=DeviceRGB',
                f'-sOutputFile={output_path}',
                input_path
            ]
            
            # Log the Ghostscript command for debugging
            app.logger.info(f"Executing Ghostscript command: {' '.join(gs_command)}")
            
            # Execute Ghostscript with full error capture
            try:
                result = subprocess.run(
                    gs_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=60,  # 60 seconds timeout
                    check=True   # Raises CalledProcessError on non-zero return code
                )
                
                # Log the full Ghostscript output for debugging
                app.logger.debug(f"Ghostscript stdout: {result.stdout}")
                app.logger.debug(f"Ghostscript stderr: {result.stderr}")
                
                # Check if output file was created and has content
                if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                    error_msg = "Ghostscript did not generate any output"
                    app.logger.error(error_msg)
                    raise Exception(f"PDF compression failed: {error_msg}")
                
                # Read the compressed PDF into memory
                with open(output_path, 'rb') as f:
                    output = BytesIO(f.read())
                    output.seek(0)
                    
                # Verify the output is a valid PDF
                if output.getbuffer().nbytes < 4 or output.read(4) != b'%PDF':
                    error_msg = "Output is not a valid PDF file"
                    app.logger.error(error_msg)
                    raise Exception(f"PDF compression failed: {error_msg}")
                output.seek(0)  # Reset position after validation
                    
            except subprocess.TimeoutExpired:
                raise Exception("PDF compression timed out (60 seconds)")
                
        except Exception as e:
            app.logger.error(f"Error during PDF compression: {str(e)}")
            raise
            
        finally:
            # Clean up temporary files
            try:
                if os.path.exists(input_path):
                    os.unlink(input_path)
                if os.path.exists(output_path):
                    os.unlink(output_path)
            except Exception as e:
                app.logger.error(f"Error cleaning up temporary files: {str(e)}")
        
        # Create a unique filename
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}_compressed.pdf"
        
        # Create processed directory if it doesn't exist
        processed_dir = os.path.join(app.root_path, 'static', 'processed')
        os.makedirs(processed_dir, exist_ok=True)
        
        output_path = os.path.join(processed_dir, output_filename)
        
        # Save to disk
        with open(output_path, 'wb') as f:
            f.write(output.getvalue())
        
        # Log the conversion
        conversion = ConversionHistory(
            filename=output_filename,
            original_filename=file.filename,
            file_type='pdf',
            conversion_type='compress_pdf',
            file_size=os.path.getsize(output_path),
            status='completed',
            processed_at=datetime.utcnow()
        )
        db.session.add(conversion)
        db.session.commit()
        
        # Return the compressed file
        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/pdf'
        )
                
    except Exception as e:
        app.logger.error(f'Error compressing PDF: {str(e)}')
        flash(f'Error compressing PDF: {str(e)}', 'error')
        return redirect(request.url)

@app.route('/pdf-to-images')
def pdf_to_images_page():
    """PDF to Images page"""
    return render_template('pdf_tools/pdf_to_images.html')

@app.route('/images-to-pdf')
def images_to_pdf_page():
    """Images to PDF page"""
    return render_template('pdf_tools/images_to_pdf.html')

@app.route('/merge-pdf', methods=['POST'])
def merge_pdf():
    """Handle PDF merging"""
    from PyPDF2 import PdfMerger
    
    files = request.files.getlist('files')
    if not files or len(files) < 2:
        flash('Please select at least 2 PDF files to merge', 'error')
        return redirect(request.url)
    
    try:
        merger = PdfMerger()
        temp_files = []
        
        # Save uploaded files temporarily
        for file in files:
            if file and file.filename.lower().endswith('.pdf'):
                filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                merger.append(filepath)
                temp_files.append(filepath)
        
        # Create merged PDF
        merged_filename = f"merged_{uuid.uuid4().hex[:8]}.pdf"
        merged_path = os.path.join(app.config['PROCESSED_FOLDER'], merged_filename)
        
        os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
        merger.write(merged_path)
        merger.close()
        
        # Clean up temp files
        for temp_file in temp_files:
            os.remove(temp_file)
        
        # Save to database
        conversion = ConversionHistory(
            filename=merged_filename,
            original_filename='merged_pdf',
            file_type='pdf',
            conversion_type='merge_pdf',
            file_size=os.path.getsize(merged_path),
            status='completed',
            processed_at=datetime.utcnow()
        )
        db.session.add(conversion)
        db.session.commit()
        
        flash('PDFs merged successfully!', 'success')
        return send_file(merged_path, as_attachment=True, download_name='merged.pdf')
        
    except Exception as e:
        app.logger.error(f'PDF merge error: {str(e)}')
        flash(f'Error merging PDFs: {str(e)}', 'error')
        return redirect(request.url)

@app.route('/split-pdf', methods=['POST'])
def split_pdf():
    """Handle PDF splitting"""
    from PyPDF2 import PdfReader, PdfWriter
    import zipfile
    
    if 'file' not in request.files:
        flash('No PDF file selected', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    if not file or not file.filename.lower().endswith('.pdf'):
        flash('Please select a PDF file', 'error')
        return redirect(request.url)
    
    try:
        # Save uploaded file
        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Split PDF
        reader = PdfReader(filepath)
        output_dir = os.path.join(app.config['PROCESSED_FOLDER'], f"split_{uuid.uuid4().hex[:8]}")
        os.makedirs(output_dir, exist_ok=True)
        
        page_files = []
        for page_num in range(len(reader.pages)):
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num])
            
            page_filename = f"page_{page_num + 1}.pdf"
            page_path = os.path.join(output_dir, page_filename)
            
            with open(page_path, 'wb') as output_file:
                writer.write(output_file)
            page_files.append(page_path)
        
        # Create zip file
        zip_filename = f"split_pages_{uuid.uuid4().hex[:8]}.zip"
        zip_path = os.path.join(app.config['PROCESSED_FOLDER'], zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for page_file in page_files:
                zip_file.write(page_file, os.path.basename(page_file))
        
        # Clean up
        os.remove(filepath)
        for page_file in page_files:
            os.remove(page_file)
        os.rmdir(output_dir)
        
        # Save to database
        conversion = ConversionHistory(
            filename=zip_filename,
            original_filename=file.filename,
            file_type='pdf',
            conversion_type='split_pdf',
            file_size=os.path.getsize(zip_path),
            status='completed',
            processed_at=datetime.utcnow()
        )
        db.session.add(conversion)
        db.session.commit()
        
        flash('PDF split successfully!', 'success')
        return send_file(zip_path, as_attachment=True, download_name='split_pages.zip')
        
    except Exception as e:
        app.logger.error(f'PDF split error: {str(e)}')
        flash(f'Error splitting PDF: {str(e)}', 'error')
        return redirect(request.url)

@app.route('/pdf-to-images', methods=['POST'])
def pdf_to_images():
    """Convert PDF pages to images"""
    import pdf2image
    import zipfile
    
    if 'file' not in request.files:
        flash('No PDF file selected', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    if not file or not file.filename.lower().endswith('.pdf'):
        flash('Please select a PDF file', 'error')
        return redirect(request.url)
    
    try:
        # Save uploaded file
        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Convert PDF to images
        images = pdf2image.convert_from_path(filepath)
        output_dir = os.path.join(app.config['PROCESSED_FOLDER'], f"images_{uuid.uuid4().hex[:8]}")
        os.makedirs(output_dir, exist_ok=True)
        
        image_files = []
        for i, image in enumerate(images):
            image_filename = f"page_{i + 1}.png"
            image_path = os.path.join(output_dir, image_filename)
            image.save(image_path, 'PNG')
            image_files.append(image_path)
        
        # Create zip file
        zip_filename = f"pdf_images_{uuid.uuid4().hex[:8]}.zip"
        zip_path = os.path.join(app.config['PROCESSED_FOLDER'], zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for image_file in image_files:
                zip_file.write(image_file, os.path.basename(image_file))
        
        # Clean up
        os.remove(filepath)
        for image_file in image_files:
            os.remove(image_file)
        os.rmdir(output_dir)
        
        # Save to database
        conversion = ConversionHistory(
            filename=zip_filename,
            original_filename=file.filename,
            file_type='pdf',
            conversion_type='pdf_to_images',
            file_size=os.path.getsize(zip_path),
            status='completed',
            processed_at=datetime.utcnow()
        )
        db.session.add(conversion)
        db.session.commit()
        
        flash('PDF converted to images successfully!', 'success')
        return send_file(zip_path, as_attachment=True, download_name='pdf_images.zip')
        
    except Exception as e:
        app.logger.error(f'PDF to images error: {str(e)}')
        flash(f'Error converting PDF to images: {str(e)}', 'error')
        return redirect(request.url)

@app.route('/images-to-pdf', methods=['POST'])
def images_to_pdf():
    """Convert images to PDF"""
    from PIL import Image
    
    files = request.files.getlist('files')
    if not files:
        flash('Please select image files', 'error')
        return redirect(request.url)
    
    try:
        images = []
        temp_files = []
        
        for file in files:
            if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Open and convert image
                image = Image.open(filepath)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                images.append(image)
                temp_files.append(filepath)
        
        if not images:
            flash('No valid image files found', 'error')
            return redirect(request.url)
        
        # Create PDF
        pdf_filename = f"images_to_pdf_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = os.path.join(app.config['PROCESSED_FOLDER'], pdf_filename)
        
        os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
        images[0].save(pdf_path, save_all=True, append_images=images[1:])
        
        # Clean up temp files
        for temp_file in temp_files:
            os.remove(temp_file)
        
        # Save to database
        conversion = ConversionHistory(
            filename=pdf_filename,
            original_filename='images_to_pdf',
            file_type='pdf',
            conversion_type='images_to_pdf',
            file_size=os.path.getsize(pdf_path),
            status='completed',
            processed_at=datetime.utcnow()
        )
        db.session.add(conversion)
        db.session.commit()
        
        flash('Images converted to PDF successfully!', 'success')
        return send_file(pdf_path, as_attachment=True, download_name='images.pdf')
        
    except Exception as e:
        app.logger.error(f'Images to PDF error: {str(e)}')
        flash(f'Error converting images to PDF: {str(e)}', 'error')
        return redirect(request.url)

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
