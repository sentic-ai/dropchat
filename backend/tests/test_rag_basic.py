#!/usr/bin/env python3
"""
Basic test for RAG components without OpenAI API calls.
This tests PDF parsing and text chunking functionality.
"""

import os
import sys
sys.path.append('.')
from test_rag import SimpleRAG

def test_pdf_parsing():
    """Test PDF parsing functionality."""
    print("Testing PDF parsing...")

    try:
        rag = SimpleRAG("dummy-key")
    except:
        class TestRAG:
            def extract_text_from_pdf(self, pdf_path):
                return SimpleRAG.extract_text_from_pdf(self, pdf_path)

            def chunk_text(self, text, chunk_size=1000, overlap=200):
                return SimpleRAG.chunk_text(self, text, chunk_size, overlap)

        rag = TestRAG()

    documents_dir = "documents"
    pdf_files = [f for f in os.listdir(documents_dir) if f.endswith('.pdf')]

    if not pdf_files:
        print("No PDF files found in documents directory")
        return False

    pdf_path = os.path.join(documents_dir, pdf_files[0])
    print(f"Testing with: {pdf_files[0]}")

    try:
        text = rag.extract_text_from_pdf(pdf_path)
        print(f"✓ Extracted {len(text)} characters from PDF")

        chunks = rag.chunk_text(text, chunk_size=500, overlap=100)
        print(f"✓ Created {len(chunks)} text chunks")

        if chunks:
            print(f"✓ Sample chunk (first 200 chars): {chunks[0][:200]}...")

        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def main():
    print("=== Basic RAG Component Test ===")
    print("This test verifies PDF parsing and text chunking without API calls.\n")

    if test_pdf_parsing():
        print("\n✓ Basic components working correctly!")
        print("\nTo test the full RAG pipeline:")
        print("1. Set your OpenAI API key: export OPENAI_API_KEY='your-key'")
        print("2. Run: python test_rag.py")
    else:
        print("\n✗ Component tests failed")

if __name__ == "__main__":
    main()