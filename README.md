# PDF Data Extraction with Ollama and LangChain

This project demonstrates a Proof of Concept (PoC) for intelligent PDF data extraction using a combination of PDF Plumber, LangChain, and Ollama. The system provides a user-friendly web interface built with Streamlit for uploading PDFs and extracting specific information based on user-defined criteria.

## 🚀 Features

- PDF text extraction using PDF Plumber
- Intelligent data extraction using Ollama's Gemma model
- Web interface built with Streamlit
- Docker-based Ollama server setup
- Chunk-based processing for handling large documents
- Customizable extraction criteria

## 🛠️ Technology Stack

### Core Components

1. **PDF Plumber**
   - Used for robust PDF text extraction
   - Maintains text formatting and structure
   - Handles complex PDF layouts effectively

2. **LangChain**
   - Provides the framework for building LLM applications
   - Implements text chunking for processing large documents
   - Manages prompt templates and LLM chains
   - Enables structured data extraction

3. **Ollama**
   - Runs the Gemma model locally in a Docker container
   - Provides efficient inference capabilities
   - Ensures data privacy by keeping processing local
   - Docker setup simulates RHEL 9 environment

4. **Streamlit**
   - Creates an intuitive web interface
   - Handles file uploads and user input
   - Displays extraction results in a clean format

## 📋 Prerequisites

- Windows 10/11
- Docker Desktop
- Python 3.7+
- 4GB+ RAM
- 20GB+ free disk space

## 🚀 Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd ollama_poc
   ```

2. **Set Up Python Environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Start Ollama Container**
   ```bash
   docker-compose up -d
   ```

4. **Pull Required Model**
   ```bash
   docker exec -it ollama ollama pull gemma3:4b
   ```

5. **Run the Application**
   ```bash
   streamlit run app.py
   ```

## 💻 Usage

1. Access the web interface at `http://localhost:8501`
2. Upload a PDF file using the file uploader
3. Enter your extraction criteria in the text area
4. View the extracted information displayed below

### Example Criteria
```
Extract all dates in MM/DD/YYYY format, company names, and monetary values
```

## 🔧 Project Structure

- `app.py` - Streamlit web application
- `pdf_processor.py` - Core PDF processing and extraction logic
- `ollama_client.py` - Ollama API client implementation
- `docker-compose.yml` - Docker configuration for Ollama
- `requirements.txt` - Python dependencies
- `monitor_resources.py` - Resource monitoring utility

## 🔍 How It Works

1. **PDF Processing**
   - PDF is uploaded through the Streamlit interface
   - PDF Plumber extracts text while preserving structure
   - Text is split into manageable chunks

2. **Data Extraction**
   - LangChain manages the extraction process
   - Custom prompts guide the Gemma model
   - Results are aggregated and structured

3. **Ollama Integration**
   - Runs in a Docker container for isolation
   - Provides local inference capabilities
   - Ensures data privacy and security

## 🛠️ Development

### Running Tests
```bash
python test_prompt.py
python test_memory.py
```

### Monitoring Resources
```bash
python monitor_resources.py
```

## 🔒 Security Considerations

- All processing is done locally
- No data is sent to external services
- Docker container provides isolation
- Temporary files are properly cleaned up

## 📝 License

[Your License Here]

## 🤝 Contributing

[Your Contribution Guidelines Here] 