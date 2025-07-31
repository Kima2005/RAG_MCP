import os
import uuid
import json
from dotenv import load_dotenv
import chromadb
from openai import OpenAI

# Load .env để lấy API key
load_dotenv()

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="products")

# OpenAI embedding client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str) -> list[float]:
    """Get OpenAI embedding"""
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def build_information(product: dict) -> str:
    """Ghép các trường lại thành chuỗi thông tin duy nhất để embedding"""
    parts = []
    if product.get("title"):
        parts.append(product["title"])
    if product.get("price"):
        parts.append(f"Giá: {product['price']}")
    if product.get("content"):
        content = product["content"].replace("\n", " ").replace("<br>", " ")
        parts.append(content)
    return ". ".join(parts)

# Đọc dữ liệu từ file JSON
with open('data/output.json', 'r', encoding="utf8") as f:
    products = json.load(f)  

# Xử lý và lưu vào ChromaDB
for product in products:
    information = build_information(product)
    embedding = get_embedding(information)
    doc_id = str(uuid.uuid4())

    metadata = {
        "title": product.get("title", ""),
        "price": product.get("price", ""),
        "url": product.get("url", "")
    }

    collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[information],
        metadatas=[metadata]
    )

print(f"✅ Đã lưu {len(products)} sản phẩm vào ChromaDB.")
