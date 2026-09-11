import os
import pdfplumber
from docx import Document
from fpdf import FPDF
from dotenv import load_dotenv

load_dotenv()
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq


llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="openai/gpt-oss-120b",
    temperature=0.0
)


prompt = PromptTemplate(
    input_variables=["context", "num_questions"],
    template="""
    I am an AI assistant helping the user to generate multiple-choice questions from the text below:
    
    Text: {context}
    
    Generate {num_questions} MCQs.
    
    Requirements:
    
    1. Use the provided text as the only source of information. Do not add outside knowledge.
    2. Do not introduce facts, information, or concepts that are not mentioned in the text.
    3. Write each question directly and naturally, as it would appear in a real exam or quiz.
    4. Do NOT use phrases such as:
       - "According to the text..."
       - "According to the passage..."
       - "Based on the text..."
       - "Based on the passage..."
       - "What does the text say about..."
       - "What is mentioned in the text..."
       - "The text states..."
       - "The passage explains..."
    5. Do not mention the text, passage, document, source, or reading in the questions.
    6. Ask directly about the subject, concept, fact, process, person, event, or definition described in the text.
    7. Make the questions clear, meaningful, and suitable for an exam or quiz.
    8. Avoid vague or overly general questions.
    9. Each question must have exactly four options: A, B, C, and D.
    10. Only one option should be correct.
    11. Make the incorrect options plausible but clearly incorrect based on the provided text.
    12. Do not repeat the same question or test the same fact multiple times.
    13. Clearly indicate the correct answer.
    14. Do not provide explanations unless requested.
    15. Do not copy complete sentences from the text as questions. Convert the information into natural questions.
    16. Do not add horizontal lines, decorative separators, or extra formatting.

    
    Use this format:
    
    MCQ
    Question: [Direct and natural question]
    A) [option A]
    B) [option B]
    C) [option C]
    D) [option D]
    
    Correct Answer: [A, B, C or D]
    """
)

mcq_chain = prompt | llm

# Text Extraction from PDF, DOCX, or TXT file

def extract_text(file_path):

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == ".pdf":
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
        return text.strip()

    elif file_extension == ".docx":
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()

    elif file_extension == ".txt":
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip()

    else:
        raise ValueError(
            "Unsupported file type. Please use PDF, DOCX, or TXT."
        )



# MCQ Generation
def generate_mcqs(text,num_questions):

    if not text:
        raise ValueError("No text was provided.")

    if not num_questions or num_questions < 1:
        raise ValueError("Number of questions must be at least 1.")

    response = mcq_chain.invoke({
        "context": text,
        "num_questions": num_questions
    })

    return response.content


# Save Text File
def save_txt(mcqs, output_path):
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(mcqs)

    return output_path



# Save PDF
def save_pdf(mcqs, output_path, font_path="DejaVuSans.ttf"):
    pdf = FPDF()
    pdf.add_page()

    pdf.add_font(
        "DejaVu",
        "",
        font_path
    )

    pdf.set_font(
        "DejaVu",
        size=12
    )

    for mcq in mcqs.split("MCQ"):
        if mcq.strip():
            pdf.multi_cell(0,10, mcq.strip())
            pdf.ln(5)
    pdf.output(output_path)

    return output_path

