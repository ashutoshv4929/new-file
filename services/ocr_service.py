import os
import io
import logging
from google.cloud import vision
from google.oauth2 import service_account
from PIL import Image
import pdf2image

class OCRService:
    def __init__(self):
        self.client = None
        
        try:
            # Initialize Google Cloud Vision client
            credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path:
                credentials = service_account.Credentials.from_service_account_file(credentials_path)
                self.client = vision.ImageAnnotatorClient(credentials=credentials)
            else:
                # Use default credentials
                self.client = vision.ImageAnnotatorClient()
            
            logging.info("Google Cloud Vision API initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Google Cloud Vision API: {str(e)}")
            self.client = None
    
    def extract_text(self, file_path):
        """Extract text from an image or PDF file"""
        if not self.client:
            raise Exception("Google Cloud Vision API not properly configured")
        
        try:
            # Check if file is PDF
            if file_path.lower().endswith('.pdf'):
                return self._extract_text_from_pdf(file_path)
            else:
                return self._extract_text_from_image(file_path)
        except Exception as e:
            logging.error(f"Error extracting text from {file_path}: {str(e)}")
            raise e
    
    def _extract_text_from_image(self, image_path):
        """Extract text from an image file"""
        try:
            # Load image
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Perform text detection
            response = self.client.text_detection(image=image)
            texts = response.text_annotations
            
            if response.error.message:
                raise Exception(f'Google Cloud Vision API error: {response.error.message}')
            
            if texts:
                # The first text annotation contains the entire detected text
                extracted_text = texts[0].description
                # Calculate average confidence
                confidence = sum([vertex.confidence for vertex in texts[0].bounding_poly.vertices if hasattr(vertex, 'confidence')]) / len(texts[0].bounding_poly.vertices) if texts[0].bounding_poly.vertices else 0.0
                
                return extracted_text, confidence
            else:
                return "", 0.0
                
        except Exception as e:
            logging.error(f"Error extracting text from image: {str(e)}")
            raise e
    
    def _extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file by converting to images first"""
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(pdf_path)
            
            all_text = []
            total_confidence = 0.0
            
            for i, image in enumerate(images):
                # Convert PIL Image to bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Create Vision API image object
                vision_image = vision.Image(content=img_byte_arr)
                
                # Perform text detection
                response = self.client.text_detection(image=vision_image)
                texts = response.text_annotations
                
                if response.error.message:
                    raise Exception(f'Google Cloud Vision API error: {response.error.message}')
                
                if texts:
                    page_text = texts[0].description
                    all_text.append(f"--- Page {i+1} ---\n{page_text}")
                    
                    # Calculate confidence for this page
                    page_confidence = sum([vertex.confidence for vertex in texts[0].bounding_poly.vertices if hasattr(vertex, 'confidence')]) / len(texts[0].bounding_poly.vertices) if texts[0].bounding_poly.vertices else 0.0
                    total_confidence += page_confidence
            
            # Combine all text
            full_text = "\n\n".join(all_text) if all_text else ""
            average_confidence = total_confidence / len(images) if images else 0.0
            
            return full_text, average_confidence
            
        except Exception as e:
            logging.error(f"Error extracting text from PDF: {str(e)}")
            raise e
    
    def is_configured(self):
        """Check if OCR service is properly configured"""
        return self.client is not None
    
    def detect_document_text(self, file_path):
        """Detect and extract document text with layout information"""
        if not self.client:
            raise Exception("Google Cloud Vision API not properly configured")
        
        try:
            with io.open(file_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Perform document text detection
            response = self.client.document_text_detection(image=image)
            document = response.full_text_annotation
            
            if response.error.message:
                raise Exception(f'Google Cloud Vision API error: {response.error.message}')
            
            # Extract text with structure
            text_blocks = []
            for page in document.pages:
                for block in page.blocks:
                    block_text = ""
                    for paragraph in block.paragraphs:
                        para_text = ""
                        for word in paragraph.words:
                            word_text = ''.join([symbol.text for symbol in word.symbols])
                            para_text += word_text + " "
                        block_text += para_text + "\n"
                    text_blocks.append(block_text.strip())
            
            return "\n\n".join(text_blocks), document.text
            
        except Exception as e:
            logging.error(f"Error detecting document text: {str(e)}")
            raise e
