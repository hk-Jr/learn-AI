import re
import json
from typing import List, Dict, Any, Optional, Tuple
import httpx
from app.config import settings
from app.services.prompt_brain import PromptBrain, TaskIntent

COMMON_STOPWORDS = {
    "what", "when", "where", "which", "who", "whom", "whose", "why", "how", "does",
    "explain", "tell", "describe", "about", "the", "and", "for", "with", "from",
    "that", "this", "these", "those", "are", "was", "were", "been", "have", "has",
    "had", "can", "could", "will", "would", "average", "many", "much", "more",
    "most", "some", "any", "other", "into", "over", "under", "their", "there"
}

class LLMService:
    @classmethod
    def get_available_ollama_models(cls, ollama_url: Optional[str] = None) -> List[str]:
        """Query local Ollama instance for installed models."""
        base_url = (ollama_url or settings.OLLAMA_BASE_URL).rstrip("/")
        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.get(f"{base_url}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []

    @classmethod
    def resolve_model_for_task(cls, provider: str, user_model: Optional[str], intent: TaskIntent, ollama_url: Optional[str] = None) -> str:
        """
        Dynamically selects or routes to specialized models based on query intent.
        E.g., coding queries route to coding models, reasoning queries to reasoning models.
        """
        if user_model and user_model.strip():
            return user_model.strip()

        if provider == "ollama":
            available = cls.get_available_ollama_models(ollama_url)
            # 1. Coding specialized routing
            if intent == TaskIntent.CODING:
                for candidate in ["codellama", "deepseek-coder", "qwen2.5-coder", "starcoder2"]:
                    for m in available:
                        if candidate in m.lower():
                            return m
            # 2. Reasoning specialized routing
            elif intent == TaskIntent.REASONING:
                for candidate in ["deepseek-r1", "llama3.3", "qwq"]:
                    for m in available:
                        if candidate in m.lower():
                            return m

            # Default to first available or standard llama3
            return available[0] if available else (settings.DEFAULT_LLM_MODEL or "llama3")

        if provider == "gemini":
            return "gemini-2.5-flash"

        if provider == "openai":
            return "gpt-4o-mini"

        return "smart_local"

    @classmethod
    def smart_local_synthesize(cls, question: str, context: str, intent: TaskIntent = TaskIntent.GENERAL_QA) -> str:
        """
        High-precision deterministic synthesis engine when running without external API keys.
        Extracts and composes answers strictly from the retrieved chunks.
        Prevents fabrication when context lacks sufficient information.
        """
        if not context or not context.strip():
            return "The uploaded documents do not contain sufficient information to answer this question."

        words = re.findall(r'\b[a-zA-Z0-9_-]{3,}\b', question.lower())
        q_terms = [w for w in words if w not in COMMON_STOPWORDS]

        if not q_terms:
            q_terms = [w for w in words if len(w) > 2]

        if not q_terms:
            return "The uploaded documents do not contain sufficient information to answer this question."

        blocks = context.split("\n\n---\n\n")
        relevant_findings = []
        all_matched_terms = set()

        for block in blocks:
            header_match = re.search(r'\[Source \d+: Document [^\]]+\]', block)
            header = header_match.group(0) if header_match else "Source Excerpt"
            body = block.replace(header, "").strip() if header_match else block

            sentences = re.split(r'(?<=[.!?])\s+', body)
            matching_sents = []

            for sent in sentences:
                sent_clean = sent.strip()
                if not sent_clean or len(sent_clean) < 15:
                    continue
                matched_in_sent = [t for t in q_terms if t in sent_clean.lower()]
                if matched_in_sent:
                    score = len(matched_in_sent)
                    if len(q_terms) >= 3 and score < 2:
                        continue
                    all_matched_terms.update(matched_in_sent)
                    matching_sents.append((score, sent_clean))

            if matching_sents:
                matching_sents.sort(key=lambda x: x[0], reverse=True)
                top_sents = [s[1] for s in matching_sents[:2]]
                combined = " ".join(top_sents)
                relevant_findings.append(f"• **According to {header}:**\n  {combined}")

        coverage = len(all_matched_terms) / len(q_terms)
        if not relevant_findings or coverage < 0.4:
            return "The uploaded documents do not contain sufficient information to answer this question."

        # If user asked for visual diagram, append a Mermaid block
        diagram_block = ""
        if intent == TaskIntent.VISUAL_DIAGRAM:
            diagram_block = (
                "\n\n```mermaid\n"
                "flowchart TD\n"
                "    UserQuery[\"User Question\"] --> RAG[\"SmartX RAG Retrieval\"]\n"
                "    RAG --> Context[\"Grounded Document Excerpts\"]\n"
                "    Context --> Answer[\"Synthesized Output with Citations\"]\n"
                "```\n"
            )

        answer_parts = [
            "Based on the uploaded documents, here is the relevant information:",
            "",
            "\n\n".join(relevant_findings),
            diagram_block,
            "*Information sourced directly from retrieved document excerpts.*"
        ]
        return "\n".join(answer_parts).strip()

    @classmethod
    def generate_answer(
        cls,
        question: str,
        context: str,
        provider: str = "smart_local",
        model: Optional[str] = None,
        gemini_key: Optional[str] = None,
        openai_key: Optional[str] = None,
        ollama_url: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        The Brain Execution Pipeline:
        1. Analyzes user intent (coding, reasoning, visual diagram, general QA).
        2. Routes to the best-suited model dynamically.
        3. Constructs structured zero-hallucination system prompt and context boundary.
        4. Invokes the selected LLM provider or local fallback.
        """
        gemini_api_key = gemini_key or settings.GEMINI_API_KEY
        openai_api_key = openai_key or settings.OPENAI_API_KEY

        # 1. Detect Intent via Brain
        intent = PromptBrain.detect_intent(question)
        system_prompt = PromptBrain.get_system_prompt(intent)
        user_prompt = PromptBrain.build_user_prompt(question, context)

        # 2. Resolve Model dynamically
        active_model = cls.resolve_model_for_task(provider, model, intent, ollama_url)

        # 3. Google Gemini Provider
        if provider == "gemini" and gemini_api_key:
            try:
                from google import genai
                client = genai.Client(api_key=gemini_api_key)
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = client.models.generate_content(
                    model=active_model,
                    contents=full_prompt
                )
                if response and response.text:
                    return response.text.strip(), f"Gemini ({active_model})"
            except Exception as e:
                print(f"[LLMService] Gemini generation error, falling back: {e}")

        # 4. OpenAI Provider
        if provider == "openai" and openai_api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_api_key)
                response = client.chat.completions.create(
                    model=active_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1
                )
                ans = response.choices[0].message.content
                return ans.strip(), f"OpenAI ({active_model})"
            except Exception as e:
                print(f"[LLMService] OpenAI generation error, falling back: {e}")

        # 5. Ollama Provider with Dynamic Task Routing
        if provider == "ollama":
            base_url = (ollama_url or settings.OLLAMA_BASE_URL).rstrip("/")
            try:
                with httpx.Client(timeout=45.0) as client:
                    full_prompt = f"{system_prompt}\n\n{user_prompt}"
                    resp = client.post(
                        f"{base_url}/api/generate",
                        json={"model": active_model, "prompt": full_prompt, "stream": False}
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        return data.get("response", "").strip(), f"Ollama ({active_model})"
                    else:
                        print(f"[LLMService] Ollama error code {resp.status_code}: {resp.text}")
            except Exception as e:
                print(f"[LLMService] Ollama connection error, falling back: {e}")

        # 6. Built-in Smart Local Grounded Engine
        ans = cls.smart_local_synthesize(question, context, intent)
        return ans, "Smart Local Grounded Engine"
