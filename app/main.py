from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from app.ai_service import AIService
from app.export_service import ExportService
import base64
import os

load_dotenv()

# Configuration: Business logic defaults
DEFAULT_TAX_RATE = float(os.getenv('DEFAULT_TAX_RATE', '7.5'))  # 7.5% default
DEFAULT_DELIVERY_RATE = float(os.getenv('DEFAULT_DELIVERY_RATE', '3.0'))  # 3% default

app = FastAPI(
    title="Quotla AI Document Generator",
    description="""
## AI-Powered Invoice & Quote Generator

Convert natural language descriptions, files, or images into structured business documents using AI.

### 🎯 Unified API Design

**One endpoint to rule them all**: `/api/generate` accepts text prompts, file uploads, or images - no need for separate endpoints!

### Key Features

* **Universal Input**: Text, PDF, DOCX, TXT, or images (JPEG, PNG, etc.)
* **Natural Language Processing**: Describe documents in plain English
* **Multi-Provider AI**: OpenAI GPT-4, Anthropic Claude, or Google Gemini
* **Vision AI**: Process scanned receipts and invoice photos
* **Multiple Export Formats**: JSON, PDF, DOCX, PNG
* **Conversation History**: Multi-turn conversations to refine documents
* **Auto-Detection**: Automatically determines if input is an invoice or quote
* **Smart Currency Detection**: Prompts user if currency not specified

### Supported Document Types

* **Invoices**: Full invoicing with tax and delivery charges
* **Quotes**: Professional quotations with tax calculations

### AI Models Used

* **Text Models**: gpt-4, claude-3-5-sonnet-20241022, gemini-pro
* **Vision Models**: gpt-4o, claude-3-5-sonnet-20241022, gemini-1.5-flash

Configure via `AI_PROVIDER` environment variable.

### Quick Start

Use `/api/generate` for everything:
- Text only: `{"prompt": "Invoice for John at Lagos, 100 units at 5000 NGN"}`
- With file: Upload file with `file` parameter
- Export directly: Use `/api/export/pdf`, `/api/export/docx`, or `/api/export/png`
    """,
    version="2.0.0",
    contact={
        "name": "Quotla Support",
        "url": "https://github.com/missiontoscale/quotla",
    },
    license_info={
        "name": "See LICENSE file",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_service = AIService()
export_service = ExportService()

# Models removed - using Form parameters for unified endpoint compatibility

@app.get(
    "/",
    tags=["General"],
    summary="API Root",
    description="Returns basic API information and version."
)
async def root():
    return {"message": "Quotla AI API", "version": "2.0.0"}

@app.get(
    "/health",
    tags=["General"],
    summary="Health Check",
    description="Check if the API server is running and healthy. Use this for monitoring and uptime checks."
)
async def health():
    return {"status": "healthy"}

@app.post(
    "/api/generate",
    tags=["Document Generation"],
    summary="Universal Document Generator",
    description="""
Generate structured business documents from text prompts, files, or images - all in one unified endpoint.

**Input Methods:**
1. **Text Prompt Only**: Just provide a prompt in the request body
2. **File Upload**: Include a file (PDF, DOCX, TXT) with optional prompt
3. **Image Upload**: Include an image (JPEG, PNG, etc.) with optional prompt

**Supported File Types:**
- Documents: PDF (.pdf), Word (.docx, .doc), Text (.txt)
- Images: JPEG, PNG, GIF, BMP, WEBP (uses Vision AI)

**Features:**
- AI-powered document type detection (invoice vs quote)
- Intelligent currency detection - prompts if not specified
- Multi-turn conversation support via history
- Automatic calculations and enrichment
- Works with text, documents, and images seamlessly

**AI Models:**
- Text: GPT-4, Claude 3.5 Sonnet, or Gemini Pro
- Vision: GPT-4o, Claude 3.5 Sonnet, or Gemini 1.5 Flash

**Example Text Prompt:**
```json
{
  "prompt": "Invoice for John Doe at Lagos. 100 units at 5000 NGN each"
}
```

**Example with File Upload:**
Use multipart/form-data with:
- `prompt`: "Extract invoice data from this PDF"
- `file`: [uploaded file]
- `document_type`: "invoice" (optional)

**Response:**
- `success`: Boolean
- `document_type`: Detected/specified type
- `data`: Structured document data
- `text_output`: Formatted text
- `needs_currency`: Boolean (if currency required)
    """,
    response_description="Structured document data with enriched fields and calculations"
)
async def generate_document(
    prompt: str = Form(None, description="Text prompt or instructions for extraction"),
    file: Optional[UploadFile] = File(None, description="Optional file upload (PDF, DOCX, TXT, or image)"),
    document_type: Optional[str] = Form(None, description="Force type: 'invoice' or 'quote' (auto-detected if omitted)"),
    history: Optional[str] = Form(None, description="JSON string of conversation history")
):
    try:
        # Parse history if provided
        parsed_history = []
        if history:
            import json
            try:
                parsed_history = json.loads(history)
            except:
                pass

        # If no file provided, treat as text-only request
        if not file:
            # Prompt is required for text-only
            if not prompt:
                raise HTTPException(status_code=400, detail="Either 'prompt' or 'file' must be provided")

            # Use AI to detect document type if not specified
            detection_result = document_type or _ai_detect_type(prompt)

            # Handle conversational requests
            if isinstance(detection_result, dict) and detection_result.get('document_type') == 'conversation':
                return {
                    "success": True,
                    "document_type": "conversation",
                    "message": detection_result.get('message', 'Hello! I help generate invoices and quotes. Just describe what you need!'),
                    "text_output": detection_result.get('message', 'Hello! I help generate invoices and quotes. Just describe what you need!')
                }

            # Extract document type from detection result
            doc_type = detection_result if isinstance(detection_result, str) else detection_result.get('document_type', 'quote')
            data = await ai_service.extract_document_data(prompt, parsed_history, doc_type)

        else:
            # File upload path
            file_bytes = await file.read()
            filename = file.filename or "document"
            file_ext = filename.lower().split('.')[-1]

            # Use prompt or default extraction instruction
            extraction_prompt = prompt or "Extract all document data from this file"

            # Detect document type
            doc_type = document_type or _ai_detect_type(extraction_prompt)
            if isinstance(doc_type, dict):
                doc_type = doc_type.get('document_type', 'quote')

            # Determine file type and process accordingly
            image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
            document_extensions = ['pdf', 'docx', 'doc', 'txt']

            if file_ext in image_extensions:
                # Use vision AI for images
                image_b64 = base64.b64encode(file_bytes).decode('utf-8')
                data = await ai_service.extract_with_image(extraction_prompt, image_b64, doc_type)
            elif file_ext in document_extensions:
                # Extract text and process
                data = await ai_service.extract_from_file(extraction_prompt, file_bytes, filename, doc_type)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file_ext}. Supported: PDF, DOCX, TXT, JPEG, PNG"
                )

        # Check if currency is missing
        if not data.get('currency'):
            return {
                "success": False,
                "needs_currency": True,
                "message": "Please specify the currency for this document (e.g., NGN, USD, EUR, GBP)",
                "detected_document_type": doc_type,
                "partial_data": data
            }

        enriched = _enrich_data(data, doc_type)
        text_output = _format_text(enriched, doc_type)

        return {
            "success": True,
            "document_type": doc_type,
            "data": enriched,
            "text_output": text_output
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/api/generate/invoice",
    tags=["Document Generation (Legacy)"],
    summary="[DEPRECATED] Generate Invoice",
    description="""
**⚠️ DEPRECATED: Use `/api/generate` with `document_type="invoice"` instead.**

Legacy endpoint for backward compatibility.

**Same as `/api/generate` but:**
- Always generates an invoice (never a quote)
- Includes delivery charges (3% of subtotal)
- Uses invoice numbering format: INV{timestamp}

**Example:**
```json
{
  "prompt": "John at Lagos for 500 units at 5000 NGN"
}
```
    """,
    response_description="Invoice data with tax and delivery calculations",
    deprecated=True
)
async def generate_invoice(
    prompt: str = Form(...),
    history: Optional[str] = Form(None)
):
    return await generate_document(prompt=prompt, file=None, document_type="invoice", history=history)

@app.post(
    "/api/generate/quote",
    tags=["Document Generation (Legacy)"],
    summary="[DEPRECATED] Generate Quote",
    description="""
**⚠️ DEPRECATED: Use `/api/generate` with `document_type="quote"` instead.**

Legacy endpoint for backward compatibility.

**Same as `/api/generate` but:**
- Always generates a quote (never an invoice)
- No delivery charges (quotes only include tax)
- Uses quote numbering format: QT{timestamp}

**Example:**
```json
{
  "prompt": "Jane Smith in Abuja. 50 consulting hours at 15000 NGN per hour"
}
```
    """,
    response_description="Quote data with tax calculations (no delivery)",
    deprecated=True
)
async def generate_quote(
    prompt: str = Form(...),
    history: Optional[str] = Form(None)
):
    return await generate_document(prompt=prompt, file=None, document_type="quote", history=history)

@app.post(
    "/api/generate/with-file",
    tags=["Document Generation (Legacy)"],
    summary="[DEPRECATED] Generate from File",
    description="""
**⚠️ DEPRECATED: Use `/api/generate` with the `file` parameter instead.**

Legacy endpoint for backward compatibility.

Simply use the main `/api/generate` endpoint and include your file - it automatically detects whether you're uploading text, documents, or images.
    """,
    response_description="Extracted document data from file",
    deprecated=True
)
async def generate_with_file(
    prompt: str = Form(..., description="Instructions for extracting data from the file"),
    file: UploadFile = File(..., description="Document or image file (PDF, DOCX, TXT, JPEG, PNG, etc.)"),
    document_type: Optional[str] = Form(None, description="Force document type: 'invoice' or 'quote' (auto-detected if omitted)")
):
    return await generate_document(prompt=prompt, file=file, document_type=document_type, history=None)

@app.post(
    "/api/export/pdf",
    tags=["Export Formats"],
    summary="Export as PDF",
    description="""
Generate document from text, files, or images and download as professionally formatted PDF.

**Input Methods:**
- Text prompt only
- File upload (PDF, DOCX, TXT, images)
- Combination of prompt + file

**Features:**
- Professional layout with headers and branding
- Formatted tables for line items
- Color-coded sections (header, items, totals)
- Automatic calculations displayed
- Currency formatting with proper alignment
- Letter-sized pages (8.5" × 11")

**Use Cases:**
- Print-ready invoices
- Professional client delivery
- Accounting records
- Archive storage

**Response:**
Binary PDF file with appropriate filename (e.g., INV20241201.pdf)
    """,
    response_description="Binary PDF file",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Successfully generated PDF document"
        }
    }
)
async def export_pdf(
    prompt: str = Form(None),
    file: Optional[UploadFile] = File(None),
    document_type: Optional[str] = Form(None),
    history: Optional[str] = Form(None)
):
    try:
        enriched, doc_type = await _generate_document_data(prompt, file, document_type, history)
        pdf_buffer = export_service.generate_pdf(enriched, doc_type)
        filename = f"{enriched.get('invoice_number' if doc_type == 'invoice' else 'quote_number', 'document')}.pdf"

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/api/export/docx",
    tags=["Export Formats"],
    summary="Export as DOCX",
    description="""
Generate document from text, files, or images and download as Microsoft Word document.

**Input Methods:**
- Text prompt only
- File upload (PDF, DOCX, TXT, images)
- Combination of prompt + file

**Features:**
- Editable Word document format (.docx)
- Professional table styling with grid borders
- Bold headers and emphasis on totals
- Standard Word compatibility
- Preserves formatting for easy customization
- Ready for further editing and branding

**Use Cases:**
- Editable templates
- Custom branding additions
- Company letterhead integration
- Further modifications needed

**Benefits:**
- Fully editable in Microsoft Word, Google Docs, LibreOffice
- Add logos, signatures, notes after generation
- Customize colors and fonts
- Easy to adapt to company style guides

**Response:**
Binary DOCX file with appropriate filename (e.g., INV20241201.docx)
    """,
    response_description="Binary DOCX file",
    responses={
        200: {
            "content": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document": {}},
            "description": "Successfully generated DOCX document"
        }
    }
)
async def export_docx(
    prompt: str = Form(None),
    file: Optional[UploadFile] = File(None),
    document_type: Optional[str] = Form(None),
    history: Optional[str] = Form(None)
):
    try:
        enriched, doc_type = await _generate_document_data(prompt, file, document_type, history)
        docx_buffer = export_service.generate_docx(enriched, doc_type)
        filename = f"{enriched.get('invoice_number' if doc_type == 'invoice' else 'quote_number', 'document')}.docx"

        return StreamingResponse(
            docx_buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/api/export/png",
    tags=["Export Formats"],
    summary="Export as PNG Image",
    description="""
Generate document from text, files, or images and download as PNG image.

**Input Methods:**
- Text prompt only
- File upload (PDF, DOCX, TXT, images)
- Combination of prompt + file

**Image Specifications:**
- Resolution: 800×1000 pixels
- Format: PNG (lossless)
- Background: Clean white
- Professional typography
- High-quality rendering

**Use Cases:**
- Social media sharing
- WhatsApp/messaging apps
- Quick previews
- Mobile-friendly format
- Email attachments
- Web display

**Benefits:**
- Universal compatibility
- No special software needed to view
- Easy to share on mobile
- Perfect for instant messaging
- Lightweight file size
- Screenshot-like appearance

**Response:**
Binary PNG image file with appropriate filename (e.g., INV20241201.png)
    """,
    response_description="Binary PNG image file",
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "Successfully generated PNG image"
        }
    }
)
async def export_png(
    prompt: str = Form(None),
    file: Optional[UploadFile] = File(None),
    document_type: Optional[str] = Form(None),
    history: Optional[str] = Form(None)
):
    try:
        enriched, doc_type = await _generate_document_data(prompt, file, document_type, history)
        png_buffer = export_service.generate_image(enriched, doc_type)
        filename = f"{enriched.get('invoice_number' if doc_type == 'invoice' else 'quote_number', 'document')}.png"

        return StreamingResponse(
            png_buffer,
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _detect_type(prompt: str) -> str:
    """Simple keyword-based detection (fallback)"""
    lower = prompt.lower()
    return 'invoice' if 'invoice' in lower or 'bill' in lower else 'quote'

def _ai_detect_type(prompt: str):
    """AI-powered document type detection based on context - returns dict for conversation or string for doc type"""
    try:
        detection_prompt_file = ai_service.prompts_dir / "document_type_detection.txt"
        if detection_prompt_file.exists():
            detection_template = detection_prompt_file.read_text()
            detection_prompt = detection_template.replace("{prompt}", prompt)

            # Use AI to detect document type
            result = ai_service.detect_document_type(detection_prompt)

            # If it's a conversation, return the full dict with message
            if result.get("document_type") == "conversation":
                return result

            # Otherwise return just the document type string
            return result.get("document_type", "quote")
        else:
            # Fallback to simple detection
            return _detect_type(prompt)
    except Exception:
        # Fallback to simple detection on error
        return _detect_type(prompt)

def _enrich_data(data: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
    if doc_type == 'invoice':
        data['invoice_number'] = f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}"
    else:
        data['quote_number'] = f"QT{datetime.now().strftime('%Y%m%d%H%M%S')}"

    data['date'] = datetime.now().strftime('%Y-%m-%d')

    for item in data.get('items', []):
        if 'amount' not in item:
            item['amount'] = item.get('quantity', 0) * item.get('unit_price', 0)

    subtotal = sum(item.get('amount', 0) for item in data.get('items', []))
    data['subtotal'] = subtotal

    # Handle tax rate - AI returns as percentage (8 for 8%), convert to decimal
    # Use user-provided rate if available, otherwise use configured default
    tax_rate = data.get('tax_rate', 0)
    if tax_rate == 0 and subtotal > 0:
        tax_rate = DEFAULT_TAX_RATE
    # Store as decimal for calculations, but keep percentage in separate field for display
    data['tax_rate_percentage'] = tax_rate
    data['tax_rate'] = tax_rate / 100  # Convert to decimal (8 -> 0.08)
    data['tax_amount'] = subtotal * data['tax_rate']

    if doc_type == 'invoice':
        # Handle delivery rate - AI returns as percentage (3 for 3%), convert to decimal
        # Use user-provided rate if available, otherwise use configured default
        delivery_rate = data.get('delivery_rate', 0)
        if delivery_rate == 0 and subtotal > 0:
            delivery_rate = DEFAULT_DELIVERY_RATE
        data['delivery_rate_percentage'] = delivery_rate
        data['delivery_rate'] = delivery_rate / 100  # Convert to decimal (3 -> 0.03)
        data['delivery_amount'] = subtotal * data['delivery_rate']
        data['total'] = subtotal + data['tax_amount'] + data['delivery_amount']
    else:
        data['total'] = subtotal + data['tax_amount']

    # Keep currency as provided (including None/null if not specified)
    if 'currency' not in data or data['currency'] is None:
        data['currency'] = None

    return data

async def _generate_document_data(
    prompt: str,
    file: Optional[UploadFile] = None,
    document_type: Optional[str] = None,
    history: Optional[str] = None
) -> tuple[Dict[str, Any], str]:
    """Shared logic for generating document data - used by all export endpoints"""
    # Parse history if provided
    parsed_history = []
    if history:
        import json
        try:
            parsed_history = json.loads(history)
        except:
            pass

    # If no file provided, treat as text-only request
    if not file:
        if not prompt:
            raise HTTPException(status_code=400, detail="Either 'prompt' or 'file' must be provided")

        doc_type = document_type or _ai_detect_type(prompt)
        if isinstance(doc_type, dict):
            doc_type = doc_type.get('document_type', 'quote')

        data = await ai_service.extract_document_data(prompt, parsed_history, doc_type)
    else:
        # File upload path
        file_bytes = await file.read()
        filename = file.filename or "document"
        file_ext = filename.lower().split('.')[-1]

        extraction_prompt = prompt or "Extract all document data from this file"
        doc_type = document_type or _ai_detect_type(extraction_prompt)
        if isinstance(doc_type, dict):
            doc_type = doc_type.get('document_type', 'quote')

        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        document_extensions = ['pdf', 'docx', 'doc', 'txt']

        if file_ext in image_extensions:
            image_b64 = base64.b64encode(file_bytes).decode('utf-8')
            data = await ai_service.extract_with_image(extraction_prompt, image_b64, doc_type)
        elif file_ext in document_extensions:
            data = await ai_service.extract_from_file(extraction_prompt, file_bytes, filename, doc_type)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Supported: PDF, DOCX, TXT, JPEG, PNG"
            )

    # Check for currency
    if not data.get('currency'):
        raise HTTPException(
            status_code=400,
            detail="Currency not specified. Please include currency in your prompt (e.g., NGN, USD, EUR)"
        )

    enriched = _enrich_data(data, doc_type)
    return enriched, doc_type

def _format_text(data: Dict[str, Any], doc_type: str) -> str:
    items_text = "\n".join([
        f"{item['description']}\n  Qty: {item['quantity']} x {data['currency']} {item['unit_price']:,.2f} = {data['currency']} {item['amount']:,.2f}"
        for item in data['items']
    ])

    if doc_type == 'invoice':
        return f"""--- INVOICE ---
Invoice Number: {data['invoice_number']}
Date: {data['date']}

Bill To:
{data.get('customer_name', 'N/A')}
{data.get('address', 'N/A')}
{data.get('city', 'N/A')}, {data.get('country', 'N/A')}

Items:
{items_text}

Subtotal: {data['currency']} {data['subtotal']:,.2f}
Tax ({data.get('tax_rate_percentage', data['tax_rate']*100):.1f}%): {data['currency']} {data['tax_amount']:,.2f}
Delivery ({data.get('delivery_rate_percentage', data['delivery_rate']*100):.1f}%): {data['currency']} {data['delivery_amount']:,.2f}

TOTAL: {data['currency']} {data['total']:,.2f}"""
    else:
        return f"""--- QUOTATION ---
Quote Number: {data['quote_number']}
Date: {data['date']}

To:
{data.get('customer_name', 'N/A')}
{data.get('address', 'N/A')}
{data.get('city', 'N/A')}, {data.get('country', 'N/A')}

Items:
{items_text}

Subtotal: {data['currency']} {data['subtotal']:,.2f}
Tax ({data.get('tax_rate_percentage', data['tax_rate']*100):.1f}%): {data['currency']} {data['tax_amount']:,.2f}

TOTAL: {data['currency']} {data['total']:,.2f}"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
