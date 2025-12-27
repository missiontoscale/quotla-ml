"""
Image Upload Test for Quotla AI

Run with: python tests/test_image_upload.py
"""

import requests
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def create_test_image():
    """Create a simple test image"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # Create invoice-like image
        img = Image.new('RGB', (600, 400), color='white')
        draw = ImageDraw.Draw(img)

        # Draw text
        text = """
        INVOICE #INV001

        Bill To: Test Customer
        Address: Lagos, Nigeria

        Item: Test Product
        Qty: 100
        Price: 5000 NGN

        Total: 500,000 NGN
        """

        draw.text((50, 50), text, fill='black')

        test_img_path = Path("tests/test_invoice.jpg")
        test_img_path.parent.mkdir(exist_ok=True)
        img.save(test_img_path)
        return test_img_path
    except ImportError:
        print("PIL not installed. Skipping test image creation.")
        return None

def test_image_upload_endpoint():
    """Test image upload with generated test image"""
    print("\n" + "="*60)
    print("IMAGE UPLOAD TEST")
    print("="*60)

    test_img = create_test_image()
    if not test_img:
        print("✗ SKIP | Could not create test image (PIL not installed)")
        return False

    start = time.time()
    try:
        with open(test_img, 'rb') as f:
            files = {'image': ('test_invoice.jpg', f, 'image/jpeg')}
            data = {
                'prompt': 'Extract invoice information from this image',
                'document_type': 'invoice'
            }

            response = requests.post(
                f"{BASE_URL}/api/generate/with-image",
                files=files,
                data=data
            )

        duration = time.time() - start

        if response.status_code == 200:
            result = response.json()
            success = result.get("success") == True
            details = f"Duration: {duration:.2f}s | Invoice: {result.get('data', {}).get('invoice_number', 'N/A')}"
            print(f"✓ PASS | Image Upload Test | {details}")
        else:
            print(f"✗ FAIL | Image Upload Test | Status: {response.status_code}")
            print(f"  Error: {response.text[:200]}")
            success = False

        return success
    except Exception as e:
        print(f"✗ FAIL | Image Upload Test | Error: {str(e)}")
        return False

def test_image_upload_with_real_file():
    """Test with user-provided image file"""
    print("\n" + "="*60)
    print("MANUAL IMAGE UPLOAD TEST")
    print("="*60)
    print("To test with your own invoice image:")
    print(f"  curl -X POST {BASE_URL}/api/generate/with-image \\")
    print(f"    -F 'prompt=Extract invoice from this image' \\")
    print(f"    -F 'image=@/path/to/your/invoice.jpg' \\")
    print(f"    -F 'document_type=invoice'")
    print("="*60 + "\n")

if __name__ == "__main__":
    print("\nMake sure server is running: uvicorn app.main:app --reload\n")

    result1 = test_image_upload_endpoint()
    test_image_upload_with_real_file()

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")
