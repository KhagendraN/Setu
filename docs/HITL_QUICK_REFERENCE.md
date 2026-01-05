# HITL Bias Detection - Quick Reference

## API Endpoints Summary

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/api/v1/bias-detection-hitl/start-review` | POST | Upload PDF & start review | ✓ |
| `/api/v1/bias-detection-hitl/approve-suggestion` | POST | Approve/reject suggestion | ✓ |
| `/api/v1/bias-detection-hitl/regenerate-suggestion` | POST | Get new suggestion | ✓ |
| `/api/v1/bias-detection-hitl/session/{session_id}` | GET | Get session status | ✓ |
| `/api/v1/bias-detection-hitl/generate-pdf` | POST | Generate final PDF | ✓ |
| `/api/v1/bias-detection-hitl/health` | GET | Health check | ✗ |

---

## Sentence Status Flow

```
┌──────────┐
│ pending  │ ◄─── New biased sentence with suggestion
└────┬─────┘
     │
     ├──► approve ────┐
     │                │
     └──► reject      │
            ↓         │
     ┌──────────────────┐
     │needs_regeneration│
     └────┬─────────────┘
          │
          ├──► regenerate ──► pending (with new suggestion)
          │
          └──► give up ──► manual intervention needed
                            │
                            ↓
                      ┌──────────┐
                      │ approved │ ◄─── All approved? → Generate PDF
                      └──────────┘
```

---

## Quick Start (cURL)

```bash
# 1. Start review
SESSION_ID=$(curl -X POST "http://localhost:8000/api/v1/bias-detection-hitl/start-review" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf" | jq -r '.session_id')

# 2. Get session details
curl -X GET "http://localhost:8000/api/v1/bias-detection-hitl/session/$SESSION_ID" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 3. Approve a suggestion
curl -X POST "http://localhost:8000/api/v1/bias-detection-hitl/approve-suggestion" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"sentence_id\":\"SENTENCE_ID\",\"action\":\"approve\",\"approved_suggestion\":\"approved text here\"}"

# 4. Generate PDF
curl -X POST "http://localhost:8000/api/v1/bias-detection-hitl/generate-pdf" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\"}" \
  --output debiased.pdf
```

---

## Key Response Fields

### StartReviewResponse
```javascript
{
  session_id: "uuid",          // Save this!
  total_sentences: 25,
  biased_count: 5,             // Needs review
  neutral_count: 20,           // Auto-approved
  sentences: [...]             // Array of BiasReviewItem
}
```

### BiasReviewItem
```javascript
{
  sentence_id: "uuid",         // Use for approval/rejection
  original_sentence: "...",    // Original text
  is_biased: true,            // true or false
  category: "gender",          // Bias type
  confidence: 0.92,            // 0.0-1.0
  suggestion: "...",           // LLM suggestion
  approved_suggestion: null,   // Filled after approval
  status: "pending"            // pending/approved/needs_regeneration
}
```

### SessionStatusResponse
```javascript
{
  status: "in_progress",       // pending_review/in_progress/completed
  pending_count: 2,            // Still needs review
  approved_count: 22,          // Ready
  needs_regeneration_count: 1  // Rejected, needs new suggestion
}
```

---

## Common Patterns

### Pattern 1: Simple Approval Loop
```python
# Get session
session = start_review(pdf_file)

# Approve all suggestions
for sentence in session['sentences']:
    if sentence['is_biased']:
        approve_suggestion(
            session_id=session['session_id'],
            sentence_id=sentence['sentence_id'],
            approved_text=sentence['suggestion']
        )

# Generate PDF
generate_pdf(session['session_id'])
```

### Pattern 2: Reject & Regenerate
```python
# Reject
approve_suggestion(
    session_id=SESSION_ID,
    sentence_id=SENTENCE_ID,
    action='reject'
)

# Regenerate
new_suggestion = regenerate_suggestion(
    session_id=SESSION_ID,
    sentence_id=SENTENCE_ID
)

# Review new suggestion, then approve
approve_suggestion(
    session_id=SESSION_ID,
    sentence_id=SENTENCE_ID,
    action='approve',
    approved_text=new_suggestion
)
```

### Pattern 3: Check Progress Before PDF
```python
status = get_session_status(SESSION_ID)

if status['pending_count'] == 0 and status['needs_regeneration_count'] == 0:
    pdf = generate_pdf(SESSION_ID)
else:
    print(f"Still need to review {status['pending_count']} sentences")
```

---

## Error Codes

| Code | Error | Solution |
|------|-------|----------|
| 400 | Not all sentences reviewed | Review all pending/rejected sentences |
| 404 | Session not found | Check session_id or start new session |
| 404 | Sentence not found | Verify sentence_id from session data |
| 500 | PDF generation failed | Check logs, may use fallback method |
| 500 | LLM unavailable | Verify MISTRAL_API_KEY is set |
| 503 | Model not loaded | Check bias detection model status |

---

## Testing Checklist

- [ ] Upload PDF successfully
- [ ] Session ID returned
- [ ] Biased sentences have suggestions
- [ ] Neutral sentences auto-approved
- [ ] Can approve suggestion
- [ ] Can reject suggestion
- [ ] Can regenerate after rejection
- [ ] Can get session status
- [ ] PDF generation blocked if not all approved
- [ ] PDF generation succeeds when all approved
- [ ] Downloaded PDF contains changes

---

## Files Structure

```
api/
├── routes/
│   ├── bias_detection.py          # Original bias detection
│   └── bias_detection_hitl.py     # New HITL endpoints
├── schemas.py                      # Data models (updated)
└── main.py                         # Router registration (updated)

utility/
├── pdf_processor.py                # PDF extraction (existing)
├── hitl_session_manager.py         # Session management (new)
└── pdf_regenerator.py              # PDF regeneration (new)

docs/
├── HITL_BIAS_DETECTION_GUIDE.md   # Full documentation
└── HITL_QUICK_REFERENCE.md        # This file
```

---

## Environment Variables

```bash
# Required
MISTRAL_API_KEY=your_mistral_api_key_here

# Optional (already configured)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

---

## Deployment Notes

### Before Deploying:
1. Set MISTRAL_API_KEY environment variable
2. Test with sample PDFs
3. Consider adding rate limiting
4. Monitor memory usage
5. Plan session cleanup strategy

### Production Considerations:
- [ ] Add session TTL (time-to-live)
- [ ] Implement session cleanup job
- [ ] Add file size limits
- [ ] Rate limit LLM API calls
- [ ] Migrate to persistent storage (Supabase/Redis)
- [ ] Add logging and monitoring
- [ ] Implement proper error tracking

---

## Support Resources

- Full Guide: `docs/HITL_BIAS_DETECTION_GUIDE.md`
- Health Check: `GET /api/v1/bias-detection-hitl/health`
- Original Bias Detection: `GET /api/v1/health`
- API Docs: `http://localhost:8000/docs` (when server running)
