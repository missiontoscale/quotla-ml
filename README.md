# Quotla AI Document Generator API

A FastAPI-based service that converts natural language prompts into structured business documents (invoices and quotes) using AI, with support for multiple AI providers and export formats.

## Features

- **Natural Language Processing**: Convert plain text descriptions into structured invoice/quote data
- **Multi-Provider AI Support**: OpenAI GPT-4, Anthropic Claude, and Google Gemini
- **File Upload Support**: Extract data from PDF, DOCX, TXT, and image files
- **Vision AI**: Process scanned receipts and invoice photos using vision models
- **Unified Export Endpoint**: Single `/api/export` endpoint for PDF, DOCX, and PNG formats
- **Conversation History**: Support for multi-turn conversations to refine documents
- **AI-Powered Detection**: Automatically detects document type based on context
- **Smart Currency Detection**: Prompts user when currency is not specified
- **Automatic Calculations**: Tax, delivery, and totals calculated automatically
- **Dual Rate Format**: Stores both decimal and percentage formats for calculations and display

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

### File Upload Support

The `/api/generate` endpoint also supports file uploads using multipart/form-data:

**Request (multipart/form-data):**
- `prompt` (optional): Instructions for extracting data
- `file` (optional): Document or image file
- `document_type` (optional): "invoice" or "quote" (auto-detected if omitted)
- `history` (optional): JSON string of conversation history

**Supported File Types:**

*Documents (Text Extraction):*
- PDF (.pdf)
- Word Documents (.docx, .doc)
- Text Files (.txt)

*Images (Vision AI):*
- JPEG / JPG
- PNG
- GIF, BMP, WEBP

**AI Models Used:**

*For Images (Vision AI):*
- OpenAI: gpt-4o
- Anthropic: claude-3-5-sonnet-20241022
- Gemini: gemini-2.0-flash-exp

*For Documents (Text):*
- OpenAI: gpt-4
- Anthropic: claude-3-5-sonnet-20241022
- Gemini: gemini-2.0-flash-exp

**Examples:**

```bash
# Extract from PDF invoice
curl -X POST http://localhost:8000/api/generate \
  -F "prompt=Extract invoice data from this PDF" \
  -F "file=@invoice.pdf" \
  -F "document_type=invoice"

# Extract from Word document
curl -X POST http://localhost:8000/api/generate \
  -F "prompt=Parse quote information" \
  -F "file=@quote.docx"

# Extract from receipt image
curl -X POST http://localhost:8000/api/generate \
  -F "prompt=Extract data from this receipt" \
  -F "file=@receipt.jpg"

# Extract from text file
curl -X POST http://localhost:8000/api/generate \
  -F "prompt=Create invoice from this data" \
  -F "file=@invoice_data.txt"
```

---

### Legacy Document Generation Endpoints (Deprecated)

The following endpoints are deprecated but still supported for backward compatibility:

- **POST** `/api/generate/invoice` - Use `/api/generate` with `document_type=invoice` instead
- **POST** `/api/generate/quote` - Use `/api/generate` with `document_type=quote` instead
- **POST** `/api/generate/with-file` - Use `/api/generate` with file upload instead

---

### Export Document (Unified Endpoint)

**POST** `/api/export`

Generate document and download in your preferred format (PDF, DOCX, or PNG) - all from one unified endpoint.

**Request Parameters (multipart/form-data):**
- `format` (required): Export format - 'pdf', 'docx', or 'png' (default: 'pdf')
- `prompt` (optional): Natural language description
- `file` (optional): Document or image file to extract from
- `document_type` (optional): 'invoice' or 'quote' (auto-detected if omitted)
- `history` (optional): JSON string of conversation history

**Response:** Binary file in the specified format

**Examples:**

```bash
# Export as PDF (default)
curl -X POST http://localhost:8000/api/export \
  -F "prompt=Invoice for John at Lagos for 500 units at 5000 NGN" \
  -F "format=pdf" \
  --output invoice.pdf

# Export as DOCX (Word document)
curl -X POST http://localhost:8000/api/export \
  -F "prompt=Quote for 100 hours consulting at 20000 NGN" \
  -F "format=docx" \
  --output quote.docx

# Export as PNG (Image)
curl -X POST http://localhost:8000/api/export \
  -F "prompt=Invoice for services rendered" \
  -F "format=png" \
  --output invoice.png

# Export from uploaded file
curl -X POST http://localhost:8000/api/export \
  -F "file=@receipt.jpg" \
  -F "prompt=Extract invoice data" \
  -F "format=pdf" \
  --output extracted_invoice.pdf
```

**Export Format Features:**

**PDF Format:**
- Professional layout with headers and branding
- Formatted tables for line items
- Color-coded sections (header, items, totals)
- Letter-sized pages (8.5" × 11")
- Best for: Print-ready invoices, professional delivery, accounting records

**DOCX Format:**
- Editable Word document format
- Professional table styling with grid borders
- Standard Word/Google Docs/LibreOffice compatibility
- Best for: Templates, custom branding, further modifications

**PNG Format:**
- 800×1000 pixel resolution
- Clean white background
- Professional typography
- Best for: Social media, WhatsApp, quick previews, mobile sharing

---

### Legacy Export Endpoints (Deprecated)

The following endpoints are deprecated but still supported for backward compatibility:

- **POST** `/api/export/pdf` - Use `/api/export` with `format=pdf` instead
- **POST** `/api/export/docx` - Use `/api/export` with `format=docx` instead
- **POST** `/api/export/png` - Use `/api/export` with `format=png` instead

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
- Model: `gemini-2.0-flash-exp`
- Supports both text and vision capabilities
- Best for: Fast processing and cost efficiency

---

## Document Processing Logic

### 1. Document Type Detection

If `document_type` is not provided, the API uses AI-powered detection:
- Analyzes context and keywords in the prompt
- Detects conversational requests vs. business documents
- Falls back to keyword detection if AI detection fails
- Returns "invoice" or "quote" based on context

### 2. Data Extraction

The AI service uses specialized prompts from:
- `app/prompts/invoice_prompt.txt` - Invoice extraction schema
- `app/prompts/quote_prompt.txt` - Quote extraction schema
- `app/prompts/document_type_detection.txt` - Type detection logic

### 3. Data Enrichment

After AI extraction, the system automatically enriches the data:

**For Invoices:**
- `invoice_number`: `INV{YYYYMMDDHHmmss}` (auto-generated timestamp-based ID)
- `date`: Current date (YYYY-MM-DD format)
- `subtotal`: Sum of all item amounts
- `tax_rate`: Decimal value (e.g., 0.075 for 7.5%)
- `tax_rate_percentage`: Display value (e.g., 7.5)
- `tax_amount`: `subtotal × tax_rate`
- `delivery_rate`: Decimal value (e.g., 0.03 for 3%)
- `delivery_rate_percentage`: Display value (e.g., 3.0)
- `delivery_amount`: `subtotal × delivery_rate`
- `total`: `subtotal + tax_amount + delivery_amount`
- `currency`: Extracted from prompt or null (prompts user if missing)

**For Quotes:**
- `quote_number`: `QT{YYYYMMDDHHmmss}` (auto-generated timestamp-based ID)
- `date`: Current date (YYYY-MM-DD format)
- `subtotal`: Sum of all item amounts
- `tax_rate`: Decimal value (e.g., 0.075 for 7.5%)
- `tax_rate_percentage`: Display value (e.g., 7.5)
- `tax_amount`: `subtotal × tax_rate`
- `total`: `subtotal + tax_amount` (no delivery for quotes)
- `currency`: Extracted from prompt or null (prompts user if missing)

**Default Rates (Configurable via Environment):**
- Tax Rate: 7.5% (`DEFAULT_TAX_RATE`)
- Delivery Rate: 3.0% (`DEFAULT_DELIVERY_RATE`)

### 4. Item Calculation

For each line item:
```
amount = quantity × unit_price
```

All monetary calculations are performed automatically during enrichment.

### 5. Response Schema

**Complete Invoice Response Schema:**
```json
{
  "success": true,
  "document_type": "invoice",
  "data": {
    "invoice_number": "INV20241230153045",
    "date": "2024-12-30",
    "customer_name": "John Doe",
    "address": "123 Main Street",
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
    "tax_rate_percentage": 7.5,
    "tax_amount": 37500,
    "delivery_rate": 0.03,
    "delivery_rate_percentage": 3.0,
    "delivery_amount": 15000,
    "total": 552500,
    "currency": "NGN"
  },
  "text_output": "--- INVOICE ---\n..."
}
```

**Complete Quote Response Schema:**
```json
{
  "success": true,
  "document_type": "quote",
  "data": {
    "quote_number": "QT20241230153045",
    "date": "2024-12-30",
    "customer_name": "Jane Smith",
    "address": "456 Oak Avenue",
    "city": "Abuja",
    "country": "Nigeria",
    "items": [
      {
        "description": "Consulting Services",
        "quantity": 50,
        "unit_price": 15000,
        "amount": 750000
      }
    ],
    "subtotal": 750000,
    "tax_rate": 0.075,
    "tax_rate_percentage": 7.5,
    "tax_amount": 56250,
    "total": 806250,
    "currency": "NGN"
  },
  "text_output": "--- QUOTATION ---\n..."
}
```

**Note on Rate Fields:**
- AI returns rates as percentages (7.5 for 7.5%)
- Backend converts to decimals for calculations (0.075)
- Both formats stored in response for different uses:
  - Use `tax_rate` and `delivery_rate` (decimals) for calculations
  - Use `tax_rate_percentage` and `delivery_rate_percentage` for display

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
google-genai>=0.2.0       # Google Gemini API client (new package)
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

**Note:** The free tier on Render may spin down after inactivity. First request after inactivity may take 30-60 seconds. See "Keeping the Server Awake (Free Tier)" below to prevent this.

### Keeping the Server Awake (Free Tier)

Render's free tier spins down your service after 15 minutes of inactivity. To keep your API running 24/7 for free, use [UptimeRobot](https://uptimerobot.com) to ping your health endpoint:

**How It Works:**

1. Render provides 750 free hours per month (31.25 days) - enough for full-time operation
2. UptimeRobot pings your `/health` endpoint every 5 minutes
3. This keeps Render thinking the app is active, preventing shutdown
4. Your API stays responsive without manual wake-up delays

**Setup Steps:**

1. **Deploy your service to Render** (follow steps above)
   - Note your service URL: `https://your-service-name.onrender.com`

2. **Sign up for UptimeRobot** (free plan)
   - Go to [uptimerobot.com](https://uptimerobot.com)
   - Create a free account

3. **Create a Monitor**
   - Click "+ Add New Monitor"
   - Monitor Type: `HTTP(s)`
   - Friendly Name: `Quotla API Health Check`
   - URL: `https://your-service-name.onrender.com/health`
   - Monitoring Interval: `5 minutes`
   - Click "Create Monitor"

4. **Verify It's Working**

   ```bash
   # Check your health endpoint
   curl https://your-service-name.onrender.com/health
   # Expected: {"status": "healthy"}
   ```

**Benefits:**

- ✅ 24/7 uptime on free tier
- ✅ No cold starts or 30-60 second delays
- ✅ No manual intervention needed
- ✅ Free monitoring dashboard
- ✅ Email alerts if service goes down

**Free Tier Limits:**

- Render: 750 hours/month per service (31.25 days)
- UptimeRobot: Up to 50 monitors on free plan
- Result: Completely free, always-on API

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
