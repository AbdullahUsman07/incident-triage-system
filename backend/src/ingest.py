import os
import glob
from dotenv import load_dotenv
from pathlib import Path
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from chunker import LogAwareChunker

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "incident-triage")

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is missing from environment variables!")

print("Loading embedding model (all-MiniLM-L6-v2)...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Connecting to Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)

existing_indexes = [idx.name for idx in pc.list_indexes()]

# Create index if it does not exists
if INDEX_NAME not in existing_indexes:
    print(f"Creating serverless Pinecone index '{INDEX_NAME}'...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(INDEX_NAME)
chunker = LogAwareChunker()

# read and adaptively chunk all 20 Post-Mortems
post_mortem_files = glob.glob("data/post_mortems/*.md")

if not post_mortem_files:
    raise FileNotFoundError("No .md files found in data/post_mortems/! Run cleanup_and_replace.py first.")

print(f"\nProcessing {len(post_mortem_files)} post-mortem files...")
all_chunks = []

for filepath in post_mortem_files:
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Process file through our unified frontmatter + markdown chunker
    file_chunks = chunker.chunk_post_mortem(content, filename)
    all_chunks.extend(file_chunks)

print(f"Extracted a total of {len(all_chunks)} context chunks across all post-mortems.")

# Generate Vector Embeddings and Prepare Payload
print("\nGenerating dense vector embeddings...")
vectors_to_upsert = []

for chunk in all_chunks:
    # Convert chunk text to 384-dimensional vector
    embedding = model.encode(chunk["text"]).tolist()
    
    vectors_to_upsert.append({
        "id": chunk["id"],
        "values": embedding,
        "metadata": {
            "text": chunk["text"],
            "title": chunk["metadata"]["title"],
            "company": chunk["metadata"]["company"],
            "summary": chunk["metadata"].get("summary", ""),
            "source": chunk["metadata"]["source"],
            "type": chunk["metadata"]["type"],
            "chunk_index": chunk["metadata"]["chunk_index"]
        }
    })

# upsert to pinecone in the batch of 50
BATCH_SIZE = 50
print(f"\nUpserting vectors to Pinecone index '{INDEX_NAME}' in batches of {BATCH_SIZE}...")

for i in range(0, len(vectors_to_upsert), BATCH_SIZE):
    batch = vectors_to_upsert[i : i + BATCH_SIZE]
    index.upsert(vectors=batch)
    print(f"  ├─ Upserted vectors {i + 1} to {min(i + BATCH_SIZE, len(vectors_to_upsert))}")

print(f"\nSUCCESS: All {len(vectors_to_upsert)} vectors successfully indexed in Pinecone!")

