import streamlit as st #To design the web app
import google.generativeai as genai #To use the Generative AI model
import fitz #To read the PDF file
import pytesseract #To extract text from images
from PIL import Image #To handle image files
import io 
import os
import docx #To read docx files
import uuid #To generate unique keys for the file uploader, just to avoid the file uploader from getting stuck during the reset process
from dotenv import load_dotenv
#Since Pytesseract cannot run on its own, we need to specify the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\z0054vmp\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

load_dotenv()

API_KEY = os.getenv('GOOGLE_API_KEY')
# Initialize the Generative AI model
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

st.set_page_config(page_title="Document Summarizer and Q&A", layout="wide")
st.title("Document Summarizer and Q&A Assistant")

#Initialize session state variables
if "document_text" not in st.session_state:
    st.session_state.document_text = "" #Stores document content
if "summary" not in st.session_state:
    st.session_state.summary = "" #Stores document summary
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [] #Stores chat history
if "suggestions" not in st.session_state:
    st.session_state.suggestions = [] #Stores smart suggestions
if "current_summary" not in st.session_state:
    st.session_state.current_summary = "" #Current Document Summary
if "question_input" not in st.session_state:
    st.session_state.question_input = "" #User's current question input
if "suggestion_clicked" not in st.session_state:
    st.session_state.suggestion_clicked = False

st.sidebar.header("Upload Document")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"], key=st.session_state.get("file_uploader_key", "file_uploader"))

def extract_text_from_pdf(file):
    doc = fitz.open(stream = file.read(), filetype="pdf")
    full_text = "" #The text extracted will append to this variable
    #Iterate through each page in the PDF document
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if not text.strip():
            pix  = page.get_pixmap(dpi=300) #The higher the DPI, the better the quality of the image and the more memory it will use
            img  = Image.open(io.BytesIO(pix.tobytes("png"))) #We convert the raw pixel representation to an image which OCR-able.
            text = pytesseract.image_to_string(img)
            #To convert pdf to image and extract text
        full_text += f"\n--- Page {page_num + 1} ---\n" + text
    return full_text

def extract_text_from_txt(file):
    return file.read().decode("utf-8")
    # This will read the text file and return its content as a string

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs]) 
    #This has access to the document's content and returns the whole text from the document

def extract_text_from_image(file):
    img = Image.open(file)
    return pytesseract.image_to_string(img) #This will OCR the image directly and return the text
    
def generate_smart_suggestions(document_text, chat_history):
    history_str = "\n".join([f"{speaker}: {message}" for speaker, message in chat_history[-6:]])

    prompt = f"""
    Given the following document content and conversation history between a user and assistant,
    generate 6 helpful, context-relevant follow-up questions the user might ask next. Where 3 should be simple and 3 should be more complex.
    But you should not say "Here are some questions you could ask" or similar phrases. You should not give the terms "question" or "questions" in the output. Just the questions only thats it.

    Document:
    \"\"\" 
    {document_text}
    \"\"\"

    Conversation so far:
    \"\"\"
    {history_str}
    \"\"\"

    List the suggested questions as bullet points only.
    """ #The \"\"\" is used to show the multiline text in the prompt (Answering Mahesh's question)
    try:
        #This is to generate the answer
        response = model.generate_content(prompt)
        raw_output = response.text.strip()
        #This is to clean the output and return a list of questions
        return [line.lstrip("-.* ").strip() for line in raw_output.split("\n") if line.strip()] #This is written because the questions given by Gemini will be in points or extraspaces. So just to clean the questions and separate them accordingly just so that the questions can be given in the suggested section.
    except Exception as e:
        
        return[]
    
if uploaded_file: #This is to check the extension of the uploaded file
    ext = uploaded_file.name.split(".")[-1].lower()
    if ext == "pdf":
        st.session_state.document_text = extract_text_from_pdf(uploaded_file)
    elif ext == "txt":
        st.session_state.document_text = extract_text_from_txt(uploaded_file)
    elif ext == "docx":
        st.session_state.document_text = extract_text_from_docx(uploaded_file)
    elif ext in ["png", "jpg", "jpeg"]:
        st.session_state.document_text = extract_text_from_image(uploaded_file)
    else:
        st.error("Unsupported file type. Please upload a PDF, DOCX, TXT, or image file.")
    
    st.success("Document uploaded and text extracted successfully!")

    with st.spinner("Generating summary..."):
        if not st.session_state.current_summary:  # Only generate if not already present, since it used to generate the summary for every question asked and it used to always generate a different summary. Hence the 'if' block.
            prompt = f"Summarize the following document and highlight key information:\n\n{st.session_state.document_text}"
            response = model.generate_content(prompt)
            st.session_state.current_summary = response.text.strip()
        st.session_state.summary = st.session_state.current_summary

    # Only generate suggestions if not clicked on a suggestion button
    if not st.session_state.suggestion_clicked and not st.session_state.suggestions:
        st.session_state.suggestions = generate_smart_suggestions(st.session_state.document_text, st.session_state.chat_history)

if st.session_state.document_text:
    st.subheader("Document Summary")
    st.markdown(st.session_state.summary)

    if st.session_state.suggestions:
        st.subheader("Suggested Questions")
        cols = st.columns(2)
        for i, question in enumerate(st.session_state.suggestions):
            if cols[i % 2].button(question, key=f"suggested_{i}"): #This is to create a unique identifier for each question and then map the button to the question.
                # Set the question input value when suggestion is clicked
                st.session_state.question_input = question
                st.session_state.suggestion_clicked = True
                st.rerun()  # Force rerun to update the input box immediately
        
st.subheader("Ask a Question")
question = st.text_input(
    "Type your question here:", 
    value=st.session_state.question_input,
    key="question_text_input"
) #This is to input the question and save it from the session state

# Update session state when user types directly
if question != st.session_state.question_input:
    st.session_state.question_input = question
    st.session_state.suggestion_clicked = False  # Reset flag when user types manually

if st.button("Submit Question") and question:
    with st.spinner("Generating answer..."):
        prompt = f"""
        Use only the following document content to answer the question.

        Document:
        \"\"\"{st.session_state.document_text}\"\"\"

        Question: {question}
        """
        response = model.generate_content(prompt)
        answer = response.text.strip() #This is done to keep the question in Gemini's format when asking a question.
        st.session_state.chat_history.append(("You", question))
        st.session_state.chat_history.append(("Gemini", answer))
        
        # Clear the question input after submitting
        st.session_state.question_input = ""
        st.session_state.suggestion_clicked = False  # Reset flag

        # Generate smart suggestions based on the updated chat history
        st.session_state.suggestions = generate_smart_suggestions(st.session_state.document_text, st.session_state.chat_history)
        
        st.rerun()  # Rerun to clear the input and show updated suggestions

# Display chat history
if st.session_state.chat_history:
    st.subheader("Chat History")
    for speaker, message in st.session_state.chat_history:
        with st.chat_message("user" if speaker == "You" else "assistant"):
            st.markdown(message)

#Reset Button
st.sidebar.markdown("---")
if st.sidebar.button("Reset Document and Chat"):
    st.session_state.document_text = ""
    st.session_state.summary = ""
    st.session_state.chat_history = []
    st.session_state.suggestions = []
    st.session_state.question_input = ""
    st.session_state.current_summary = ""
    st.session_state.suggestion_clicked = False
    st.session_state["file_uploader_key"] = str(uuid.uuid4())  # force file_uploader to reset.
    st.rerun() #To start the app fresh
    st.success("Document and chat history have been reset.")