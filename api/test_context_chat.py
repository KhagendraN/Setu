"""
Test script for context-aware chat functionality
This demonstrates the new chat endpoint with conversation context
"""

import requests
import json
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust to your API URL
API_TOKEN = None  # Will be set after login


def login(email: str, password: str) -> Optional[str]:
    """Login and get access token"""
    url = f"{BASE_URL}/auth/login"
    payload = {"email": email, "password": password}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        token = data.get("session", {}).get("access_token")
        print(f"✓ Login successful")
        return token
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return None


def create_conversation(token: str, title: str = "Test Conversation") -> Optional[str]:
    """Create a new conversation"""
    url = f"{BASE_URL}/chat-history/conversations"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"title": title}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        conv_id = data.get("id")
        print(f"✓ Conversation created: {conv_id}")
        return conv_id
    except Exception as e:
        print(f"✗ Failed to create conversation: {e}")
        return None


def send_chat_message(
    token: str,
    query: str,
    conversation_id: Optional[str] = None
) -> dict:
    """Send a chat message with context awareness"""
    url = f"{BASE_URL}/law-explanation/chat"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "query": query,
        "conversation_id": conversation_id
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f"✗ Chat request failed: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return {}


def get_conversation_history(token: str, conversation_id: str) -> list:
    """Get conversation messages"""
    url = f"{BASE_URL}/chat-history/conversations/{conversation_id}/messages"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"✗ Failed to get messages: {e}")
        return []


def print_response(response: dict, test_name: str):
    """Pretty print the response"""
    print(f"\n{'='*60}")
    print(f"Test: {test_name}")
    print(f"{'='*60}")

    if not response:
        print("No response received")
        return

    print(f"Query: {response.get('query', 'N/A')}")
    print(f"Context Used: {response.get('context_used', False)}")
    print(f"Is Non-Legal: {response.get('is_non_legal', False)}")

    if response.get('original_query'):
        print(f"Original Query: {response['original_query']}")
    if response.get('summarized_query'):
        print(f"Summarized Query: {response['summarized_query']}")

    print(f"\nSummary: {response.get('summary', 'N/A')}")
    print(f"\nExplanation: {response.get('explanation', 'N/A')[:200]}...")
    print(f"\nSources: {len(response.get('sources', []))} documents")
    print(f"{'='*60}\n")


def run_test_scenario(token: str):
    """Run comprehensive test scenarios"""
    print("\n" + "="*60)
    print("CONTEXT-AWARE CHAT TEST SCENARIOS")
    print("="*60 + "\n")

    # Create a new conversation for testing
    conv_id = create_conversation(token, "Context Awareness Test")
    if not conv_id:
        print("Cannot proceed without conversation ID")
        return

    # Test 1: Initial legal query
    print("\n--- Test 1: Initial Legal Query (No Context) ---")
    response1 = send_chat_message(
        token,
        "I had a fight with my brother over property",
        conv_id
    )
    print_response(response1, "Initial Property Dispute Query")

    # Test 2: Dependent follow-up query
    print("\n--- Test 2: Dependent Follow-up Query (With Context) ---")
    response2 = send_chat_message(
        token,
        "He is making fake allegations",
        conv_id
    )
    print_response(response2, "Follow-up About Brother's Allegations")

    # Test 3: Another dependent query
    print("\n--- Test 3: Another Dependent Query ---")
    response3 = send_chat_message(
        token,
        "What evidence do I need to counter this?",
        conv_id
    )
    print_response(response3, "Evidence Question (Continuation)")

    # Test 4: Independent new topic
    print("\n--- Test 4: Independent New Topic ---")
    response4 = send_chat_message(
        token,
        "How do I apply for citizenship in Nepal?",
        conv_id
    )
    print_response(response4, "New Independent Query - Citizenship")

    # Test 5: Non-legal query (greeting)
    print("\n--- Test 5: Non-Legal Query (Greeting) ---")
    response5 = send_chat_message(
        token,
        "Thank you so much for your help!",
        conv_id
    )
    print_response(response5, "Gratitude Message")

    # Test 6: Non-legal query (small talk)
    print("\n--- Test 6: Non-Legal Query (Greeting) ---")
    response6 = send_chat_message(
        token,
        "Hi, how are you?",
        conv_id
    )
    print_response(response6, "Casual Greeting")

    # Test 7: Back to legal query
    print("\n--- Test 7: Back to Legal Topic ---")
    response7 = send_chat_message(
        token,
        "What are the divorce laws in Nepal?",
        conv_id
    )
    print_response(response7, "New Legal Topic - Divorce")

    # Show conversation history summary
    print("\n" + "="*60)
    print("CONVERSATION HISTORY SUMMARY")
    print("="*60)
    messages = get_conversation_history(token, conv_id)
    print(f"Total messages in conversation: {len(messages)}")

    for i, msg in enumerate(messages, 1):
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        print(f"\n{i}. [{role.upper()}]: {content[:100]}...")


def run_edge_case_tests(token: str):
    """Test edge cases"""
    print("\n" + "="*60)
    print("EDGE CASE TESTS")
    print("="*60 + "\n")

    # Test without conversation_id
    print("\n--- Test: No Conversation ID (Standalone Query) ---")
    response = send_chat_message(
        token,
        "What are tenant rights in Nepal?",
        conversation_id=None
    )
    print_response(response, "Standalone Query Without Conversation")

    # Test with empty conversation
    conv_id = create_conversation(token, "Empty Conversation Test")
    print("\n--- Test: First Message in New Conversation ---")
    response = send_chat_message(
        token,
        "Tell me about labor laws",
        conversation_id=conv_id
    )
    print_response(response, "First Message in Fresh Conversation")


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║   Context-Aware Chat Testing Suite                         ║
║   Tests conversation context awareness, independence       ║
║   detection, and non-legal query filtering                 ║
╚════════════════════════════════════════════════════════════╝
    """)

    # Get credentials
    print("Please provide your test credentials:")
    email = input("Email: ").strip()
    password = input("Password: ").strip()

    # Login
    token = login(email, password)
    if not token:
        print("\nCannot proceed without authentication token")
        exit(1)

    # Run tests
    try:
        run_test_scenario(token)
        print("\n" + "="*60)
        run_edge_case_tests(token)

        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60 + "\n")

    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\nTest suite failed: {e}")
        import traceback
        traceback.print_exc()
