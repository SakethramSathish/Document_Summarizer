# Multi-Document Summarizer and Q&A Assistant

A professional, interactive web application for summarizing, comparing, and querying multiple documents using Google Gemini AI. Built with Streamlit, this tool supports PDFs, Word documents, text files, and images (with OCR), providing comprehensive summaries, document comparisons, and intelligent Q&A capabilities.

## Features

- **Multi-format Upload:** Supports PDF, DOCX, TXT, PNG, JPG, and JPEG files.
- **Automatic Text Extraction:** Extracts text from documents and images (using Tesseract OCR for images and scanned PDFs).
- **AI-Powered Summarization:** Generates concise, informative summaries for each uploaded document using Google Gemini.
- **Document Comparison:** Compares any two documents, highlighting similarities and differences in a structured format.
- **Smart Q&A:** Ask questions about the uploaded documents and receive context-aware answers.
- **Suggested Questions:** Recommends follow-up questions based on document content and chat history.
- **Modern UI:** Clean, dark-themed interface with intuitive controls and expandable sections.

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/SakethramSathish/Document_Summarizer
cd "Document Summarization"
```

### 2. Install Dependencies
Ensure you have Python 3.8+ installed. Then run:
```bash
pip install -r requirements.txt
```

#### Required Python Packages
- streamlit
- python-docx
- python-dotenv
- pytesseract
- Pillow
- PyMuPDF (fitz)
- google-generativeai

### 3. Install Tesseract OCR
- Download and install Tesseract OCR from [here](https://github.com/tesseract-ocr/tesseract).
- Update the `pytesseract.pytesseract.tesseract_cmd` path in `app.py` if needed.

### 4. Set Up Google Gemini API
- Create a `.env` file in the project root:
  ```env
  GOOGLE_API_KEY=your_gemini_api_key_here
  ```
- Obtain your API key from the [Google AI Studio](https://aistudio.google.com/app/apikey).

### 5. Run the Application
```bash
streamlit run app.py
```

## Usage
1. Upload one or more documents via the sidebar.
2. View AI-generated summaries and document comparisons.
3. Ask questions about the documents and explore suggested queries.
4. Reset the app anytime from the sidebar.

## Architecture
See `Architecture.png` for a high-level overview.

## License
This project is for educational and research purposes. Please check the terms of use for Google Gemini and Tesseract OCR.

---

**Developed by:** Sakethram Sathish
