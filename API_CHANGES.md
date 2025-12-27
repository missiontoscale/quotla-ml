# API Consolidation - Version 2.0.0

## Summary

The Quotla AI API has been refactored from multiple fragmented endpoints into a **unified design** with a single universal endpoint that handles all input types.

## What Changed

### Before (v1.0)
```
/api/generate           - Text prompts only
/api/generate/invoice   - Text prompts (force invoice type)
/api/generate/quote     - Text prompts (force quote type)
/api/generate/with-file - File uploads only
```

### After (v2.0)
```
/api/generate          - Universal endpoint (text, files, images, all in one!)
/api/export/pdf        - Export to PDF (now also accepts files)
/api/export/docx       - Export to DOCX (now also accepts files)
/api/export/png        - Export to PNG (now also accepts files)
```

## Migration Guide

### For Text-Only Requests

**Before:**
```json
POST /api/generate
{
  "prompt": "Invoice for John at Lagos, 100 units at 5000 NGN"
}
```

**After (still works!):**
```
POST /api/generate
Content-Type: multipart/form-data

prompt: "Invoice for John at Lagos, 100 units at 5000 NGN"
```

### For File Uploads

**Before:**
```
POST /api/generate/with-file
Content-Type: multipart/form-data

prompt: "Extract invoice data"
file: [uploaded file]
```

**After:**
```
POST /api/generate
Content-Type: multipart/form-data

prompt: "Extract invoice data"
file: [uploaded file]
```

### For Specific Document Types

**Before:**
```json
POST /api/generate/invoice
{
  "prompt": "John at Lagos, 100 units at 5000 NGN"
}
```

**After:**
```
POST /api/generate
Content-Type: multipart/form-data

prompt: "John at Lagos, 100 units at 5000 NGN"
document_type: "invoice"
```

## Key Benefits

1. **Simplified API Surface**: One endpoint for everything
2. **More Flexible**: Mix text prompts with file uploads
3. **Better Developer Experience**: No need to remember which endpoint to use
4. **Backward Compatible**: Legacy endpoints still work (marked as deprecated)
5. **Export Enhancements**: All export formats now support file uploads

## Universal Endpoint Parameters

### `/api/generate`

**Form Parameters:**
- `prompt` (optional*): Text instruction or description
- `file` (optional*): File upload (PDF, DOCX, TXT, JPEG, PNG, etc.)
- `document_type` (optional): Force "invoice" or "quote" (auto-detected if omitted)
- `history` (optional): JSON string of conversation history

*At least one of `prompt` or `file` must be provided.

**Examples:**

1. Text only:
```
prompt: "Invoice for John at Lagos, 100 units at 5000 NGN"
```

2. File only:
```
file: [invoice.pdf]
prompt: "Extract all data"
```

3. Image upload:
```
file: [receipt.jpg]
prompt: "Extract invoice from this receipt photo"
```

4. Force document type:
```
prompt: "John Smith, 50 hours consulting"
document_type: "quote"
```

5. With conversation history:
```
prompt: "Change the customer to Jane Doe"
history: '[{"role":"user","content":"..."},{"role":"assistant","content":"..."}]'
```

## Export Endpoints

All export endpoints now accept the same parameters as `/api/generate`:

### `/api/export/pdf`
Generate and download as PDF

### `/api/export/docx`
Generate and download as Word document

### `/api/export/png`
Generate and download as PNG image

**Example:**
```
POST /api/export/pdf
Content-Type: multipart/form-data

file: [scanned_invoice.jpg]
prompt: "Convert this scanned invoice to PDF"
```

## Legacy Endpoints (Deprecated)

The following endpoints are **deprecated but still functional** for backward compatibility:

- `/api/generate/invoice` - Use `/api/generate` with `document_type="invoice"`
- `/api/generate/quote` - Use `/api/generate` with `document_type="quote"`
- `/api/generate/with-file` - Use `/api/generate` with `file` parameter

These will be removed in a future version.

## Testing the Changes

You can test the new unified endpoint using curl:

```bash
# Text only
curl -X POST "http://localhost:8000/api/generate" \
  -F "prompt=Invoice for John at Lagos, 100 units at 5000 NGN each"

# With file
curl -X POST "http://localhost:8000/api/generate" \
  -F "prompt=Extract invoice data" \
  -F "file=@invoice.pdf"

# Export to PDF
curl -X POST "http://localhost:8000/api/export/pdf" \
  -F "prompt=Invoice for John at Lagos, 100 units at 5000 NGN each" \
  -o invoice.pdf
```

## Questions?

Refer to the interactive API documentation at `/docs` (Swagger UI) or `/redoc` for detailed information about all endpoints and parameters.
