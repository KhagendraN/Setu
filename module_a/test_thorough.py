"""
Thorough Testing Script for Module A
Runs comprehensive real-life scenarios and generates a report.
"""

import os
import logging
import json
from datetime import datetime
from dotenv import load_dotenv

# Load env vars
load_dotenv()

from module_a.rag_chain import LegalRAGChain
from module_a.config import LOG_LEVEL

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("=" * 80)
    print("Running Thorough Tests for Nepal Justice Weaver")
    print("=" * 80)
    
    # Check API key
    if not os.getenv("MISTRAL_API_KEY"):
        print("Error: MISTRAL_API_KEY not found.")
        return

    # Initialize chain
    try:
        rag = LegalRAGChain()
    except Exception as e:
        print(f"Failed to initialize RAG chain: {e}")
        return

    # Test Scenarios
    scenarios = [
        {
            "category": "Citizenship",
            "query": "I am a single mother. Can I get citizenship for my child in my name? The father is not in the picture.",
            "expected_intent": "Citizenship by descent (Article 11)"
        },
        {
            "category": "Inheritance",
            "query": "My parents want to give all property to my brother. As a daughter, do I have a claim?",
            "expected_intent": "Equal inheritance rights (Article 18, Civil Code)"
        },
        {
            "category": "Divorce",
            "query": "My husband wants a divorce but refuses to share any property. What are my rights?",
            "expected_intent": "Property partition upon divorce"
        },
        {
            "category": "Marriage",
            "query": "We want to do a court marriage. What is the process and what documents do we need?",
            "expected_intent": "Marriage registration process"
        },
        {
            "category": "Fundamental Rights",
            "query": "Can the police arrest me for posting my opinion on social media?",
            "expected_intent": "Freedom of opinion and speech (Article 17)"
        },
        {
            "category": "Cyber Law",
            "query": "Someone is harassing me online and threatening me. What can I do?",
            "expected_intent": "Cyber crime / harassment laws (might be general guidance if specific act not in DB)"
        },
        {
            "category": "Contracts",
            "query": "I lent money to a friend verbally. Is this agreement valid in court?",
            "expected_intent": "Contract validity / evidence"
        }
    ]

    results = []

    print(f"\nRunning {len(scenarios)} scenarios...\n")

    for i, scenario in enumerate(scenarios, 1):
        print(f"Scenario {i}/{len(scenarios)}: {scenario['category']}")
        print(f"Query: {scenario['query']}")
        
        try:
            # Run RAG
            response = rag.run(scenario['query'])
            
            # Store result
            result_entry = {
                "scenario": scenario,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            results.append(result_entry)
            print("✓ Success\n")
            
        except Exception as e:
            print(f"✗ Failed: {e}\n")
            results.append({
                "scenario": scenario,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    # Generate Report
    generate_report(results)
    print("=" * 80)
    print(f"Testing Complete. Report generated: module_a/test_report.md")
    print("=" * 80)

def generate_report(results):
    """Generate a Markdown report from test results"""
    
    report_path = "module_a/test_report.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Module A: Thorough Test Report\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Scenarios**: {len(results)}\n\n")
        
        f.write("## Summary of Results\n\n")
        for i, res in enumerate(results, 1):
            category = res['scenario']['category']
            status = "✅ Success" if "error" not in res else "❌ Failed"
            f.write(f"- **{i}. {category}**: {status}\n")
        
        f.write("\n---\n\n")
        
        for i, res in enumerate(results, 1):
            scenario = res['scenario']
            
            f.write(f"## Scenario {i}: {scenario['category']}\n\n")
            f.write(f"**Query**: \"{scenario['query']}\"\n\n")
            f.write(f"**Expected Intent**: {scenario['expected_intent']}\n\n")
            
            if "error" in res:
                f.write(f"> ❌ **Error**: {res['error']}\n\n")
                continue
                
            response = res['response']
            
            f.write("### Generated Response\n\n")
            f.write(f"{response['explanation']}\n\n")
            
            f.write("### Retrieved Sources\n\n")
            for source in response['sources']:
                f.write(f"- **{source['section']}** ({source['file']}) - Score: {source['relevance_score']:.4f}\n")
            
            f.write("\n---\n\n")

if __name__ == "__main__":
    main()
