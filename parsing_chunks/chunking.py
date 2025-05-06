import os
import io
import openai
import boto3
from pinecone import Pinecone
from dotenv import load_dotenv

# 📥 Load environment variables
load_dotenv()

# 🔐 Credentials
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX")
AWS_BUCKET = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# 🔑 Set API Key
openai.api_key = OPENAI_API_KEY

# 📦 Init S3
s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# 📌 Init Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# 📏 Count tokens (rough estimate)
def token_count(text: str) -> int:
    return len(text.split())

# 🔁 Recursive splitter
def recursive_split(text, max_tokens=300):
    if token_count(text) <= max_tokens:
        return [text]

    for splitter in ["\n\n", "\n", ". "]:
        parts = text.split(splitter)
        if len(parts) == 1:
            continue

        chunks, current = [], ""
        for part in parts:
            candidate = (current + splitter + part).strip() if current else part.strip()
            if token_count(candidate) <= max_tokens:
                current = candidate
            else:
                if current:
                    chunks.extend(recursive_split(current, max_tokens))
                current = part.strip()
        if current:
            chunks.extend(recursive_split(current, max_tokens))
        return chunks

    return [text]  # fallback chunk

# 📥 Load markdown from S3
def load_md_from_s3(file_name: str) -> str:
    key = f"Markdown_Conversions/{file_name}/{file_name}.md"
    try:
        response = s3.get_object(Bucket=AWS_BUCKET, Key=key)
        return response["Body"].read().decode("utf-8")
    except Exception as e:
        print(f"❌ Failed to load {key} from S3:", e)
        return ""

# 🧠 Get OpenAI embedding
def get_embedding(text: str) -> list:
    try:
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print("❌ Error embedding text:", e)
        return []

# 🔼 Upload to Pinecone
def upload_chunks_to_pinecone(chunks, file_name):
    batch = []
    for idx, chunk in enumerate(chunks):
        chunk_id = f"{file_name}_{idx}"
        embedding = get_embedding(chunk)
        if not embedding:
            continue

        metadata = {
            "source": file_name,
            "chunk_index": idx,
            "text": chunk
        }

        batch.append((chunk_id, embedding, metadata))

        if len(batch) >= 20:
            index.upsert(vectors=batch)
            print(f"🔼 Uploaded {len(batch)} chunks...")
            batch.clear()

    if batch:
        index.upsert(vectors=batch)
        print(f"🔼 Uploaded final {len(batch)} chunks for {file_name}.")

# 🚀 Process a file
def process_file(file_name: str):
    print(f"\n📄 Processing: {file_name}")
    markdown = load_md_from_s3(file_name)
    if not markdown:
        return

    chunks = recursive_split(markdown)
    print(f"🧱 Total chunks created: {len(chunks)}")
    upload_chunks_to_pinecone(chunks, file_name)

# 🏁 Main
if __name__ == "__main__":
    files_to_process = [
        "cdc1",
        "cdc2",
        "who1",
        "who2",
        "sdoh_strategies1",
        "sdoh_strategies2",
        "additional",
        "additional2"
    ]

    for fname in files_to_process:
        process_file(fname)
