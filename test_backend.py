"""
Quick diagnostic script to test the backend fixes
Run this to verify the tax calculation fix is working
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import _enrich_data

# Test case from your error report
test_data = {
    "customer_name": "Jane Smith",
    "city": "Abuja",
    "items": [
        {
            "description": "consulting hours",
            "quantity": 50,
            "unit_price": 15000,
            "amount": 750000
        }
    ],
    "tax_rate": 8,  # AI returns as percentage
    "currency": "NGN"
}

print("=" * 60)
print("TESTING BACKEND FIX - Tax Calculation")
print("=" * 60)

print("\n1. Input data (as AI provides it):")
print(f"   Tax rate from AI: {test_data['tax_rate']} (percentage)")
print(f"   Subtotal: {750000:,} NGN")

print("\n2. Running _enrich_data for QUOTE...")
enriched_quote = _enrich_data(test_data.copy(), 'quote')

print("\n3. Quote Results:")
print(f"   ✓ tax_rate (decimal): {enriched_quote['tax_rate']}")
print(f"   ✓ tax_rate_percentage: {enriched_quote['tax_rate_percentage']}")
print(f"   ✓ tax_amount: {enriched_quote['tax_amount']:,.2f} NGN")
print(f"   ✓ total: {enriched_quote['total']:,.2f} NGN")

# Verify calculations
expected_tax = 750000 * 0.08
expected_total = 750000 + expected_tax

if enriched_quote['tax_amount'] == expected_tax:
    print(f"   ✅ Tax calculation CORRECT: {expected_tax:,.2f} NGN")
else:
    print(f"   ❌ Tax calculation WRONG: Expected {expected_tax:,.2f}, got {enriched_quote['tax_amount']:,.2f}")

print("\n4. Running _enrich_data for INVOICE...")
enriched_invoice = _enrich_data(test_data.copy(), 'invoice')

print("\n5. Invoice Results:")
print(f"   ✓ tax_rate (decimal): {enriched_invoice['tax_rate']}")
print(f"   ✓ tax_rate_percentage: {enriched_invoice['tax_rate_percentage']}")
print(f"   ✓ tax_amount: {enriched_invoice['tax_amount']:,.2f} NGN")
print(f"   ✓ delivery_rate (decimal): {enriched_invoice['delivery_rate']}")
print(f"   ✓ delivery_rate_percentage: {enriched_invoice['delivery_rate_percentage']}")
print(f"   ✓ delivery_amount: {enriched_invoice['delivery_amount']:,.2f} NGN")
print(f"   ✓ total: {enriched_invoice['total']:,.2f} NGN")

# Verify calculations
expected_delivery = 750000 * 0.03
expected_invoice_total = 750000 + expected_tax + expected_delivery

if enriched_invoice['tax_amount'] == expected_tax:
    print(f"   ✅ Tax calculation CORRECT: {expected_tax:,.2f} NGN")
else:
    print(f"   ❌ Tax calculation WRONG: Expected {expected_tax:,.2f}, got {enriched_invoice['tax_amount']:,.2f}")

if enriched_invoice['delivery_amount'] == expected_delivery:
    print(f"   ✅ Delivery calculation CORRECT: {expected_delivery:,.2f} NGN")
else:
    print(f"   ❌ Delivery calculation WRONG: Expected {expected_delivery:,.2f}, got {enriched_invoice['delivery_amount']:,.2f}")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

quote_pass = enriched_quote['tax_amount'] == expected_tax
invoice_pass = (enriched_invoice['tax_amount'] == expected_tax and
                enriched_invoice['delivery_amount'] == expected_delivery)

if quote_pass and invoice_pass:
    print("✅ ALL TESTS PASSED - Backend fix is working correctly!")
    print("\nExpected values:")
    print(f"  Quote - Tax (8%): 60,000 NGN, Total: 810,000 NGN")
    print(f"  Invoice - Tax (8%): 60,000 NGN, Delivery (3%): 22,500 NGN, Total: 832,500 NGN")
else:
    print("❌ TESTS FAILED - There are still issues")
    if not quote_pass:
        print("  - Quote tax calculation is wrong")
    if not invoice_pass:
        print("  - Invoice tax/delivery calculation is wrong")

print("=" * 60)
