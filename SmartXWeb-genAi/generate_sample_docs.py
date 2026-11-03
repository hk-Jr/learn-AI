import os
from pathlib import Path
import pymupdf
import docx

SAMPLES_DIR = Path("data/sample_documents")
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

# 1. Generate PDF
pdf_path = SAMPLES_DIR / "Deep_Learning_Architectures.pdf"
doc = pymupdf.open()

# Page 1
page1 = doc.new_page()
p1_text = (
    "DEEP LEARNING ARCHITECTURES AND ATTENTION MECHANISMS\n\n"
    "Section 1: Transformer Architecture Overview\n"
    "The Transformer model, introduced in 2017 by Vaswani et al. in 'Attention Is All You Need', "
    "dispenses with recurrence and convolutions entirely, relying solely on an attention mechanism "
    "known as Scaled Dot-Product Self-Attention. The model utilizes multi-head attention where queries, "
    "keys, and values are projected into multiple subspaces with dimension d_k = 64.\n\n"
    "Section 2: Positional Encoding\n"
    "Because the Transformer contains no recurrence and no convolution, in order for the model to make use "
    "of the order of the sequence, sinusoidal positional encodings are injected into the input embeddings. "
    "The wavelengths form a geometric progression from 2pi to 10000 * 2pi."
)
page1.insert_text((50, 72), p1_text, fontsize=11)

# Page 2
page2 = doc.new_page()
p2_text = (
    "Section 3: Retrieval-Augmented Generation (RAG)\n"
    "Retrieval-Augmented Generation bridges pre-trained parametric memory with non-parametric external knowledge. "
    "In standard RAG architectures, document collections are chunked into contiguous passages of 200 to 500 tokens. "
    "Dense embeddings are generated using bi-encoder networks such as Dense Passage Retrieval (DPR) or MiniLM. "
    "At inference time, cosine similarity ranking identifies top-k context passages which are prepended to the prompt "
    "to enforce grounded generation and prevent hallucinations."
)
page2.insert_text((50, 72), p2_text, fontsize=11)

doc.save(str(pdf_path))
doc.close()
print(f"Generated {pdf_path}")

# 2. Generate DOCX
docx_path = SAMPLES_DIR / "Quantum_Computing_Principles.docx"
d = docx.Document()
d.add_heading("Principles of Quantum Computing and Cryptography", level=0)
d.add_heading("1. Fundamentals of Qubits and Superposition", level=1)
d.add_paragraph(
    "Unlike classical bits which exist deterministically as 0 or 1, quantum bits (qubits) exist in a superposition "
    "of states represented mathematically as |psi> = alpha|0> + beta|1>, where |alpha|^2 + |beta|^2 = 1. "
    "This property allows quantum computers to evaluate vast combinatorial solution spaces simultaneously."
)
d.add_heading("2. Quantum Supremacy and Shor's Algorithm", level=1)
d.add_paragraph(
    "Peter Shor formulated Shor's algorithm in 1994, which factors integers in polynomial time O((log N)^3). "
    "This threatens modern asymmetric cryptography systems including RSA and Elliptic Curve Cryptography (ECC). "
    "Post-Quantum Cryptography (PQC) standards, including lattice-based algorithms like CRYSTALS-Kyber and CRYSTALS-Dilithium, "
    "are currently being adopted by NIST to secure communications against future quantum decryption."
)
d.save(str(docx_path))
print(f"Generated {docx_path}")

# 3. Generate TXT
txt_path = SAMPLES_DIR / "Mars_Exploration_Rover_Mission.txt"
with open(txt_path, "w", encoding="utf-8") as f:
    f.write(
        "MISSION REPORT: PERSEVERANCE MARS ROVER AND INGENUITY HELICOPTER\n\n"
        "1. Mission Overview\n"
        "The Mars 2020 Perseverance rover touched down inside Jezero Crater on February 18, 2021. "
        "The primary mission objectives are seeking signs of ancient habitability and collecting sealed rock core samples "
        "for return to Earth during the future Mars Sample Return campaign.\n\n"
        "2. Scientific Instrumentation\n"
        "Perseverance carries seven primary instruments, including SuperCam for laser-induced breakdown spectroscopy, "
        "PIXL for micro-focus X-ray fluorescence, and MOXIE, which demonstrated the in-situ production of breathable oxygen "
        "from atmospheric carbon dioxide at a rate of approximately 6 grams per hour.\n\n"
        "3. Ingenuity Helicopter Milestones\n"
        "The Ingenuity Mars Helicopter achieved the first powered, controlled aerodynamic flight on another planet "
        "on April 19, 2021. Originally designed for a 30-day technology demonstration consisting of up to 5 flights, "
        "Ingenuity completed 72 operational flights over nearly three years before concluding its mission."
    )
print(f"Generated {txt_path}")

# 4. Generate Markdown
md_path = SAMPLES_DIR / "Enterprise_Cloud_Security_Policy.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write(
        "# Enterprise Cloud Infrastructure & Data Security Policy\n\n"
        "## Policy Statement: Access Control & Zero Trust\n"
        "All corporate resources adhere strictly to the principle of Least Privilege and Zero Trust Architecture. "
        "Access to production cloud environments requires Multi-Factor Authentication (MFA) utilizing FIDO2 hardware security keys. "
        "Password-only authentication and SMS-based verification are strictly prohibited.\n\n"
        "## Data Encryption Standards\n"
        "- **Data at Rest**: All storage volumes, vector database clusters, and object storage buckets must use AES-256 GCM encryption.\n"
        "- **Data in Transit**: All network communications require TLS 1.3 encryption with Perfect Forward Secrecy (PFS).\n"
        "- **Key Management**: Customer-managed encryption keys (CMEK) must be rotated automatically every 90 days.\n\n"
        "## Incident Response Protocol\n"
        "Security incidents classified as Severity-1 require incident commander mobilization within 15 minutes of detection. "
        "All forensic logs must be preserved in immutable, write-once-read-many (WORM) storage for a minimum retention period of 365 days."
    )
print(f"Generated {md_path}")

