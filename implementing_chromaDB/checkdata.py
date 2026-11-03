import chromadb
import json

client = chromadb.PersistentClient(path="./my_local_chroma_db")
collection = client.get_collection("personal_knowledge_base")

# Fetch data without the heavy vector embeddings
data = collection.get(
    limit=5, # Change this to view more records
    include=["documents", "metadatas"]
)

for i in range(len(data['ids'])):
    print(f"\n{'='*40}")
    print(f"ID: {data['ids'][i]}")
    print(f"METADATA: {json.dumps(data['metadatas'][i], indent=2)}")
    print(f"\nDOCUMENT TEXT:\n{data['documents'][i]}")
    print(f"{'='*40}")