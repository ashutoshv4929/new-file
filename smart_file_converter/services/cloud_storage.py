import os
import logging
from google.cloud import storage
from google.oauth2 import service_account

class CloudStorageService:
    def __init__(self):
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.bucket_name = os.environ.get("GOOGLE_CLOUD_STORAGE_BUCKET")
        self.client = None
        self.bucket = None
        
        if self.project_id and self.bucket_name:
            try:
                # Initialize the client
                credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
                if credentials_path:
                    credentials = service_account.Credentials.from_service_account_file(credentials_path)
                    self.client = storage.Client(credentials=credentials, project=self.project_id)
                else:
                    # Use default credentials
                    self.client = storage.Client(project=self.project_id)
                
                self.bucket = self.client.bucket(self.bucket_name)
                logging.info(f"Google Cloud Storage initialized for project: {self.project_id}")
            except Exception as e:
                logging.error(f"Failed to initialize Google Cloud Storage: {str(e)}")
                self.client = None
                self.bucket = None
        else:
            logging.warning("Google Cloud Storage not configured - missing project ID or bucket name")
    
    def upload_file(self, local_file_path, remote_file_name):
        """Upload a file to Google Cloud Storage"""
        if not self.client or not self.bucket:
            raise Exception("Google Cloud Storage not properly configured")
        
        try:
            blob = self.bucket.blob(remote_file_name)
            blob.upload_from_filename(local_file_path)
            logging.info(f"File {local_file_path} uploaded to {remote_file_name}")
            return True
        except Exception as e:
            logging.error(f"Error uploading file to Cloud Storage: {str(e)}")
            raise e
    
    def download_file(self, remote_file_name, local_file_path):
        """Download a file from Google Cloud Storage"""
        if not self.client or not self.bucket:
            raise Exception("Google Cloud Storage not properly configured")
        
        try:
            blob = self.bucket.blob(remote_file_name)
            blob.download_to_filename(local_file_path)
            logging.info(f"File {remote_file_name} downloaded to {local_file_path}")
            return True
        except Exception as e:
            logging.error(f"Error downloading file from Cloud Storage: {str(e)}")
            raise e
    
    def delete_file(self, remote_file_name):
        """Delete a file from Google Cloud Storage"""
        if not self.client or not self.bucket:
            raise Exception("Google Cloud Storage not properly configured")
        
        try:
            blob = self.bucket.blob(remote_file_name)
            blob.delete()
            logging.info(f"File {remote_file_name} deleted from Cloud Storage")
            return True
        except Exception as e:
            logging.error(f"Error deleting file from Cloud Storage: {str(e)}")
            raise e
    
    def list_files(self, prefix=None):
        """List files in Google Cloud Storage bucket"""
        if not self.client or not self.bucket:
            raise Exception("Google Cloud Storage not properly configured")
        
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logging.error(f"Error listing files from Cloud Storage: {str(e)}")
            raise e
    
    def get_file_url(self, remote_file_name, expiration_minutes=60):
        """Get a signed URL for a file"""
        if not self.client or not self.bucket:
            raise Exception("Google Cloud Storage not properly configured")
        
        try:
            blob = self.bucket.blob(remote_file_name)
            url = blob.generate_signed_url(
                version="v4",
                expiration=f"{expiration_minutes}m",
                method="GET"
            )
            return url
        except Exception as e:
            logging.error(f"Error generating signed URL: {str(e)}")
            raise e
    
    def is_configured(self):
        """Check if Cloud Storage is properly configured"""
        return self.client is not None and self.bucket is not None
