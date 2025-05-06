# ✅ FILE: parsing_chunks/mistral.py

import os
import io
import base64
import logging
from dotenv import load_dotenv
from tempfile import NamedTemporaryFile
from PIL import Image
from mistralai import Mistral
from mistralai import DocumentURLChunk
from mistralai.models import OCRResponse
import boto3

# Load environment variables
load_dotenv()

AWS_BUCKET = os.getenv("AWS_BUCKET_NAME")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Init S3 client
s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

logging.basicConfig(filename="mistral_conversion.log", level=logging.INFO, format="%(message)s")

def upload_to_s3(bucket, key, data_bytes):
    """Upload binary data to S3 under the given key"""
    s3.upload_fileobj(io.BytesIO(data_bytes), bucket, key)
    logging.info(f"✅ Uploaded to s3://{bucket}/{key}")

def replace_image_references(md: str, images: dict, base_path: str) -> str:
    """Replaces in-markdown image references with public S3 URLs after uploading"""
    for img_id, img_base64 in images.items():
        img_data = base64.b64decode(img_base64.split(",")[-1])

        image_filename = f"{img_id}.png"
        s3_key = f"{base_path}/Images/{image_filename}"

        image = Image.open(io.BytesIO(img_data)).convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        upload_to_s3(AWS_BUCKET, s3_key, buffer.read())

        image_url = f"https://{AWS_BUCKET}.s3.amazonaws.com/{s3_key}"
        md = md.replace(f"![{img_id}]({img_id})", f"![{image_filename}]({image_url})")

    return md

def mistral_pdf_to_md(pdf_bytes: bytes, file_name: str):
    """Run Mistral OCR on PDF bytes and upload Markdown + images to S3"""
    client = Mistral(api_key=MISTRAL_API_KEY)
    pdf_bytes_io = io.BytesIO(pdf_bytes)

    try:
        print("🔁 Uploading PDF to Mistral OCR...")
        uploaded = client.files.upload(file={"file_name": "temp.pdf", "content": pdf_bytes_io.read()}, purpose="ocr")
        print(f"✅ Upload complete: file_id = {uploaded.id}")
        
        signed_url = client.files.get_signed_url(file_id=uploaded.id, expiry=2)
        print(f"🔗 Signed URL fetched: {signed_url.url}")

        result = client.ocr.process(
            document=DocumentURLChunk(document_url=signed_url.url),
            model="mistral-ocr-latest",
            include_image_base64=True
        )
        print("✅ OCR processing successful")
    except Exception as e:
        print("❌ Error during Mistral processing:", str(e))
        raise e

    base_path = f"Markdown_Conversions/{file_name}"
    full_markdown = ""
    image_counter = 0

    for page in result.pages:
        images = {img.id: img.image_base64 for img in page.images}
        md_with_links = replace_image_references(page.markdown, images, base_path)
        full_markdown += md_with_links + "\n\n"
        image_counter += len(images)

    md_key = f"{base_path}/{file_name}.md"
    upload_to_s3(AWS_BUCKET, md_key, full_markdown.encode("utf-8"))

    return {
        "markdown_s3_path": md_key,
        "images_uploaded": image_counter,
        "preview_url": f"https://{AWS_BUCKET}.s3.amazonaws.com/{md_key}"
    }

def process_pdf_from_s3(file_name: str):
    """Download PDF from Raw_Pdfs/ in S3 and send to Mistral"""
    s3_key = f"Raw_Pdfs/{file_name}"
    file_name_no_ext = os.path.splitext(file_name)[0]
    print(f"📥 Downloading s3://{AWS_BUCKET}/{s3_key}")

    try:
        response = s3.get_object(Bucket=AWS_BUCKET, Key=s3_key)
        pdf_bytes = response["Body"].read()
    except Exception as e:
        print(f"❌ Failed to download {file_name} from S3:", str(e))
        return

    result = mistral_pdf_to_md(pdf_bytes, file_name_no_ext)

    print("✅ Markdown and images stored:")
    print(f"📝 Markdown URL: {result['preview_url']}")
    print(f"🖼️ Images uploaded: {result['images_uploaded']}")

if __name__ == "__main__":
    # List your Raw_Pdfs filenames here (or fetch dynamically)
    pdf_files = [
        "cdc1.pdf",
        "cdc2.pdf",
        "sdoh_strategies1.pdf",
        "sdoh_strategies2.pdf",
        "who1.pdf",
        "additional.pdf",
        "who2.pdf",
        "additional2.pdf"
    ]

    for pdf in pdf_files:
        print(f"\n📄 Processing file: {pdf}")
        process_pdf_from_s3(pdf)
