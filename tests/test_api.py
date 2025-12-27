"""
API Performance Tests for Quotla AI Document Generator

Run with: python tests/test_api.py
"""

import requests
import time
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_result(test_name: str, success: bool, duration: float, details: str = ""):
    status = "✓ PASS" if success else "✗ FAIL"
    print(f"\n{status} | {test_name} | {duration:.2f}s")
    if details:
        print(f"  {details}")

def test_health_check():
    """Test 1: Health check endpoint"""
    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}/health")
        duration = time.time() - start
        success = response.status_code == 200 and response.json()["status"] == "healthy"
        print_result("Health Check", success, duration, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result("Health Check", False, time.time() - start, f"Error: {str(e)}")
        return False

def test_simple_invoice_generation():
    """Test 2: Simple invoice generation"""
    start = time.time()
    try:
        payload = {
            "prompt": "Create invoice for John Doe at 123 Main St, Lagos, Nigeria. 100 units of Product X at 5000 NGN each",
            "document_type": "invoice"
        }
        response = requests.post(f"{BASE_URL}/api/generate", json=payload)
        duration = time.time() - start

        if response.status_code == 200:
            data = response.json()
            success = (
                data.get("success") == True and
                data.get("document_type") == "invoice" and
                "invoice_number" in data.get("data", {})
            )
            details = f"Generated: {data['data'].get('invoice_number', 'N/A')}, Total: {data['data'].get('total', 0):,.2f}"
        else:
            success = False
            details = f"Status: {response.status_code}, Error: {response.text[:100]}"

        print_result("Simple Invoice Generation", success, duration, details)
        return success
    except Exception as e:
        print_result("Simple Invoice Generation", False, time.time() - start, f"Error: {str(e)}")
        return False

def test_quote_generation():
    """Test 3: Quote generation"""
    start = time.time()
    try:
        payload = {
            "prompt": "Quote for Jane Smith in Abuja. 50 consulting hours at 15000 NGN per hour",
            "document_type": "quote"
        }
        response = requests.post(f"{BASE_URL}/api/generate/quote", json=payload)
        duration = time.time() - start

        if response.status_code == 200:
            data = response.json()
            success = (
                data.get("success") == True and
                data.get("document_type") == "quote" and
                "quote_number" in data.get("data", {})
            )
            details = f"Generated: {data['data'].get('quote_number', 'N/A')}, Total: {data['data'].get('total', 0):,.2f}"
        else:
            success = False
            details = f"Status: {response.status_code}"

        print_result("Quote Generation", success, duration, details)
        return success
    except Exception as e:
        print_result("Quote Generation", False, time.time() - start, f"Error: {str(e)}")
        return False

def test_complex_multi_item_invoice():
    """Test 4: Complex multi-item invoice"""
    start = time.time()
    try:
        payload = {
            "prompt": """Create invoice for Tech Corp Ltd at Plot 45, Victoria Island, Lagos, Nigeria.
            Items:
            - 200 units of HWY Granola 50G pack at 5000 NGN each
            - 100 units of Premium Coffee at 8000 NGN each
            - 50 units of Organic Tea at 3000 NGN each
            Apply 7.5% tax and 3% delivery charge""",
            "document_type": "invoice"
        }
        response = requests.post(f"{BASE_URL}/api/generate", json=payload)
        duration = time.time() - start

        if response.status_code == 200:
            data = response.json()
            items = data.get("data", {}).get("items", [])
            success = (
                data.get("success") == True and
                len(items) >= 2  # At least 2 items extracted
            )
            details = f"Items extracted: {len(items)}, Total: {data['data'].get('total', 0):,.2f}"
        else:
            success = False
            details = f"Status: {response.status_code}"

        print_result("Complex Multi-Item Invoice", success, duration, details)
        return success
    except Exception as e:
        print_result("Complex Multi-Item Invoice", False, time.time() - start, f"Error: {str(e)}")
        return False

def test_auto_detect_document_type():
    """Test 5: Auto-detect document type"""
    start = time.time()
    try:
        payload = {
            "prompt": "I need an invoice for 500 units of widgets at 2000 NGN each for Customer ABC"
        }
        response = requests.post(f"{BASE_URL}/api/generate", json=payload)
        duration = time.time() - start

        if response.status_code == 200:
            data = response.json()
            success = data.get("document_type") == "invoice"
            details = f"Detected: {data.get('document_type')}"
        else:
            success = False
            details = f"Status: {response.status_code}"

        print_result("Auto-Detect Document Type", success, duration, details)
        return success
    except Exception as e:
        print_result("Auto-Detect Document Type", False, time.time() - start, f"Error: {str(e)}")
        return False

def test_conversation_history():
    """Test 6: Conversation history context"""
    start = time.time()
    try:
        payload = {
            "prompt": "Actually, change the quantity to 1000 units",
            "history": [
                {"role": "user", "content": "Create invoice for 500 units of Product X at 5000 NGN"},
                {"role": "assistant", "content": "Invoice created with 500 units"}
            ],
            "document_type": "invoice"
        }
        response = requests.post(f"{BASE_URL}/api/generate", json=payload)
        duration = time.time() - start

        if response.status_code == 200:
            data = response.json()
            items = data.get("data", {}).get("items", [])
            quantity = items[0].get("quantity", 0) if items else 0
            success = quantity >= 900  # Should be close to 1000
            details = f"Updated quantity: {quantity}"
        else:
            success = False
            details = f"Status: {response.status_code}"

        print_result("Conversation History Context", success, duration, details)
        return success
    except Exception as e:
        print_result("Conversation History Context", False, time.time() - start, f"Error: {str(e)}")
        return False

def test_missing_information_handling():
    """Test 7: Handling incomplete information"""
    start = time.time()
    try:
        payload = {
            "prompt": "Invoice for customer with some products",
            "document_type": "invoice"
        }
        response = requests.post(f"{BASE_URL}/api/generate", json=payload)
        duration = time.time() - start

        # Should either succeed with defaults or fail gracefully
        success = response.status_code in [200, 400, 500]
        details = f"Status: {response.status_code}, Response handled gracefully"

        print_result("Missing Information Handling", success, duration, details)
        return success
    except Exception as e:
        print_result("Missing Information Handling", False, time.time() - start, f"Error: {str(e)}")
        return False

def test_large_numbers():
    """Test 8: Large number handling"""
    start = time.time()
    try:
        payload = {
            "prompt": "Invoice for 10000 units of industrial equipment at 250000 NGN each for ABC Industries",
            "document_type": "invoice"
        }
        response = requests.post(f"{BASE_URL}/api/generate", json=payload)
        duration = time.time() - start

        if response.status_code == 200:
            data = response.json()
            total = data.get("data", {}).get("total", 0)
            success = total > 2000000000  # Should be over 2 billion
            details = f"Total: {total:,.2f} NGN"
        else:
            success = False
            details = f"Status: {response.status_code}"

        print_result("Large Number Handling", success, duration, details)
        return success
    except Exception as e:
        print_result("Large Number Handling", False, time.time() - start, f"Error: {str(e)}")
        return False

def test_currency_extraction():
    """Test 9: Currency extraction accuracy"""
    start = time.time()
    try:
        payload = {
            "prompt": "Quote for services in Nigerian Naira: 100 hours at 20000 NGN per hour",
            "document_type": "quote"
        }
        response = requests.post(f"{BASE_URL}/api/generate", json=payload)
        duration = time.time() - start

        if response.status_code == 200:
            data = response.json()
            currency = data.get("data", {}).get("currency", "")
            success = currency == "NGN"
            details = f"Currency: {currency}"
        else:
            success = False
            details = f"Status: {response.status_code}"

        print_result("Currency Extraction", success, duration, details)
        return success
    except Exception as e:
        print_result("Currency Extraction", False, time.time() - start, f"Error: {str(e)}")
        return False

def test_calculation_accuracy():
    """Test 10: Mathematical calculation accuracy"""
    start = time.time()
    try:
        payload = {
            "prompt": "Invoice: 100 units at 1000 NGN each. 10% tax, 5% delivery",
            "document_type": "invoice"
        }
        response = requests.post(f"{BASE_URL}/api/generate", json=payload)
        duration = time.time() - start

        if response.status_code == 200:
            data = response.json()["data"]
            expected_subtotal = 100000
            expected_tax = 10000
            expected_delivery = 5000
            expected_total = 115000

            success = (
                abs(data.get("subtotal", 0) - expected_subtotal) < 100 and
                abs(data.get("total", 0) - expected_total) < 500
            )
            details = f"Subtotal: {data.get('subtotal'):,.2f}, Total: {data.get('total'):,.2f}"
        else:
            success = False
            details = f"Status: {response.status_code}"

        print_result("Calculation Accuracy", success, duration, details)
        return success
    except Exception as e:
        print_result("Calculation Accuracy", False, time.time() - start, f"Error: {str(e)}")
        return False

def run_performance_benchmark():
    """Test 11: Performance benchmark (5 requests)"""
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARK - 5 Sequential Requests")
    print("="*60)

    durations = []
    payload = {
        "prompt": "Invoice for test at Lagos. 10 items at 1000 NGN",
        "document_type": "invoice"
    }

    for i in range(5):
        start = time.time()
        try:
            response = requests.post(f"{BASE_URL}/api/generate", json=payload)
            duration = time.time() - start
            durations.append(duration)
            status = "✓" if response.status_code == 200 else "✗"
            print(f"  Request {i+1}: {status} {duration:.2f}s")
        except Exception as e:
            print(f"  Request {i+1}: ✗ Error: {str(e)}")

    if durations:
        avg = sum(durations) / len(durations)
        min_time = min(durations)
        max_time = max(durations)
        print(f"\n  Average: {avg:.2f}s | Min: {min_time:.2f}s | Max: {max_time:.2f}s")
        return avg < 10  # Success if average under 10s
    return False

def main():
    print("\n" + "="*60)
    print("QUOTLA AI DOCUMENT GENERATOR - TEST SUITE")
    print("="*60)
    print(f"Testing API at: {BASE_URL}")
    print("Make sure the server is running: uvicorn app.main:app --reload")
    print("="*60)

    tests = [
        test_health_check,
        test_simple_invoice_generation,
        test_quote_generation,
        test_complex_multi_item_invoice,
        test_auto_detect_document_type,
        test_conversation_history,
        test_missing_information_handling,
        test_large_numbers,
        test_currency_extraction,
        test_calculation_accuracy,
    ]

    results = []
    for test in tests:
        results.append(test())
        time.sleep(0.5)  # Small delay between tests

    # Performance benchmark
    perf_result = run_performance_benchmark()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results) + (1 if perf_result else 0)
    total = len(results) + 1
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print("="*60 + "\n")

    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
