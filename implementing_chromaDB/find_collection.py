import chromadb
client = chromadb.PersistentClient(path="./my_local_chroma_db")
print(client.list_collections())