# Quotla AI Document Generator API

A FastAPI-based service that converts natural language prompts into structured business documents (invoices and quotes) using AI, with support for multiple AI providers and export formats.

## Features

- **Natural Language Processing**: Convert plain text descriptions into structured invoice/quote data
- **Multi-Provider AI Support**: OpenAI, Anthropic Claude, and Google Gemini
- **File Upload Support**: Extract data from PDF, DOCX, TXT, and image files
- **Vision AI**: Process scanned receipts and invoice photos using vision models
- **Multiple Export Formats**: JSON, PDF, DOCX, and PNG
- **Conversation History**: Support for multi-turn conversations to refine documents
- **AI-Powered Detection**: Automatically detects document type based on context
- **Smart Currency Detection**: Prompts user when currency is not specified

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file with your AI provider credentials:

```bash
# Choose your AI provider: openai, anthropic, or gemini
AI_PROVIDER=openai

# Add the corresponding API key
OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here
# GEMINI_API_KEY=your_key_here
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Access Points:**
- Server: http://localhost:8000
- Interactive API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Verify Server:**
```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

## API Endpoints

### Health Check

**GET** `/health`

Returns server health status.

```bash
curl http://localhost:8000/health
```

Response:
```json
{"status": "healthy"}
```

---

### Generate Document (JSON)

**POST** `/api/generate`

Generate structured document data from natural language prompt. Auto-detects document type if not specified.

**Request Body:**
```json
{
  "prompt": "Invoice for John Doe at 123 Main St, Lagos. 100 units of Product X at 5000 NGN each",
  "history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ],
  "document_type": "invoice"
}
```

**Parameters:**
- `prompt` (required): Natural language description of the document
- `history` (optional): Conversation history for context
- `document_type` (optional): "invoice" or "quote" (auto-detected if omitted)

**Response:**
```json
{
  "success": true,
  "document_type": "invoice",
  "data": {
    "invoice_number": "INV20241201153045",
    "date": "2024-12-01",
    "customer_name": "John Doe",
    "address": "123 Main St",
    "city": "Lagos",
    "country": "Nigeria",
    "items": [
      {
        "description": "Product X",
        "quantity": 100,
        "unit_price": 5000,
        "amount": 500000
      }
    ],
    "subtotal": 500000,
    "tax_rate": 0.075,
    "tax_amount": 37500,
    "delivery_rate": 0.03,
    "delivery_amount": 15000,
    "total": 552500,
    "currency": "NGN"
  },
  "text_output": "--- INVOICE ---\n..."
}
```

**Examples:**

```bash
# Basic invoice generation
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Invoice for Jane Smith in Abuja. 50 consulting hours at 15000 NGN per hour"
  }'

# Multi-item invoice with conversation history
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Actually, change quantity to 1000 units",
    "history": [
      {"role": "user", "content": "Create invoice for 500 units of Product X at 5000 NGN"},
      {"role": "assistant", "content": "Invoice created with 500 units"}
    ],
    "document_type": "invoice"
  }'
```

---

### Generate Invoice (Specific Type)

**POST** `/api/generate/invoice`

Shortcut endpoint that forces document type to "invoice".

```bash
curl -X POST http://localhost:8000/api/generate/invoice \
  -H "Content-Type: application/json" \
  -d '{"prompt": "John at Lagos for 500 units at 5000 NGN"}'
```

---

### Generate Quote (Specific Type)

**POST** `/api/generate/quote`

Shortcut endpoint that forces document type to "quote".

```bash
curl -X POST http://localhost:8000/api/generate/quote \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Jane Smith in Abuja. 50 consulting hours at 15000 NGN per hour"}'
```

---

### Generate with File Upload (Documents & Images)

**POST** `/api/generate/with-file`

Extract document data from uploaded files - supports both document files (PDF, DOCX, TXT) and images.

**Request (multipart/form-data):**
- `prompt` (required): Instructions for extracting data
- `file` (required): Document or image file
- `document_type` (optional): "invoice" or "quote" (auto-detected if omitted)

**Supported File Types:**

*Documents (Text Extraction):*
- PDF (.pdf)
- Word Documents (.docx, .doc)
- Text Files (.txt)

*Images (Vision AI):*
- JPEG / JPG
- PNG
- Other image formats

**AI Models Used:**

*For Images:*
- OpenAI: gpt-4o
- Anthropic: claude-3-5-sonnet-20241022
- Gemini: gemini-1.5-flash

*For Documents:*
- OpenAI: gpt-4
- Anthropic: claude-3-5-sonnet-20241022
- Gemini: gemini-pro

**Examples:**

```bash
# Extract from PDF invoice
curl -X POST http://localhost:8000/api/generate/with-file \
  -F "prompt=Extract invoice data from this PDF" \
  -F "file=@invoice.pdf" \
  -F "document_type=invoice"

# Extract from Word document
curl -X POST http://localhost:8000/api/generate/with-file \
  -F "prompt=Parse quote information" \
  -F "file=@quote.docx"

# Extract from receipt image
curl -X POST http://localhost:8000/api/generate/with-file \
  -F "prompt=Extract data from this receipt" \
  -F "file=@receipt.jpg"

# Extract from text file
curl -X POST http://localhost:8000/api/generate/with-file \
  -F "prompt=Create invoice from this data" \
  -F "file=@invoice_data.txt"
```

---

### Export as PDF

**POST** `/api/export/pdf`

Generate document and download as professionally formatted PDF.

**Request:** Same as `/api/generate`

**Response:** Binary PDF file

```bash
curl -X POST http://localhost:8000/api/export/pdf \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Invoice for John at Lagos for 500 units at 5000 NGN"}' \
  --output invoice.pdf
```

**PDF Features:**
- Professional layout with header and branding
- Formatted tables for line items
- Color-coded sections
- Automatic calculations displayed
- Currency formatting

---

### Export as DOCX

**POST** `/api/export/docx`

Generate document and download as Microsoft Word document.

**Request:** Same as `/api/generate`

**Response:** Binary DOCX file

```bash
curl -X POST http://localhost:8000/api/export/docx \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Quote for 100 hours consulting at 20000 NGN"}' \
  --output quote.docx
```

**DOCX Features:**
- Editable Word document format
- Professional table styling
- Bold headers and totals
- Preserves formatting for easy customization

---

### Export as PNG

**POST** `/api/export/png`

Generate document and download as PNG image.

**Request:** Same as `/api/generate`

**Response:** Binary PNG file

```bash
curl -X POST http://localhost:8000/api/export/png \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Invoice for services rendered"}' \
  --output invoice.png
```

**Image Features:**
- 800x1000 pixel resolution
- Clean white background
- Professional typography
- Easy sharing on social media/messaging apps

---

## AI Provider Configuration

### Supported Providers

The service supports three AI providers, configurable via the `AI_PROVIDER` environment variable:

#### OpenAI (Default)
```bash
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
```
- Text model: `gpt-4`
- Vision model: `gpt-4o`
- Best for: General reliability and speed

#### Anthropic Claude
```bash
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```
- Model: `claude-3-5-sonnet-20241022`
- Best for: Complex reasoning and accuracy
- Supports vision capabilities

#### Google Gemini
```bash
AI_PROVIDER=gemini
GEMINI_API_KEY=...
```
- Text model: `gemini-pro`
- Vision model: `gemini-1.5-flash`
- Best for: Fast processing and cost efficiency

---

## Document Processing Logic

### 1. Document Type Detection

If `document_type` is not provided, the API auto-detects based on keywords:
- Contains "invoice" or "bill" → Invoice
- Otherwise → Quote

### 2. Data Extraction

The AI service uses provider-specific prompts from:
- `app/prompts/invoice_prompt.txt`
- `app/prompts/quote_prompt.txt`

### 3. Data Enrichment

After AI extraction, the system automatically adds:

**For Invoices:**
- `invoice_number`: `INV{YYYYMMDDHHmmss}`
- `date`: Current date
- `subtotal`: Sum of all item amounts
- `tax_rate`: 7.5% (default for Nigeria)
- `tax_amount`: Calculated from subtotal
- `delivery_rate`: 3% (default)
- `delivery_amount`: Calculated from subtotal
- `total`: Subtotal + tax + delivery
- `currency`: NGN (default)

**For Quotes:**
- `quote_number`: `QT{YYYYMMDDHHmmss}`
- `date`: Current date
- `subtotal`: Sum of all item amounts
- `tax_rate`: 7.5% (default)
- `tax_amount`: Calculated from subtotal
- `total`: Subtotal + tax
- `currency`: NGN (default)

### 4. Item Calculation

For each item:
```
amount = quantity × unit_price
```

All monetary calculations are automatic.

---

## Customizing AI Prompts

Customize extraction behavior by editing prompt files:

**Invoice Prompt:**
```bash
# Edit app/prompts/invoice_prompt.txt
```

**Quote Prompt:**
```bash
# Edit app/prompts/quote_prompt.txt
```

Prompts define the JSON schema and extraction instructions for the AI models. The current prompts instruct the AI to extract:
- Customer information (name, address, city, country)
- Line items (description, quantity, unit_price)
- Tax and delivery rates
- Currency

---

## Testing

### Manual Testing

Use the interactive Swagger UI at http://localhost:8000/docs to test all endpoints with a visual interface.

### Automated Tests

Run the comprehensive test suite:

```bash
# Make sure server is running first
uvicorn app.main:app --reload

# In another terminal, run tests
python tests/test_api.py
```

**Test Coverage:**
1. Health check
2. Simple invoice generation
3. Quote generation
4. Complex multi-item invoices
5. Auto-detect document type
6. Conversation history context
7. Missing information handling
8. Large number handling
9. Currency extraction
10. Calculation accuracy
11. Performance benchmark

---

## Architecture

```
quotla/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app and endpoints
│   ├── ai_service.py        # AI provider integrations
│   ├── export_service.py    # PDF/DOCX/PNG generation
│   └── prompts/
│       ├── invoice_prompt.txt
│       └── quote_prompt.txt
├── tests/
│   ├── test_api.py          # API performance tests
│   └── test_image_upload.py # Image upload tests
├── requirements.txt
├── .env.example
└── README.md
```

### Core Components

**FastAPI Application ([app/main.py](app/main.py))**
- Route handlers for all endpoints
- Request/response models using Pydantic
- Document type detection logic
- Data enrichment and formatting
- CORS middleware configuration

**AI Service ([app/ai_service.py](app/ai_service.py))**
- Provider-agnostic AI interface
- Handles OpenAI, Anthropic, and Gemini
- Text and vision model support
- JSON parsing and validation
- Prompt loading from files

**Export Service ([app/export_service.py](app/export_service.py))**
- PDF generation using ReportLab
- DOCX generation using python-docx
- PNG generation using Pillow
- Professional formatting and styling

---

## Dependencies

```
fastapi==0.104.1           # Web framework
uvicorn[standard]          # ASGI server
pydantic==2.5.0           # Data validation
python-dotenv==1.0.0      # Environment management
openai>=2.8.0             # OpenAI API client
anthropic>=0.39.0         # Anthropic API client
google-generativeai>=0.8.0 # Gemini API client
python-multipart==0.0.6   # File upload support
Pillow>=10.0.0            # Image processing
reportlab>=4.0.0          # PDF generation
python-docx>=1.0.0        # DOCX reading & generation
PyPDF2>=3.0.0             # PDF text extraction
pdfplumber>=0.10.0        # Advanced PDF parsing
```

---

## Troubleshooting

### Server Won't Start

**Issue: "No module named 'openai'"**
```bash
pip install -r requirements.txt
```

**Issue: "Port 8000 already in use"**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# OR use different port
uvicorn app.main:app --reload --port 8001
```

**Issue: "Python was not found"**
```bash
# Use py launcher
py -m uvicorn app.main:app --reload
```

### 500 Internal Server Errors

**Common Causes:**

1. **Invalid API Key**
   - Check `.env` file has correct `OPENAI_API_KEY=sk-...`
   - No quotes around the key
   - Verify key at https://platform.openai.com/account/api-keys

2. **No Credits**
   - Add credits to OpenAI account
   - OR switch to different provider (Anthropic/Gemini)

3. **AI Parsing Errors**
   - AI returned non-JSON text
   - Check uvicorn logs for actual error
   - Try different AI provider

**Debug Steps:**
```bash
# 1. Start with verbose logging
uvicorn app.main:app --reload --log-level debug

# 2. Test with simple request
curl -X POST "http://localhost:8000/api/generate/quote" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Quote for 1 item at 100 USD"}'

# 3. Check API key works
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

### Currency Detection Issues

**Symptom:** Backend returns `needs_currency: true`

**Solution:** Always include currency explicitly:
```bash
✅ GOOD: "Quote for Jane. 50 hours at 15000 NGN"
❌ BAD: "Quote for Jane. 50 hours at 15000"
```

---

## Recent Fixes

### Tax & Delivery Calculation Bug (FIXED)

**Issue:** Tax and delivery rates were displaying as 800% and 300% instead of 8% and 3%

**Root Cause:** AI returns rates as percentages (8 for 8%), but backend treated them as decimals (0.08)

**Solution:**
- Convert AI-provided percentages to decimals for calculations
- Store both formats: `tax_rate` (decimal) and `tax_rate_percentage` (display)
- Update display logic to use the percentage field

**Files Modified:**
- [app/main.py:568-589](app/main.py#L568-L589) - `_enrich_data()` calculation fix
- [app/main.py:617-618, 635](app/main.py#L617-L618) - `_format_text()` display fix

**Verification:**
```bash
# Test the fix
curl -X POST "http://localhost:8000/api/generate/quote" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Quote for Jane Smith in Abuja. 50 consulting hours at 15000 NGN per hour"}'

# Expected: Tax (7.5%): NGN 56,250.00 (NOT 800%)
```

---

## Frontend Integration Notes

**For Next.js/React Frontend Developers:**

The backend now returns two fields for rates:

```json
{
  "tax_rate": 0.075,           // Decimal for calculations
  "tax_rate_percentage": 7.5,  // Original percentage for display
  "delivery_rate": 0.03,       // Decimal for calculations
  "delivery_rate_percentage": 3 // Original percentage for display
}
```

**Best Practices:**
- Use `tax_rate` and `delivery_rate` for calculations (decimals)
- Use `tax_rate_percentage` and `delivery_rate_percentage` for display (percentages)
- Handle `needs_currency: true` response by prompting user for currency
- Check `success: false` for error handling

---

## Error Handling

All endpoints return appropriate HTTP status codes:

**200 OK**: Successful operation
```json
{
  "success": true,
  "document_type": "invoice",
  "data": {...}
}
```

**400 Bad Request**: Invalid input
```json
{
  "detail": "Invalid request format"
}
```

**500 Internal Server Error**: Processing error
```json
{
  "detail": "Error message details"
}
```

---

## Performance Considerations

- Average response time: 2-8 seconds (depends on AI provider)
- Concurrent request support via FastAPI async
- In-memory processing (no database required)
- Suitable for production with proper scaling

---

## Production Deployment

### Deploy to Render

The easiest way to deploy this API is using Render:

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to [render.com](https://render.com) and sign up/login
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml` and configure the service
   - Add your API keys as environment variables:
     - `OPENAI_API_KEY`
     - `GEMINI_API_KEY` (for fallback)
     - `ANTHROPIC_API_KEY` (optional)
   - Click "Create Web Service"

3. **Access Your API**
   - Your API will be available at `https://your-service-name.onrender.com`
   - Interactive docs: `https://your-service-name.onrender.com/docs`

**Note:** The free tier on Render may spin down after inactivity. First request after inactivity may take 30-60 seconds.

### Manual Deployment

For production environments with custom hosting:

```bash
# Without auto-reload, with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# With Gunicorn (recommended)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables

Required for production:
- `AI_PROVIDER` - Primary AI provider (openai, anthropic, or gemini)
- `FALLBACK_AI_PROVIDER` - Fallback provider if primary fails (default: gemini)
- `OPENAI_API_KEY` - OpenAI API key (if using OpenAI)
- `GEMINI_API_KEY` - Google Gemini API key (if using Gemini)
- `ANTHROPIC_API_KEY` - Anthropic API key (if using Claude)

Optional:
- `DEFAULT_TAX_RATE` - Default tax rate percentage (default: 7.5)
- `DEFAULT_DELIVERY_RATE` - Default delivery rate percentage (default: 3.0)

---

## License

See LICENSE file for details.

---

## Support

For issues or questions:
- Check the API docs: http://localhost:8000/docs
- Review test examples in `tests/test_api.py`
- Examine prompt templates in `app/prompts/`
- Enable debug logging: `uvicorn app.main:app --reload --log-level debug`
