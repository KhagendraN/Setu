import fitz  # pymupdf
import re
from typing import List
from transformers import pipeline
import torch

PDF_FILE_PATH = "module_b/file_2.pdf"  


def extract_nepali_sentences_from_pdf(pdf_path: str) -> List[str]:
    """
    Extracts clean Nepali sentences from a searchable PDF using PyMuPDF.
    """
    print(f"Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    
    full_text = ""
    for page in doc:
        text = page.get_text("text")
        full_text += text + "\n"
    
    doc.close()
    
    if not full_text.strip():
        print("Warning: No text found. PDF might be scanned (image-based). Use OCR version instead.")
        return []
    
    # Clean whitespace
    text = full_text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Split sentences intelligently
    sentences = re.split(r'(?<=[।.!?])\s+(?=[अ-हँ-ॿअ-ह])|(?<=[।.!?])(?=$)', text)
    if len(sentences) <= 1:  # fallback
        sentences = re.split(r'(?<=[।.!?])\s+', text)
    
    # Final cleaning
    cleaned = [s.strip(' ।.!?').strip() for s in sentences if len(s.strip()) > 5]
    
    print(f"Successfully extracted {len(cleaned)} clean sentences.\n")
    return cleaned


print("Loading your model from Hugging Face...")
model_name = "sangy1212/distilbert-base-nepali-fine-tuned"

classifier = pipeline(
    "text-classification",
    model=model_name,
    tokenizer=model_name,
    device=0 if torch.cuda.is_available() else -1,  
    batch_size=16  
)

print("Model loaded and ready!\n")

id_to_label = {
    "LABEL_0":  "neutral",
    "LABEL_1":  "gender",
    "LABEL_2":  "religional",
    "LABEL_3":  "caste",
    "LABEL_4":  "religion",
    "LABEL_5":  "appearence",
    "LABEL_6":  "socialstatus",
    "LABEL_7":  "amiguity",
    "LABEL_8":  "political",
    "LABEL_9":  "Age",
    "LABEL_10": "Disablity"
}

def predict_bias_on_sentences(sentences: List[str], confidence_threshold: float = 0.7):
    """
    Runs batch prediction and prints results with nice formatting.
    """
    if not sentences:
        print("No sentences to analyze.")
        return
    
    print(f"Running bias detection on {len(sentences)} sentences...\n")
    
    # Batch inference
    results = classifier(sentences)
    
    print("="*100)
    print("BIAS DETECTION RESULTS")
    print("="*100)
    
    biased_count = 0
    for sent, res in zip(sentences, results):
        label_id = res['label']
        category = id_to_label.get(label_id, "unknown")
        confidence = res['score']
        
        if category != "neutral" and confidence >= confidence_threshold:
            mark = " BIAS DETECTED"
            biased_count += 1
        else:
            mark = "✓ neutral / low confidence"
        
        print(f"{mark}")
        print(f"   Category   : {category.upper()}")
        print(f"   Confidence : {confidence:.3f}")
        print(f"   Sentence   : {sent}")
        print("-" * 80)
    
    print(f"\nSummary: {biased_count}/{len(sentences)} sentences contain detectable bias (confidence ≥ {confidence_threshold})")


if __name__ == "__main__":
    pdf_file_path = PDF_FILE_PATH 
    import os

    if os.path.exists(pdf_file_path):
        print(f"Using PDF file at: {pdf_file_path}\n")
    else:
        print(f"PDF file not found at: {pdf_file_path}. Please check the path.")
        exit(1)
    
    # Step 1: Extract sentences
    sentences = extract_nepali_sentences_from_pdf(pdf_file_path)
    
    # Step 2: Run batch prediction
    if sentences:
        predict_bias_on_sentences(sentences, confidence_threshold=0.7)
    
    print("\nDone! Your bias detection is complete.")