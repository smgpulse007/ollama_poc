import pdfplumber
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class PDFProcessor:
    def __init__(self, model_name: str = "gemma3:27b"):
        self.llm = Ollama(model=model_name)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using pdfplumber."""
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
                print(text)
        return text
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks for processing."""
        return self.text_splitter.split_text(text)
    
    def create_extraction_prompt(self, criteria: str) -> PromptTemplate:
        """Create a prompt template for data extraction."""
        template = """
        You are a data extraction expert. Given the following text from a PDF document, 
        extract information based on these criteria: {criteria}
        
        Text: {text}
        
        Please provide the extracted information in a structured format.
        """
        return PromptTemplate(
            input_variables=["text", "criteria"],
            template=template
        )
    
    def extract_data(self, text: str, criteria: str) -> Dict[str, Any]:
        """Extract data from text based on given criteria."""
        prompt = self.create_extraction_prompt(criteria)
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        # Process text in chunks if it's too long
        chunks = self.split_text(text)
        results = []
        
        for chunk in chunks:
            result = chain.run(text=chunk, criteria=criteria)
            results.append(result)
        
        return {
            "extracted_data": results,
            "criteria": criteria
        } 