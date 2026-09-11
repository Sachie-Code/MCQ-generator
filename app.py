import os
import tempfile
import streamlit as st
from fpdf import FPDF
from main import extract_text, generate_mcqs

st.set_page_config(
    page_title="AI MCQ Generator",
    layout="wide"
)


# Custom CSS

st.markdown(
    """
    <style>

    .main {
        background-color: #f8fafc;
    }

    .title {
        text-align: center;
        font-size: 34px;
        font-weight: bold;
        color: #1976D2;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 16px;
        color: #607d8b;
        margin-bottom: 20px;
    }

    .generated-title {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        color: white;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

bot_image = "botImage.png"

if os.path.exists(bot_image):
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.image(bot_image, width=100)


# Title
st.markdown(
    '<div class="title">AI MCQ Generator</div>',
    unsafe_allow_html=True
)
st.subheader("Upload Document to Generate MCQs")

# File Upload
uploaded_file = st.file_uploader(
    "Choose a file (PDF, DOCX, or TXT):",
    type=["pdf", "docx", "txt"]
)

# Number of Questions
MCQ_COUNT = st.number_input(
    "Number of Questions:",
    min_value=1,
    max_value=50,
    step=1,
    value=None,
    placeholder="Enter number of questions. This will generate 5 questions by default."
)

MCQ_COUNT = MCQ_COUNT if MCQ_COUNT is not None else 5

# Generate Button
generate_button = st.button(
    "Generate MCQs",
    type="primary"
)

# Generate MCQs
if generate_button:
    if uploaded_file is None:
        st.warning(
            "Please upload a PDF, DOCX, or TXT file."
        )

    else:
        with st.spinner("Generating MCQs..."):
            temp_file_path = None

            try:
                 # Get file extension
                file_extension = os.path.splitext(
                    uploaded_file.name
                )[1]

                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=file_extension
                ) as temp_file:

                    temp_file.write(
                        uploaded_file.getbuffer()
                    )

                    temp_file_path = temp_file.name

                # Extract Text
                text = extract_text(
                    temp_file_path
                )

                if not text:
                    st.error(
                        "No text found in the uploaded file."
                    )

                else:
                    # Generate MCQs
                    mcqs = generate_mcqs(
                        text=text,
                        num_questions=MCQ_COUNT
                    )

                    st.session_state["mcqs"] = mcqs

                    st.session_state["filename"] = (
                        uploaded_file.name
                    )

                    st.session_state["question_count"] = (
                        MCQ_COUNT
                    )

                    st.success(
                        "MCQs generated successfully!"
                    )


            except Exception as e:
                st.error(
                    f"Error: {e}"
                )

            finally:
                if temp_file_path and os.path.exists(
                    temp_file_path
                ):
                    os.remove(temp_file_path)



# Display Generated MCQs
if "mcqs" in st.session_state:
    mcqs = st.session_state["mcqs"]
    filename = st.session_state["filename"]
    base_name = os.path.splitext(
        filename
    )[0]

    st.markdown(
        '<div class="generated-title">Generated MCQs</div>',
        unsafe_allow_html=True
    )

    # TXT File
    txt_data = mcqs.encode("utf-8")

    # PDF File
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font(
        "DejaVu",
        "",
        "DejaVuSans.ttf"
    )
    pdf.set_font(
        "DejaVu",
        size=12
    )

    for mcq in mcqs.split("MCQ"):
        if mcq.strip():
            pdf.multi_cell(
                0,
                10,
                mcq.strip()
            )
            pdf.ln(5)

    pdf_data = bytes(
        pdf.output()
    )

    # Download Buttons
    col1, col2, col3 = st.columns(
        [1.5, 1.5, 10],
        gap="small"
    )


    with col1:
        st.download_button(
            label="Download as .txt",
            data=txt_data,
            file_name=(
                f"generated_mcqs_{base_name}.txt"
            ),
            mime="text/plain"
        )

    with col2:
        st.download_button(
            label="Download as .pdf",
            data=pdf_data,
            file_name=(
                f"generated_mcqs_{base_name}.pdf"
            ),
            mime="application/pdf"
        )

    # Display Questions
    st.text_area(
        "Generated Questions",
        value=mcqs,
        height=500,
        label_visibility="collapsed"
    )

