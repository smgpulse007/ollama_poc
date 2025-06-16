import streamlit as st
import tempfile
import os
from pdf_processor import PDFProcessor

st.set_page_config(
    page_title="PDF Data Extractor",
    page_icon="📄",
    layout="wide"
)

st.title("📄 PDF Data Extractor")
st.write("Upload a PDF and specify criteria to extract information using AI.")

# Initialize PDF processor
@st.cache_resource
def get_processor():
    return PDFProcessor()

processor = get_processor()

# File upload
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# Criteria input
criteria = st.text_area(
    "Enter extraction criteria",
    placeholder="Example: Extract all dates, names, and monetary values from the document.",
    height=100
)

if uploaded_file and criteria:
    # Create a temporary file to store the uploaded PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        with st.spinner("Processing PDF..."):
            # Extract text from PDF
            text = processor.extract_text_from_pdf(tmp_file_path)
            
            # Extract data based on criteria
            results = processor.extract_data(text, criteria)
            
            # Display results
            st.subheader("Extracted Information")
            for i, result in enumerate(results["extracted_data"], 1):
                st.markdown(f"**Chunk {i}:**")
                st.write(result)
                st.markdown("---")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    
    finally:
        # Clean up temporary file
        os.unlink(tmp_file_path)

# Add some helpful information
with st.expander("How to use this app"):
    st.markdown("""
    1. Upload a PDF file using the file uploader above
    2. Enter your extraction criteria in the text area
    3. The app will process the PDF and extract information based on your criteria
    4. Results will be displayed below
    
    **Tips for better results:**
    - Be specific in your criteria
    - For multiple types of information, list them clearly
    - Example criteria: "Extract all dates in MM/DD/YYYY format, company names, and monetary values"
    """) 