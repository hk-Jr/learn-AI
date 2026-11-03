import os
import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
import pymupdf
import docx

from app.main import app
from app.database import engine, Base, SessionLocal
from app.services.document_parser import DocumentParser
from app.services.text_chunker import TextChunker
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import vector_store
from app.services.retrieval_engine import retrieval_engine
from app.services.llm_service import LLMService

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield

def test_document_parser_pdf(tmp_path):
    pdf_path = tmp_path / "test_doc.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 72), "Autonomous Artificial Intelligence Agents are revolutionizing modern software engineering by orchestrating multi-agent systems.")
    doc.save(str(pdf_path))
    doc.close()

    pages, total_pages, total_chars = DocumentParser.parse_file(pdf_path, ".pdf")
    assert total_pages == 1
    assert "Autonomous Artificial Intelligence Agents" in pages[0].text
    assert total_chars > 20

def test_document_parser_docx(tmp_path):
    docx_path = tmp_path / "test_doc.docx"
    d = docx.Document()
    d.add_heading("Deep Learning Architecture", level=1)
    d.add_paragraph("Retrieval-Augmented Generation bridges external knowledge with generative language models.")
    d.save(str(docx_path))

    pages, total_pages, total_chars = DocumentParser.parse_file(docx_path, ".docx")
    assert total_pages >= 1
    assert "Retrieval-Augmented Generation" in pages[0].text
    assert total_chars > 20

def test_text_chunking():
    pages = [DocumentParser.clean_text(
        "First section discusses vector databases and embeddings. Second section details semantic search. " * 15
    )]
    from app.services.document_parser import ExtractedPage
    extracted_pages = [ExtractedPage(page_number=1, text=pages[0])]

    chunker = TextChunker(chunk_size=300, chunk_overlap=40)
    chunks = chunker.chunk_pages(extracted_pages)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c.content) <= 450
        assert c.page_number == 1

def test_vector_store_and_retrieval():
    ids = ["test_chunk_1", "test_chunk_2"]
    docs = [
        "Quantum computing utilizes qubits to achieve superposition and entanglement for computational advantage.",
        "Photosynthesis in green plants converts sunlight, water, and carbon dioxide into glucose and oxygen."
    ]
    embed_service = EmbeddingService()
    embeddings = embed_service.embed_texts(docs)
    metas = [
        {"document_id": "doc_quantum", "document_name": "quantum.txt", "page_number": 1, "chunk_index": 0},
        {"document_id": "doc_biology", "document_name": "biology.txt", "page_number": 1, "chunk_index": 1}
    ]

    vector_store.add_chunks(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)

    # Search for quantum
    hits = vector_store.query(
        query_embedding=embed_service.embed_query("How do qubits and superposition work in quantum computing?"),
        top_k=2
    )
    assert len(hits) > 0
    top_hit = hits[0]
    assert "quantum" in top_hit["content"].lower() or "qubit" in top_hit["content"].lower()

def test_grounded_answer_and_refusal():
    context = (
        "[Source 1: Document 'quantum.txt', Page 1, Chunk #0]\n"
        "Quantum computing utilizes qubits to achieve superposition and entanglement for computational advantage."
    )
    # Grounded question
    ans, _ = LLMService.generate_answer(
        question="What does quantum computing utilize?",
        context=context,
        provider="smart_local"
    )
    assert "qubit" in ans.lower() or "superposition" in ans.lower()

    # Out of context question
    ans_unrelated, _ = LLMService.generate_answer(
        question="What is the capital city of Australia?",
        context=context,
        provider="smart_local"
    )
    assert "do not contain sufficient information" in ans_unrelated.lower()

def test_api_workflows(tmp_path):
    # 1. Health check
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    # 2. Upload a test TXT document
    txt_content = b"The Voyager 1 spacecraft was launched by NASA on September 5, 1977 to study the outer Solar System."
    files = [("files", ("voyager.txt", io.BytesIO(txt_content), "text/plain"))]
    upload_res = client.post("/api/documents/upload", files=files)
    assert upload_res.status_code == 200
    uploaded_data = upload_res.json()
    assert len(uploaded_data) == 1
    doc_id = uploaded_data[0]["id"]
    assert uploaded_data[0]["status"] == "indexed"
    assert uploaded_data[0]["total_chunks"] >= 1

    # 3. Ask question via Chat API
    chat_payload = {
        "question": "When was Voyager 1 launched by NASA?",
        "top_k": 3
    }
    chat_res = client.post("/api/chat/ask", json=chat_payload)
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert "1977" in chat_data["answer"] or "september" in chat_data["answer"].lower()
    assert len(chat_data["citations"]) > 0
    assert chat_data["citations"][0]["document_name"] == "voyager.txt"

    # 4. Check dashboard stats
    dash_res = client.get("/api/dashboard/stats")
    assert dash_res.status_code == 200
    stats = dash_res.json()
    assert stats["total_documents"] >= 1
    assert stats["processed_documents"] >= 1
    assert stats["total_questions_asked"] >= 1

    # 5. Check Settings API
    settings_res = client.get("/api/settings")
    assert settings_res.status_code == 200
    assert "chunk_size" in settings_res.json()

def test_prompt_brain_intent_detection():
    from app.services.prompt_brain import PromptBrain, TaskIntent
    assert PromptBrain.detect_intent("Write a python function to implement RAG chunking") == TaskIntent.CODING
    assert PromptBrain.detect_intent("Step-by-step compare and analyze the architectural tradeoffs") == TaskIntent.REASONING
    assert PromptBrain.detect_intent("Draw a flowchart diagram of the document pipeline") == TaskIntent.VISUAL_DIAGRAM
    assert PromptBrain.detect_intent("What is the mission duration?") == TaskIntent.GENERAL_QA

def test_ollama_discovery_endpoint():
    res = client.get("/api/settings/ollama-models")
    assert res.status_code == 200
    data = res.json()
    assert "ollama_url" in data
    assert isinstance(data["available_models"], list)


