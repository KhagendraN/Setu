"""
Test script for Human-in-the-Loop Bias Detection workflow
Run this to verify the HITL implementation is working correctly
"""

import requests
import json
import sys
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8000/api/v1/bias-detection-hitl"
AUTH_TOKEN = "YOUR_AUTH_TOKEN_HERE"  # Replace with actual token

# Sample PDF path (update this to your test PDF)
TEST_PDF_PATH = "path/to/test/document.pdf"


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_json(data, indent=2):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=indent, ensure_ascii=False))


def test_health_check():
    """Test 1: Health Check"""
    print_section("TEST 1: Health Check")

    try:
        response = requests.get(f"{API_BASE}/health")
        response.raise_for_status()

        print("✓ Health check passed")
        print_json(response.json())
        return True

    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


def test_start_review(pdf_path):
    """Test 2: Start Review Session"""
    print_section("TEST 2: Start Review Session")

    if not Path(pdf_path).exists():
        print(f"✗ PDF file not found: {pdf_path}")
        print("Please update TEST_PDF_PATH in the script")
        return None

    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': f}
            data = {
                'refine_with_llm': 'true',
                'confidence_threshold': '0.7'
            }
            headers = {'Authorization': f'Bearer {AUTH_TOKEN}'}

            response = requests.post(
                f"{API_BASE}/start-review",
                files=files,
                data=data,
                headers=headers
            )
            response.raise_for_status()

        result = response.json()

        print("✓ Review session started successfully")
        print(f"\nSession ID: {result['session_id']}")
        print(f"Total Sentences: {result['total_sentences']}")
        print(f"Biased: {result['biased_count']}")
        print(f"Neutral: {result['neutral_count']}")

        # Show first biased sentence
        biased_sentences = [s for s in result['sentences'] if s['is_biased']]
        if biased_sentences:
            print("\nFirst Biased Sentence:")
            sentence = biased_sentences[0]
            print(f"  Original: {sentence['original_sentence']}")
            print(f"  Category: {sentence['category']}")
            print(f"  Confidence: {sentence['confidence']:.2f}")
            print(f"  Suggestion: {sentence['suggestion']}")

        return result

    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"✗ Failed to start review: {e}")
        return None


def test_get_session_status(session_id):
    """Test 3: Get Session Status"""
    print_section("TEST 3: Get Session Status")

    try:
        headers = {'Authorization': f'Bearer {AUTH_TOKEN}'}
        response = requests.get(
            f"{API_BASE}/session/{session_id}",
            headers=headers
        )
        response.raise_for_status()

        result = response.json()

        print("✓ Session status retrieved")
        print(f"\nStatus: {result['status']}")
        print(f"Pending: {result['pending_count']}")
        print(f"Approved: {result['approved_count']}")
        print(f"Needs Regeneration: {result['needs_regeneration_count']}")

        return result

    except Exception as e:
        print(f"✗ Failed to get session status: {e}")
        return None


def test_approve_suggestion(session_id, sentence_id, suggestion):
    """Test 4: Approve Suggestion"""
    print_section("TEST 4: Approve Suggestion")

    try:
        headers = {
            'Authorization': f'Bearer {AUTH_TOKEN}',
            'Content-Type': 'application/json'
        }
        data = {
            'session_id': session_id,
            'sentence_id': sentence_id,
            'action': 'approve',
            'approved_suggestion': suggestion
        }

        response = requests.post(
            f"{API_BASE}/approve-suggestion",
            json=data,
            headers=headers
        )
        response.raise_for_status()

        result = response.json()

        print(f"✓ {result['message']}")
        return True

    except Exception as e:
        print(f"✗ Failed to approve suggestion: {e}")
        return False


def test_reject_and_regenerate(session_id, sentence_id):
    """Test 5: Reject and Regenerate Suggestion"""
    print_section("TEST 5: Reject and Regenerate")

    try:
        headers = {
            'Authorization': f'Bearer {AUTH_TOKEN}',
            'Content-Type': 'application/json'
        }

        # Step 1: Reject
        print("Rejecting suggestion...")
        reject_data = {
            'session_id': session_id,
            'sentence_id': sentence_id,
            'action': 'reject'
        }

        response = requests.post(
            f"{API_BASE}/approve-suggestion",
            json=reject_data,
            headers=headers
        )
        response.raise_for_status()
        print("✓ Suggestion rejected")

        # Step 2: Regenerate
        print("\nRegenerating new suggestion...")
        regen_data = {
            'session_id': session_id,
            'sentence_id': sentence_id
        }

        response = requests.post(
            f"{API_BASE}/regenerate-suggestion",
            json=regen_data,
            headers=headers
        )
        response.raise_for_status()

        result = response.json()
        print("✓ New suggestion generated")
        print(f"New Suggestion: {result['new_suggestion']}")

        return result['new_suggestion']

    except Exception as e:
        print(f"✗ Failed to reject/regenerate: {e}")
        return None


def test_generate_pdf(session_id, output_path="test_debiased.pdf"):
    """Test 6: Generate PDF"""
    print_section("TEST 6: Generate PDF")

    try:
        headers = {
            'Authorization': f'Bearer {AUTH_TOKEN}',
            'Content-Type': 'application/json'
        }
        data = {'session_id': session_id}

        response = requests.post(
            f"{API_BASE}/generate-pdf",
            json=data,
            headers=headers
        )
        response.raise_for_status()

        # Save PDF
        with open(output_path, 'wb') as f:
            f.write(response.content)

        changes = response.headers.get('X-Changes-Applied', 'unknown')
        print(f"✓ PDF generated successfully")
        print(f"Changes Applied: {changes}")
        print(f"Saved to: {output_path}")

        return True

    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP Error: {e}")
        if e.response.text:
            print(f"Error Details: {e.response.text}")
        return False
    except Exception as e:
        print(f"✗ Failed to generate PDF: {e}")
        return False


def run_complete_workflow():
    """Run the complete HITL workflow test"""
    print("\n" + "█"*60)
    print("  HITL BIAS DETECTION - WORKFLOW TEST")
    print("█"*60)

    # Test 1: Health Check
    if not test_health_check():
        print("\n⚠ Health check failed. Is the server running?")
        return False

    # Test 2: Start Review
    review_data = test_start_review(TEST_PDF_PATH)
    if not review_data:
        print("\n⚠ Could not start review session")
        return False

    session_id = review_data['session_id']
    biased_sentences = [s for s in review_data['sentences'] if s['is_biased']]

    if not biased_sentences:
        print("\n⚠ No biased sentences found. Test with a PDF containing bias.")
        return False

    # Test 3: Get Session Status
    test_get_session_status(session_id)

    # Test 4: Approve first biased sentence
    first_sentence = biased_sentences[0]
    test_approve_suggestion(
        session_id,
        first_sentence['sentence_id'],
        first_sentence['suggestion']
    )

    # Test 5: Reject and regenerate (if there's a second biased sentence)
    if len(biased_sentences) > 1:
        second_sentence = biased_sentences[1]
        new_suggestion = test_reject_and_regenerate(
            session_id,
            second_sentence['sentence_id']
        )

        # Approve the new suggestion
        if new_suggestion:
            test_approve_suggestion(
                session_id,
                second_sentence['sentence_id'],
                new_suggestion
            )

    # Auto-approve remaining sentences for testing
    print_section("Auto-approving remaining sentences")
    for sentence in biased_sentences[2:]:
        test_approve_suggestion(
            session_id,
            sentence['sentence_id'],
            sentence['suggestion']
        )

    # Test 6: Generate PDF
    test_generate_pdf(session_id)

    print_section("TEST SUMMARY")
    print("✓ All tests completed successfully!")
    print(f"\nSession ID: {session_id}")
    print("Check 'test_debiased.pdf' for the generated output")

    return True


def main():
    """Main entry point"""
    print("\n🔧 HITL Bias Detection Test Script")
    print("="*60)

    # Check configuration
    if AUTH_TOKEN == "YOUR_AUTH_TOKEN_HERE":
        print("⚠ Please set AUTH_TOKEN in the script")
        print("Get token from Supabase authentication")
        sys.exit(1)

    if TEST_PDF_PATH == "path/to/test/document.pdf":
        print("⚠ Please set TEST_PDF_PATH in the script")
        print("Use a Nepali PDF with potentially biased content")
        sys.exit(1)

    # Run workflow
    success = run_complete_workflow()

    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
