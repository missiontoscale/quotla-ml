# Quotla API Tests

## Setup

```bash
# Install test dependencies
pip install requests Pillow

# Make sure server is running
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run Tests

### Full API Test Suite
```bash
python tests/test_api.py
```

**Tests include:**
1. Health check
2. Simple invoice generation
3. Quote generation
4. Multi-item invoice
5. Auto-detect document type
6. Conversation history
7. Missing information handling
8. Large numbers
9. Currency extraction
10. Calculation accuracy
11. Performance benchmark

### Image Upload Test
```bash
python tests/test_image_upload.py
```

## Manual Testing

### Test with curl

**Basic invoice:**
```bash
curl -X POST http://localhost:8000/api/generate/invoice \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Invoice for John at Lagos for 500 units at 5000 NGN"}'
```

**With image:**
```bash
curl -X POST http://localhost:8000/api/generate/with-image \
  -F "prompt=Extract invoice from image" \
  -F "image=@invoice.jpg" \
  -F "document_type=invoice"
```

### Test with API Docs

Visit: http://localhost:8000/docs

Interactive UI for testing all endpoints.

## Performance Metrics

**Expected results:**
- Health check: < 0.1s
- Simple generation: 2-5s (depending on AI provider)
- Complex generation: 3-8s
- Image upload: 3-10s (vision models)

## What to Check

✓ **Accuracy**: Are extracted values correct?
✓ **Calculations**: Are totals, tax, delivery calculated properly?
✓ **Format**: Is JSON structure valid?
✓ **Edge cases**: How does it handle missing/incomplete data?
✓ **Performance**: Response times acceptable?
✓ **Error handling**: Graceful failures?
