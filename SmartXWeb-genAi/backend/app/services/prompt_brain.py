import re
from enum import Enum
from typing import Optional, Dict, Any

class TaskIntent(str, Enum):
    GENERAL_QA = "general_qa"
    CODING = "coding"
    REASONING = "reasoning"
    VISUAL_DIAGRAM = "visual_diagram"

class PromptBrain:
    """
    The Brain of the Intelligent Knowledge Retrieval System.
    Manages prompt engineering, hallucination prevention directives,
    citation protocols, and task-specific reasoning frameworks.
    """

    @classmethod
    def detect_intent(cls, question: str) -> TaskIntent:
        """
        Dynamically classifies the user's query intent to route to the
        optimal prompt template and specialized model.
        """
        q_lower = question.lower()

        # 1. Visual or Diagram intent
        if re.search(r'\b(diagram|flowchart|visualize|architecture chart|sequence diagram|draw|visual representation)\b', q_lower):
            return TaskIntent.VISUAL_DIAGRAM

        # 2. Coding intent
        if re.search(r'\b(code|python|function|class|javascript|typescript|react|api|sql|script|algorithm|regex|bug|syntax|implement|method)\b', q_lower):
            return TaskIntent.CODING

        # 3. Deep Analytical / Reasoning intent
        if re.search(r'\b(why|prove|reason|step-by-step|compare|contrast|tradeoffs|evaluate|analysis|implications|root cause)\b', q_lower):
            return TaskIntent.REASONING

        return TaskIntent.GENERAL_QA

    @classmethod
    def get_system_prompt(cls, intent: TaskIntent = TaskIntent.GENERAL_QA) -> str:
        """
        Core system directives that govern the LLM's cognition, grounding,
        and strict refusal boundaries.
        """
        base_rules = (
            "You are an enterprise Intelligent Knowledge Retrieval and Question Answering Assistant (SmartX RAG).\n"
            "Your objective is to provide high-precision answers grounded strictly in the provided document excerpts.\n\n"
            "### CRITICAL OPERATING PROTOCOLS (ZERO-HALLUCINATION POLICY):\n"
            "1. Answer ONLY using facts explicitly present in the provided Document Excerpts.\n"
            "2. If the excerpts do NOT contain sufficient information to answer the question, you MUST refuse by stating:\n"
            "   'The uploaded documents do not contain sufficient information to answer this question.'\n"
            "3. NEVER speculate, extrapolate, assume, or inject outside knowledge not corroborated by the excerpts.\n"
            "4. For every factual claim, cite the source document and page number, e.g.: [Source X: Document 'filename', Page Y].\n"
            "5. Never fabricate citations or source numbers.\n"
        )

        if intent == TaskIntent.CODING:
            specialized_directive = (
                "\n### CODING & IMPLEMENTATION DIRECTIVES:\n"
                "- Extract exact API signatures, data schemas, algorithms, and specifications from the excerpts.\n"
                "- Provide clean, idiomatic, fully working code blocks with proper syntax highlighting.\n"
                "- Ensure code directly reflects the technical constraints and logic described in the documents.\n"
            )
        elif intent == TaskIntent.REASONING:
            specialized_directive = (
                "\n### ANALYTICAL REASONING DIRECTIVES:\n"
                "- Perform step-by-step verification of facts across the retrieved passages.\n"
                "- Cross-reference multiple excerpts to resolve complex relationships or trade-offs.\n"
                "- Structure your answer with clear bullet points, logical steps, and source attribution at each step.\n"
            )
        elif intent == TaskIntent.VISUAL_DIAGRAM:
            specialized_directive = (
                "\n### VISUAL DIAGRAM DIRECTIVES:\n"
                "- Synthesize the document flow, system architecture, or process into a Mermaid diagram (`flowchart TD` or `sequenceDiagram`).\n"
                "- Provide a concise explanatory walkthrough citing the relevant sections.\n"
            )
        else:
            specialized_directive = (
                "\n### GENERAL QA DIRECTIVES:\n"
                "- Provide concise, clear, and structured answers.\n"
                "- Highlight key takeaways with bullet points where appropriate.\n"
            )

        return base_rules + specialized_directive

    @classmethod
    def build_user_prompt(cls, question: str, context: str) -> str:
        """
        Constructs the grounded context window linking raw retrieved chunks
        with clear boundary demarcations.
        """
        return (
            "=== SOURCE DOCUMENT EXCERPTS ===\n"
            f"{context.strip() if context and context.strip() else '[No relevant excerpts retrieved]'}\n"
            "=== END OF EXCERPTS ===\n\n"
            f"User Question: {question}\n\n"
            "Answer strictly grounded in the excerpts above (with source citations):"
        )

