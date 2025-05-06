import boto3
import os
import sys
from dotenv import load_dotenv

# Load AWS credentials from .env file
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
RAW_PDF_PREFIX = "Raw_Pdfs/"

# Initialize the S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

def upload_pdf_to_s3(file_path):
    """Uploads a single PDF file to the Raw_Pdfs/ folder in the S3 bucket."""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    if not file_path.lower().endswith(".pdf"):
        print(f"❌ Skipped (not a PDF): {file_path}")
        return

    file_name = os.path.basename(file_path)
    s3_key = f"{RAW_PDF_PREFIX}{file_name}"

    try:
        s3_client.upload_file(file_path, BUCKET_NAME, s3_key)
        print(f"✅ Uploaded: {file_path} → s3://{BUCKET_NAME}/{s3_key}")
    except Exception as e:
        print(f"❌ Failed to upload {file_path}: {e}")

if __name__ == "__main__":
    # Get file path from user input
    if len(sys.argv) != 2:
        print("Usage: python pdf_to_s3.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    upload_pdf_to_s3(pdf_path)
