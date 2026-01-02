"""
Prompt templates for Legal Explanation RAG
"""

# System prompt to set the persona and constraints
LEGAL_SYSTEM_PROMPT = """You are an expert legal assistant for the "Nepal Justice Weaver" platform. 
Your goal is to explain complex Nepali laws in simple, plain language that anyone can understand.

Follow these guidelines:
1. SIMPLICITY: Use everyday language. Avoid legal jargon where possible, or explain it simply if necessary.
2. ACCURACY: Base your explanation ONLY on the provided context (retrieved laws). Do not invent laws.
3. EMPATHY: Be helpful and direct. Address the user's situation.
4. STRUCTURE: Use short paragraphs and bullet points for readability.
5. LANGUAGE: Respond in English (unless asked otherwise), but keep in mind the user might be a non-native speaker.

If the provided context does not contain the answer, state clearly that you couldn't find the specific law in the available documents, but provide general guidance if possible based on general knowledge (marking it as such).
"""

# Main RAG prompt template
LEGAL_RAG_PROMPT_TEMPLATE = """
CONTEXT (Relevant Laws):
{context}

USER QUERY:
{query}

INSTRUCTIONS:
Based on the laws provided above, explain the answer to the user's query. 
Start with a direct answer, then explain the details simply. 
Cite the specific Article or Section numbers mentioned in the context.
"""

def format_rag_prompt(query: str, context_chunks: list) -> str:
    """
    Format the RAG prompt with query and context
    
    Args:
        query: User's question
        context_chunks: List of retrieved chunk dictionaries
        
    Returns:
        Formatted prompt string
    """
    # Format context chunks
    formatted_context = []
    for i, chunk in enumerate(context_chunks, 1):
        source = chunk['metadata'].get('source_file', 'Unknown Source')
        section = chunk['metadata'].get('article_section', 'Unknown Section')
        text = chunk['text']
        
        formatted_context.append(f"SOURCE {i}: {source} | SECTION: {section}\nCONTENT: {text}\n")
    
    context_str = "\n---\n".join(formatted_context)
    
    return LEGAL_RAG_PROMPT_TEMPLATE.format(
        context=context_str,
        query=query
    )
