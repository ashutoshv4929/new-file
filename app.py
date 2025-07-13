import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from extensions import db, Base

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///smart_converter.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PROCESSED_FOLDER'] = 'static/processed'

# Google Cloud configuration
app.config['GOOGLE_CLOUD_PROJECT'] = os.environ.get("GOOGLE_CLOUD_PROJECT")
app.config['GOOGLE_CLOUD_STORAGE_BUCKET'] = os.environ.get("GOOGLE_CLOUD_STORAGE_BUCKET")

# Initialize the app with the extension
db.init_app(app)

# Import models after db initialization
from models import ConversionHistory, ExtractedText, AppSettings

# Create tables if they don't exist
with app.app_context():
    # Check if tables exist before creating them
    inspector = db.inspect(db.engine)
    existing_tables = inspector.get_table_names()
    
    # Get all table names from models
    table_names = [table.__tablename__ for table in [ConversionHistory, ExtractedText, AppSettings] 
                  if hasattr(table, '__tablename__')]
    
    # Create only missing tables
    missing_tables = [table for table in table_names if table not in existing_tables]
    
    if missing_tables:
        print(f"Creating missing tables: {', '.join(missing_tables)}")
        db.create_all()
    else:
        print("All tables already exist")

# Import routes after db initialization
import routes

if __name__ == '__main__':
    # Create necessary directories if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
    
    # Run the app in debug mode
    app.run(host='0.0.0.0', port=5000, debug=True)
