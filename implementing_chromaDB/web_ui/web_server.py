import http.server
import socketserver
import json
import urllib.parse
import os
import chromadb

PORT = 5050
HTML_PATH = os.path.join(os.path.dirname(__file__), "index.html")

# Connect to our local persistent ChromaDB first, or fallback to HTTP server
try:
    local_db_path = os.path.join(os.path.dirname(__file__), "..", "my_local_chroma_db")
    client = chromadb.PersistentClient(path=local_db_path)
    print(f"Web UI connected to Persistent ChromaDB at: {local_db_path}")
except Exception as e:
    print(f"Fallback to HTTP Chroma client: {e}")
    client = chromadb.HttpClient(host="localhost", port=8000)

class ChromaAtlasHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        params = urllib.parse.parse_qs(parsed_url.query)

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(HTML_PATH, "rb") as f:
                self.wfile.write(f.read())
            return

        if path == "/api/collections":
            try:
                cols = client.list_collections()
                col_data = []
                for c in cols:
                    col_data.append({
                        "name": c.name,
                        "count": c.count()
                    })
                self.send_json({"collections": col_data})
            except Exception as e:
                self.send_json({"error": str(e)}, status=500)
            return

        if path == "/api/documents":
            col_name = params.get("collection", [None])[0]
            if not col_name:
                self.send_json({"error": "Missing collection param"}, status=400)
                return
            try:
                col = client.get_collection(col_name)
                data = col.get(include=["documents", "metadatas", "embeddings"])
                self.send_json({
                    "ids": data.get("ids", []),
                    "documents": data.get("documents", []),
                    "metadatas": data.get("metadatas", []),
                    "embeddings": data.get("embeddings", [])
                })
            except Exception as e:
                self.send_json({"error": str(e)}, status=500)
            return

        if path == "/api/query":
            col_name = params.get("collection", [None])[0]
            query_text = params.get("q", [""])[0]
            n_results = int(params.get("n", [5])[0])

            if not col_name or not query_text:
                self.send_json({"error": "Missing query or collection param"}, status=400)
                return

            try:
                col = client.get_collection(col_name)
                data = col.query(query_texts=[query_text], n_results=n_results)
                self.send_json({
                    "ids": data.get("ids", []),
                    "documents": data.get("documents", []),
                    "metadatas": data.get("metadatas", []),
                    "distances": data.get("distances", [])
                })
            except Exception as e:
                self.send_json({"error": str(e)}, status=500)
            return

        self.send_response(404)
        self.end_headers()

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), ChromaAtlasHandler) as httpd:
        print(f" ChromaDB Atlas Studio running at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
