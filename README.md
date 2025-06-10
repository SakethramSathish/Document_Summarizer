# Document Summarizer and Q&A Assistant

A Streamlit-based application that processes various document formats (PDF, DOCX, TXT, images), extracts text, generates summaries, and provides an interactive Q&A interface using Google's Gemini AI model.

## Features

- **Multi-Format Document Support**:
  - PDF files (with OCR capability for scanned documents)
  - Word documents (.docx)
  - Text files (.txt)
  - Images (.png, .jpg, .jpeg)

- **Intelligent Processing**:
  - Automatic text extraction
  - OCR for scanned PDFs and images using Tesseract
  - Smart document summarization
  - Context-aware Q&A
  - Dynamic question suggestions

- **Interactive UI**:
  - Clean, user-friendly interface
  - Real-time chat history
  - Two-column suggested questions
  - Document summary display

## Architecture

The application follows a sequential processing flow:
1. Document Upload & Text Extraction
2. Summary Generation
3. Interactive Q&A
4. Smart Suggestions Generation

## Prerequisites

- Python 3.8+
- Tesseract OCR engine
- Google API key for Gemini AI

## Required Packages

```bash
pip install streamlit
pip install python-dotenv
pip install google-generativeai
pip install Pillow
pip install pytesseract
pip install python-docx
pip install PyMuPDF
```

## Environment Setup

1. Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

2. Install Tesseract OCR:
- Windows: Download and install from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- Update the Tesseract path in `app.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r'path_to_tesseract_executable'
```

## Usage

1. Run the application:
```bash
streamlit run app.py
```

2. Upload a document using the sidebar
3. View the generated summary
4. Ask questions or click suggested questions
5. Reset document and chat using the reset button

## Features in Detail

### Document Processing
- PDF: Extracts text directly, falls back to OCR if needed
- DOCX: Extracts text from paragraphs
- TXT: Reads with UTF-8 encoding
- Images: Performs OCR to extract text

### AI Integration
- Uses Gemini AI model for:
  - Document summarization
  - Question answering
  - Generating contextual suggestions

### Session Management
- Maintains conversation history
- Preserves document content
- Handles suggested questions state

## Project Structure

```
Document Summarization 2.0/
├── app.py              # Main application file
├── .env               # Environment variables
├── .gitignore        # Git ignore file
└── Test Documents/   # Sample documents for testing
```

## Limitations

- Large PDF files may take longer to process
- OCR accuracy depends on image quality
- API rate limits apply to AI operations

## Future Improvements

- Implement caching for better performance
- Add support for more file formats
- Enhance error handling
- Add progress indicators for long operations
- Implement parallel processing for large documents

## Contributing

Feel free to submit issues and enhancement requests.

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.