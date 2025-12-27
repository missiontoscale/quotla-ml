import os
import json
from pathlib import Path
from typing import List, Dict, Any
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
import io
import base64
from docx import Document
import PyPDF2
import pdfplumber

class AIService:
    def __init__(self):
        self.provider = os.getenv('AI_PROVIDER', 'openai')
        self.fallback_provider = os.getenv('FALLBACK_AI_PROVIDER', 'gemini')
        self.prompts_dir = Path(__file__).parent / "prompts"

        # Initialize primary provider
        if self.provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            self.client = OpenAI(api_key=api_key) if api_key else None
        elif self.provider == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            self.client = Anthropic(api_key=api_key) if api_key else None
        elif self.provider == 'gemini':
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
            self.client = 'configured' if api_key else None

        # Initialize fallback provider
        self._initialize_fallback()

    def _initialize_fallback(self):
        """Initialize fallback AI provider"""
        self.fallback_client = None
        if self.fallback_provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.fallback_client = OpenAI(api_key=api_key)
        elif self.fallback_provider == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.fallback_client = Anthropic(api_key=api_key)
        elif self.fallback_provider == 'gemini':
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.fallback_client = 'configured'

    def _load_prompt(self, document_type: str) -> str:
        """Load prompt from file"""
        prompt_file = self.prompts_dir / f"{document_type}_prompt.txt"
        if prompt_file.exists():
            return prompt_file.read_text()
        return self._get_default_prompt(document_type)

    def _get_default_prompt(self, document_type: str) -> str:
        """Fallback if prompt file doesn't exist"""
        return f"""Extract business document information from user requests. Return ONLY valid JSON, no markdown, no explanations.

For {document_type}:
{{
  "customer_name": "string",
  "address": "string",
  "city": "string",
  "country": "string",
  "items": [...],
  "subtotal": number,
  "tax_rate": number,
  "tax_amount": number,
  "total": number,
  "currency": "NGN"
}}"""

    async def extract_document_data(self, prompt: str, history: List[Dict], document_type: str) -> Dict[str, Any]:
        """Extract structured data from user prompt using AI with fallback support"""
        try:
            return await self._extract_with_provider(prompt, history, document_type, self.provider, self.client)
        except Exception as e:
            # Try fallback provider if available
            if self.fallback_client and self.fallback_provider != self.provider:
                print(f"Primary provider ({self.provider}) failed: {e}. Trying fallback ({self.fallback_provider})...")
                try:
                    return await self._extract_with_provider(prompt, history, document_type, self.fallback_provider, self.fallback_client)
                except Exception as fallback_error:
                    raise Exception(f"Both providers failed. Primary ({self.provider}): {e}, Fallback ({self.fallback_provider}): {fallback_error}")
            raise

    async def _extract_with_provider(self, prompt: str, history: List[Dict], document_type: str, provider: str, client: Any) -> Dict[str, Any]:
        """Extract data using a specific provider"""
        system_prompt = self._load_prompt(document_type)

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        if provider == 'openai':
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.1,
                max_tokens=1500
            )
            content = response.choices[0].message.content.strip()

        elif provider == 'anthropic':
            system_msg = messages[0]['content']
            user_messages = messages[1:]
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                temperature=0.1,
                system=system_msg,
                messages=user_messages
            )
            content = response.content[0].text.strip()

        elif provider == 'gemini':
            model = genai.GenerativeModel('gemini-pro')
            prompt_text = "\n\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            response = model.generate_content(
                prompt_text,
                generation_config=genai.types.GenerationConfig(temperature=0.1, max_output_tokens=1500)
            )
            content = response.text.strip()

        return self._parse_json(content)

    async def extract_with_image(self, prompt: str, image_b64: str, document_type: str) -> Dict[str, Any]:
        """Extract structured data from image using vision models"""

        system_prompt = self._load_prompt(document_type)

        if self.provider == 'openai':
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
                        ]
                    }
                ],
                temperature=0.1,
                max_tokens=1500
            )
            content = response.choices[0].message.content.strip()

        elif self.provider == 'anthropic':
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                temperature=0.1,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}}
                        ]
                    }
                ]
            )
            content = response.content[0].text.strip()

        elif self.provider == 'gemini':
            import PIL.Image
            import io
            import base64

            image_bytes = base64.b64decode(image_b64)
            image = PIL.Image.open(io.BytesIO(image_bytes))

            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(
                [system_prompt + "\n\n" + prompt, image],
                generation_config=genai.types.GenerationConfig(temperature=0.1, max_output_tokens=1500)
            )
            content = response.text.strip()

        return self._parse_json(content)

    def _extract_text_from_file(self, file_bytes: bytes, filename: str) -> str:
        """Extract text content from various file types"""
        file_ext = filename.lower().split('.')[-1]

        if file_ext == 'pdf':
            return self._extract_pdf_text(file_bytes)
        elif file_ext in ['docx', 'doc']:
            return self._extract_docx_text(file_bytes)
        elif file_ext == 'txt':
            return file_bytes.decode('utf-8', errors='ignore')
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

    def _extract_pdf_text(self, file_bytes: bytes) -> str:
        """Extract text from PDF using pdfplumber (more accurate)"""
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            # Fallback to PyPDF2 if pdfplumber fails
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
            except Exception as e2:
                raise ValueError(f"Failed to extract PDF text: {e}, {e2}")

    def _extract_docx_text(self, file_bytes: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(io.BytesIO(file_bytes))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract DOCX text: {e}")

    async def extract_from_file(self, prompt: str, file_bytes: bytes, filename: str, document_type: str) -> Dict[str, Any]:
        """Extract structured data from document file (PDF, DOCX, TXT)"""

        # Extract text from the document
        file_text = self._extract_text_from_file(file_bytes, filename)

        # Combine prompt with extracted text
        combined_prompt = f"{prompt}\n\nDocument content:\n{file_text}"

        # Use the regular extraction with the text
        system_prompt = self._load_prompt(document_type)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": combined_prompt}
        ]

        if self.provider == 'openai':
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.1,
                max_tokens=1500
            )
            content = response.choices[0].message.content.strip()

        elif self.provider == 'anthropic':
            system_msg = messages[0]['content']
            user_messages = messages[1:]
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                temperature=0.1,
                system=system_msg,
                messages=user_messages
            )
            content = response.content[0].text.strip()

        elif self.provider == 'gemini':
            model = genai.GenerativeModel('gemini-pro')
            prompt_text = "\n\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            response = model.generate_content(
                prompt_text,
                generation_config=genai.types.GenerationConfig(temperature=0.1, max_output_tokens=1500)
            )
            content = response.text.strip()

        return self._parse_json(content)

    def detect_document_type(self, prompt: str) -> Dict[str, Any]:
        """Use AI to detect document type from prompt"""
        if self.provider == 'openai':
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )
            content = response.choices[0].message.content.strip()

        elif self.provider == 'anthropic':
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.content[0].text.strip()

        elif self.provider == 'gemini':
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.1, max_output_tokens=200)
            )
            content = response.text.strip()

        return self._parse_json(content)

    def _parse_json(self, content: str) -> Dict[str, Any]:
        """Parse JSON from AI response"""
        content = content.strip()

        # Check if content is empty
        if not content:
            raise ValueError("AI returned empty response")

        # Remove markdown code blocks
        if content.startswith('```'):
            lines = content.split('\n')
            content = '\n'.join(lines[1:-1]) if len(lines) > 2 else content
            content = content.replace('```json', '').replace('```', '').strip()

        # Try to find JSON in the content if it has explanatory text
        if not content.startswith('{') and not content.startswith('['):
            # Look for JSON object in the content
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                content = content[start_idx:end_idx+1]
            else:
                raise ValueError(f"No JSON found in AI response. Content: {content[:200]}")

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {e}. Content: {content[:200]}")
