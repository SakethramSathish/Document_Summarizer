import streamlit as st
import fitz
import pytesseract
from PIL import Image
import io
import os
import docx
import uuid
from dotenv import load_dotenv
from itertools import combinations
import google.generativeai as genai

# Set the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\z0054vmp\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Load .env credentials
load_dotenv()

# --- Gemini API Integration Helper ---
def initialize_gemini():
    """
    Initialize the Gemini API with your API key
    """
    api_key = os.getenv('GOOGLE_API_KEY')  # Store your Gemini API key in .env file
    if not api_key:
        raise ValueError("No API key found")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash')

# Initialize Gemini model
try:
    model = initialize_gemini()
except Exception as e:
    st.error(f"Failed to initialize Gemini API: {str(e)}")
    model = None

def gemini_generate_content(prompt):
    """
    Calls the Gemini API endpoint with the prompt.
    Returns the generated content.
    """
    try:
        if not model:
            return type("Response", (), {"text": "Gemini API not initialized."})
        
        response = model.generate_content(prompt)
        return type("Response", (), {"text": response.text})
    except Exception as e:
        return type("Response", (), {"text": f"Error: {str(e)}"})

# --- Streamlit App Setup ---
st.set_page_config(
    page_title="Multi-Document Summarizer and Comparator",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* ----------- current colours stay the same ----------- */
.stApp                    {background-color:#0A0A2E; color:white;}
[data-testid="stSidebar"] {background-color:#0A0A2E !important;}
h1,h2,h3                 {color:white !important;}
hr                       {border-color:#00FFE7;}

/* ----------- file-uploader (unchanged) ----------- */
[data-testid="stFileUploader"]{padding:1rem;}
[data-testid="stFileUploaderDropZone"],
[data-testid="stFileUploader"]>div>div{
    background-color:#1E1E4E !important; color:white !important; border-radius:6px;
}
[data-testid="stFileUploader"] button{
    background-color:#00FFE7 !important; color:#0A0A2E !important; border:none !important;
}

/* ----------- buttons & inputs (unchanged) ----------- */
.stButton>button          {background-color:#00FFE7 !important; color:#0A0A2E !important; border:none !important;}
.stTextInput>div>div>input{background-color:#1E1E4E; color:white; border-color:#00FFE7;}

/* ----------- header bar (unchanged) ----------- */
header[data-testid="stHeader"]      {background-color:#0A0A2E !important; box-shadow:none;}
header[data-testid="stHeader"] *    {color:white !important;}

/* ===================================================== */
/*                 EXPANDER (dropdown)                   */
/* ===================================================== */

/* default header colour (collapsed & expanded) */
div[data-testid="stExpander"] > div:first-child{
    background-color:#1E1E4E !important;   /* dark blue */
    color:white !important;
    border-radius:4px;
}

/* hover state: make cyan */
div[data-testid="stExpander"] > div:first-child:hover{
    background-color:#00FFE7 !important;   /* cyan */
    color:#0A0A2E !important;
}

/* change arrow / caret colour on hover */
div[data-testid="stExpander"] > div:first-child:hover svg{
    fill:#0A0A2E !important;
    stroke:#0A0A2E !important;
}
            
div[data-testid="stExpander"] > div:first-child:hover{
    background-color:#00FFE7 !important;  /* cyan on hover */
}
</style>
""", unsafe_allow_html=True)

st.title("Multi-Document Summarizer and Q&A Assistant")

# --- Session State Initialization ---
if "docs_text" not in st.session_state:
    st.session_state.docs_text = {}  # {filename: content}
if "summaries" not in st.session_state:
    st.session_state.summaries = {}
if "comparisons" not in st.session_state:
    st.session_state.comparisons = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "question_input" not in st.session_state:
    st.session_state.question_input = ""
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []
if "suggestion_clicked" not in st.session_state:
    st.session_state.suggestion_clicked = False
if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = str(uuid.uuid4())

st.sidebar.header("Upload Files")
uploaded_files = st.sidebar.file_uploader(
    "Choose multiple documents", 
    type=["pdf", "docx", "txt", "png", "jpg", "jpeg"], 
    accept_multiple_files=True, 
    key=st.session_state.file_uploader_key
)

# --- Extraction Functions ---
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(doc)):
        page = doc[page_num]
        content = page.get_text()
        if not content.strip():
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            content = pytesseract.image_to_string(img)
        text += f"\n--- Page {page_num + 1} ---\n{content}"
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_txt(file):
    return file.read().decode("utf-8")

def extract_text_from_image(file):
    img = Image.open(file)
    return pytesseract.image_to_string(img)

# --- LLM Functions using Gemini API ---
def summarize_text(text):
    prompt = f"You are a professional summarizer. Read the entire document carefully and generate a comprehensive summary that clearly explains the main ideas and structure without omitting any important points. Highlight the key takeaways, central arguments, and any critical insights. The summary should be concise, objective, and easy to understand, yet rich enough to fully grasp the essence of the document. Do not include unnecessary details or examples. Avoid all emojis and ensure the tone remains formal and informative. Also you should give the key takeaways in bullet points after the summary.\n\n{text}"
    try:
        response = gemini_generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return "Summary generation failed."

def compare_docs(name1, text1, name2, text2):
    prompt = f"""
    Compare the following two documents and highlight similarities and differences.

    Document A – {name1}:
    \"\"\"{text1}\"\"\"

    Document B – {name2}:
    \"\"\"{text2}\"\"\"

    Output a comparative analysis with the following structure:

    Clearly mention which document is Document A and which is Document B, including their full names or titles.

    Add a heading: Similarities

    List the shared themes, concepts, goals, or structure between the two documents in a clear and concise manner.

    Add a heading: Differences

    Present the differences in a tabular format with the following structure:

    Column 1: Aspect/Category
    Column 2: Document A - (Short Name 1)
    Column 3: Document B - (Short Name 2)

    The (Short Name ) and (Short Name 2) should be brief, descriptive titles (3-5 words) that represent each document's core topic.

    The tone should be formal, informative, and free of emojis.
    """
    try:
        response = gemini_generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return "Comparison failed."

def generate_smart_suggestions(all_text, chat_history):
    history_str = "\n".join([f"{s}: {m}" for s, m in chat_history[-6:] if isinstance((s, m), tuple)])
    prompt = f"""
    Given the document content and the chat history, generate a total of 6 thoughtful follow-up questions:

    3 should be simple (fact-based or clarifying),
    3 should be complex (analytical, inferential, or open-ended).

    Do not include any introductory or concluding text. Output only the questions as bullet points.
    Also don't give (Simple) or (Complex) at the end. It should be the question only and nothing else.

    Document:
    \"\"\"{all_text}\"\"\"

    Chat history:
    \"\"\"{history_str}\"\"\"
    """
    try:
        response = gemini_generate_content(prompt)
        raw = response.text.strip()
        return [line.lstrip("-.* ").strip() for line in raw.split("\n") if line.strip()]
    except Exception as e:
        return []

# --- Document Handling ---
if uploaded_files:
    for file in uploaded_files:
        name = file.name
        ext = name.split(".")[-1].lower()
        if name in st.session_state.docs_text:
            continue

        if ext == "pdf":
            text = extract_text_from_pdf(file)
        elif ext == "docx":
            text = extract_text_from_docx(file)
        elif ext == "txt":
            text = extract_text_from_txt(file)
        elif ext in ["png", "jpg", "jpeg"]:
            text = extract_text_from_image(file)
        else:
            text = ""

        if text:
            st.session_state.docs_text[name] = text
            st.session_state.summaries[name] = summarize_text(text)

    # Generate comparisons
    doc_names = list(st.session_state.docs_text.keys())
    for (a, b) in combinations(doc_names, 2):
        key = f"{a} vs {b}"
        if key not in st.session_state.comparisons:
            text1 = st.session_state.docs_text[a]
            text2 = st.session_state.docs_text[b]
            st.session_state.comparisons[key] = compare_docs(a, text1, b, text2)

    # Generate smart suggestions
    if not st.session_state.suggestion_clicked and not st.session_state.suggestions:
        combined_text = "\n\n".join(st.session_state.docs_text.values())
        st.session_state.suggestions = generate_smart_suggestions(combined_text, st.session_state.chat_history)

# --- Display Summaries and Document Comparisons ---
if st.session_state.docs_text:
    st.subheader("Summaries of Uploaded Documents")
    for name, summary in st.session_state.summaries.items():
        with st.expander(f"Summary: {name}"):
            st.markdown(summary)

    st.subheader("Document Comparisons")
    if len(st.session_state.docs_text) < 2:
        st.markdown(
            """
            <div style="background-color: #00FFE7; color: #0A0A2E; padding: 10px; border-radius: 5px;">
                More than one document is required to perform document comparison.
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        for key, cmp_text in st.session_state.comparisons.items():
            with st.expander(f"Comparison: {key}"):
                st.markdown(cmp_text)

    if st.session_state.suggestions:
        st.subheader("Suggested Questions")
        cols = st.columns(2)
        for i, sug in enumerate(st.session_state.suggestions):
            if cols[i % 2].button(sug, key=f"suggested_{i}"):
                st.session_state["suggestion_clicked"] = True
                st.session_state["question_input"] = sug
                st.rerun()

# --- Q&A Section ---
st.subheader("Ask a Question")
question = st.text_input("Type your question here:", key="question_text_input", value=st.session_state.question_input)

# Detect user typing
if question != st.session_state.question_input:
    st.session_state.question_input = question
    st.session_state.suggestion_clicked = False

if st.button("Submit Question") and question:
    all_docs = "\n\n".join(st.session_state.docs_text.values())
    prompt = f"""
    Use only the content from the following documents to answer the question.

    Documents:
    \"\"\"{all_docs}\"\"\"

    Question: {question}
    """
    response = gemini_generate_content(prompt)
    answer = response.text.strip()
    st.session_state.chat_history.append(("You", question))
    st.session_state.chat_history.append(("Gemini", answer))
    st.session_state.question_input = ""
    st.session_state.suggestion_clicked = False
    st.session_state.suggestions = generate_smart_suggestions(all_docs, st.session_state.chat_history)
    st.rerun()

# --- Display Chat ---
if st.session_state.chat_history:
    st.subheader("Chat History")
    for entry in st.session_state.chat_history:
        if isinstance(entry, tuple) and len(entry) == 2:
            speaker, msg = entry
            with st.chat_message("user" if speaker == "You" else "assistant"):
                st.markdown(msg)
        else:
            st.warning(f"Invalid chat entry: {entry}")

# --- Reset ---
st.sidebar.markdown("---")
if st.sidebar.button("Reset App"):
    st.session_state.clear()
    st.session_state["file_uploader_key"] = str(uuid.uuid4())
    st.rerun()