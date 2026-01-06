# Context-Aware Chat Implementation Guide

## Overview

The context-aware chat system intelligently handles conversation continuity by:
1. **Detecting non-legal queries** (greetings, thanks, etc.) and responding appropriately without RAG
2. **Analyzing message independence** to determine if a message requires previous context
3. **Summarizing conversations** when messages are dependent on previous context
4. **Optimizing RAG calls** by only sending relevant context to the retrieval pipeline

## Architecture Flow

```
User Message
    ↓
Fetch Last 5 Conversations (if conversation_id provided)
    ↓
┌──────────────────────────┐
│  Context Analysis        │
│  (Mistral LLM)          │
└──────────────────────────┘
    ↓
┌──────────────┬──────────────────┬──────────────────┐
│              │                  │                  │
Non-Legal?     Independent?       Dependent?
│              │                  │
↓              ↓                  ↓
Simple         Send current       Summarize +
Response       message to RAG     Send to RAG
```

## API Endpoints

### 1. Context-Aware Chat Endpoint

**Endpoint**: `POST /law-explanation/chat`

**Request**:
```json
{
  "query": "He is making fake allegations",
  "conversation_id": "uuid-of-conversation"  // Optional
}
```

**Response**:
```json
{
  "summary": "Brief answer",
  "key_point": "Key legal point",
  "explanation": "Detailed explanation",
  "next_steps": "Actionable advice",
  "sources": [...],
  "query": "Original or processed query",
  "context_used": true,              // New field
  "is_non_legal": false,             // New field
  "original_query": "He is making...", // Present if context used
  "summarized_query": "My brother is making fake allegations..." // Present if context used
}
```

### 2. Traditional Explain Endpoint (Unchanged)

**Endpoint**: `POST /law-explanation/explain`

This endpoint remains unchanged and does not use conversation context.

## Usage Examples

### Example 1: Dependent Conversation

**Message 1**:
```json
{
  "query": "I had a fight with my brother over property",
  "conversation_id": "conv-123"
}
```

**Response 1**:
- `context_used: false` (no previous messages)
- Returns explanation about property disputes

**Message 2**:
```json
{
  "query": "He is making fake allegations",
  "conversation_id": "conv-123"
}
```

**Response 2**:
- `context_used: true` (dependent on previous message)
- `summarized_query: "My brother is making fake allegations against me in a property dispute"`
- RAG receives the summarized context instead of just "He is making..."

### Example 2: Independent New Topic

**Message 3**:
```json
{
  "query": "How do I apply for citizenship?",
  "conversation_id": "conv-123"
}
```

**Response 3**:
- `context_used: false` (independent new topic)
- Query sent to RAG as-is without previous context

### Example 3: Non-Legal Query

**Message 4**:
```json
{
  "query": "Thank you so much!",
  "conversation_id": "conv-123"
}
```

**Response 4**:
- `is_non_legal: true`
- `explanation: "You're welcome! I'm glad I could help..."`
- No RAG call made (saves cost and time)


## Configuration

### Adjustable Parameters

In `api/routes/chat_history.py`:
```python
# Change number of messages to fetch for context
context = await get_recent_context(
    conversation_id=conversation_id,
    user_id=user["id"],
    limit=5  # Adjust this (default: 5)
)
```

In `module_a/context_analyzer.py`:
```python
# Adjust LLM model for context analysis
class ConversationContextAnalyzer:
    def __init__(self, model: str = "mistral-small-latest"):
        # Options: mistral-tiny, mistral-small-latest, mistral-medium
```

## Testing

### Manual Testing via cURL

```bash
# 1. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'

# 2. Create conversation
curl -X POST http://localhost:8000/chat-history/conversations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Chat"}'

# 3. Send messages
curl -X POST http://localhost:8000/law-explanation/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "I had a fight with my brother", "conversation_id": "CONV_ID"}'

curl -X POST http://localhost:8000/law-explanation/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "He is making allegations", "conversation_id": "CONV_ID"}'
```

### Automated Testing

Run the provided test script:

```bash
cd api
python test_context_chat.py
```

## How It Works Internally

### 1. Non-Legal Query Detection

The system uses Mistral LLM to classify messages:

```
System Prompt: "Determine if this is legal-related or casual conversation"
Input: "Thank you!"
Output: "NON_LEGAL"
```

**Casual categories**:
- Greetings (hi, hello, hey)
- Thanks/gratitude
- Goodbyes
- Small talk

### 2. Independence Analysis

```
System Prompt: "Is the current message independent or dependent?"
Input:
  Previous: "I had a fight with my brother"
  Current: "He is making allegations"
Output: "DEPENDENT"
```

**Independent criteria**:
- New topic
- Self-contained
- No pronouns referencing previous context

**Dependent criteria**:
- Uses pronouns (he, she, it, this, that)
- Continues previous topic
- Follow-up questions

### 3. Conversation Summarization

```
System Prompt: "Combine conversation into one clear legal query"
Input:
  History: "I had a fight with my brother over property"
  Current: "He is making fake allegations"
Output: "My brother is making fake allegations against me in a property dispute. What are my rights?"
```

## Benefits

1. **Better Context Understanding**: Chatbot understands "he", "she", "it" references
2. **Efficient**: Only fetches 5 recent messages (configurable)
3. **Cost-Effective**: Skips RAG for non-legal queries
4. **Accurate**: Uses lightweight LLM for classification before heavy RAG
5. **Flexible**: Works with or without conversation_id

## Troubleshooting

### Issue: Context not being recognized

**Solution**: Check if conversation_id is being passed correctly. Without it, no context is fetched.

### Issue: Non-legal queries being sent to RAG

**Solution**: The LLM classifier might need adjustment. Check `module_a/context_analyzer.py` system prompts.

### Issue: Independent queries marked as dependent

**Solution**: Adjust temperature in `is_independent_query()` or refine the system prompt.

### Issue: Slow response times

**Solution**:
- Reduce context window size (default: 5 messages)
- Use smaller Mistral model (mistral-tiny instead of mistral-small-latest)

## Future Enhancements

Potential improvements:
1. **Caching**: Cache LLM classification results for similar queries
2. **Adaptive Context**: Dynamically adjust context window based on conversation complexity
3. **Multi-turn Summarization**: Better handling of very long conversations
4. **Language Detection**: Handle queries in multiple languages
5. **Intent Recognition**: Detect user intent (question, clarification, new topic, etc.)

## API Response Fields Reference

| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | Brief answer to the query |
| `key_point` | string | Key legal point from sources |
| `explanation` | string | Detailed explanation |
| `next_steps` | string | Actionable advice |
| `sources` | array | Source documents used |
| `query` | string | The processed query |
| `context_used` | boolean | Whether conversation context was used |
| `is_non_legal` | boolean | Whether this is a casual/non-legal query |
| `original_query` | string | Original user query (if context used) |
| `summarized_query` | string | Summarized query sent to RAG (if context used) |
