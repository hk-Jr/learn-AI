from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

def test_full_e2e_rag_workflow():
    sample_dir = Path(__file__).resolve().parent.parent.parent / "data" / "sample_documents"
    assert sample_dir.exists(), "Sample documents directory missing"

    pdf_file = sample_dir / "Deep_Learning_Architectures.pdf"
    docx_file = sample_dir / "Quantum_Computing_Principles.docx"
    txt_file = sample_dir / "Mars_Exploration_Rover_Mission.txt"

    # 1. Upload PDF
    with open(pdf_file, "rb") as f:
        res = client.post("/api/documents/upload", files=[("files", (pdf_file.name, f, "application/pdf"))])
    assert res.status_code == 200, res.text
    pdf_doc = res.json()[0]
    assert pdf_doc["status"] == "indexed"
    assert pdf_doc["total_pages"] == 2
    assert pdf_doc["total_chunks"] >= 2

    # 2. Upload DOCX
    with open(docx_file, "rb") as f:
        res = client.post("/api/documents/upload", files=[("files", (docx_file.name, f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))])
    assert res.status_code == 200, res.text
    docx_doc = res.json()[0]
    assert docx_doc["status"] == "indexed"
    assert docx_doc["total_chunks"] >= 1

    # 3. Upload TXT
    with open(txt_file, "rb") as f:
        res = client.post("/api/documents/upload", files=[("files", (txt_file.name, f, "text/plain"))])
    assert res.status_code == 200, res.text
    txt_doc = res.json()[0]
    assert txt_doc["status"] == "indexed"

    # 4. Verify Document listing
    docs_res = client.get("/api/documents")
    assert docs_res.status_code == 200
    docs = docs_res.json()
    assert len(docs) >= 3

    # 5. Inspect single document chunks
    doc_detail = client.get(f"/api/documents/{pdf_doc['id']}")
    assert doc_detail.status_code == 200
    detail_data = doc_detail.json()
    assert len(detail_data["chunks"]) >= 2
    assert detail_data["chunks"][0]["page_number"] in [1, 2]

    # 6. Ask question from PDF ("Attention Is All You Need")
    q1_res = client.post("/api/chat/ask", json={
        "question": "Who introduced the Transformer model and what attention mechanism does it rely on?",
        "top_k": 3
    })
    assert q1_res.status_code == 200
    q1_data = q1_res.json()
    assert "vaswani" in q1_data["answer"].lower() or "attention" in q1_data["answer"].lower()
    assert len(q1_data["citations"]) > 0
    assert any("Deep_Learning_Architectures.pdf" in c["document_name"] for c in q1_data["citations"])

    # 7. Ask question from DOCX ("Shor's algorithm")
    q2_res = client.post("/api/chat/ask", json={
        "question": "What algorithm factors integers in polynomial time and threatens RSA encryption?",
        "top_k": 3
    })
    assert q2_res.status_code == 200
    q2_data = q2_res.json()
    assert "shor" in q2_data["answer"].lower()
    assert any("Quantum_Computing_Principles.docx" in c["document_name"] for c in q2_data["citations"])

    # 8. Ask question from TXT ("Ingenuity helicopter flights")
    q3_res = client.post("/api/chat/ask", json={
        "question": "How many flights did the Ingenuity Mars Helicopter complete?",
        "top_k": 3
    })
    assert q3_res.status_code == 200
    q3_data = q3_res.json()
    assert "72" in q3_data["answer"]
    assert any("Mars_Exploration_Rover_Mission.txt" in c["document_name"] for c in q3_data["citations"])

    # 9. Ask completely unrelated question (Hallucination & Fabrication test)
    q_unrelated = client.post("/api/chat/ask", json={
        "question": "What is the average lifespan of a giant Galapagos tortoise in the wild?",
        "top_k": 3,
        "similarity_threshold": 0.4
    })
    assert q_unrelated.status_code == 200
    unrelated_data = q_unrelated.json()
    assert "do not contain sufficient information" in unrelated_data["answer"].lower()

    # 10. Test conversation persistence
    conv_id = q1_data["conversation_id"]
    conv_res = client.get(f"/api/chat/conversations/{conv_id}")
    assert conv_res.status_code == 200
    conv_obj = conv_res.json()
    assert len(conv_obj["messages"]) >= 2  # user + assistant

    # 11. Test Semantic Search endpoint
    search_res = client.post("/api/search", json={
        "query": "superposition and qubits in quantum computing",
        "top_k": 3
    })
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["total_results"] > 0
    assert any("Quantum_Computing_Principles.docx" in r["document_name"] for r in search_data["results"])

    # 12. Test Reprocess Document
    reprocess_res = client.post(f"/api/documents/{pdf_doc['id']}/reprocess")
    assert reprocess_res.status_code == 200
    assert reprocess_res.json()["status"] == "indexed"

    # 13. Test Delete Document
    del_res = client.delete(f"/api/documents/{docx_doc['id']}")
    assert del_res.status_code == 200
    # Verify it is gone
    check_del = client.get(f"/api/documents/{docx_doc['id']}")
    assert check_del.status_code == 404
