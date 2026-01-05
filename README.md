# Setu 🇳🇵

**An AI-powered platform for legal assistance in Nepal** - making legal documents accessible, generating official letters, and detecting bias in legal text.

## 🎯 Project Overview

Setu is a comprehensive legal assistance platform that leverages AI/ML to help Nepali citizens interact with legal documents and government processes. The system consists of three main modules integrated with a modern web interface.

## 🎥 Demo Video

Watch the platform in action: [View Demo Video](https://drive.google.com/file/d/12j2J-_g7SHdcQTwU3hQU_uiWldB2RFUz/view?usp=drive_link)

## 🚀 Features

### Module A: Law Explanation (RAG-Based Chatbot)
- **Intelligent Q&A**: Ask questions about Nepali laws in natural language (English/Nepali)
- **Retrieval-Augmented Generation**: Retrieves relevant legal text and generates accurate explanations
- **Source References**: Provides exact article/section references
- **Vector Database**: ChromaDB with semantic search capabilities

### Module B: Multi-Category Bias Detection
- **10+ Bias Categories**: Detects gender, caste, religion, age, disability, appearance, social status, political, and ambiguity biases
- **Fine-tuned DistilBERT**: Custom model trained on Nepali legal texts
- **Sentence Analysis**: Analyzes individual sentences or batch processing
- **Debiasing Suggestions**: Provides bias-free alternatives for detected biases
- **Confidence Scoring**: Returns confidence scores for each detection

### Module C: Letter Generation
- **Template-Based Generation**: RAG-based intelligent template selection
- **Natural Language Input**: Describe your need, get the right letter
- **Smart Field Extraction**: Automatically extracts name, date, district, etc.
- **Official Formats**: Generates proper Nepali government letter formats

### Utility: PDF Processing
- **Text Extraction**: Extract text from legal PDFs (English & Nepali)
- **Multi-method Support**: PyMuPDF, pdfplumber with intelligent fallback
- **OCR Ready**: Handles scanned documents
- **Integrated Pipeline**: Direct integration with bias detection

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python) - RESTful API
- ChromaDB - Vector database for embeddings
- Mistral AI - LLM for generation
- Sentence Transformers - Embeddings
- PyMuPDF, PDFPlumber - PDF processing

**Frontend:**
- Next.js 16 - React framework
- TypeScript - Type safety
- Tailwind CSS - Styling
- Radix UI - Component library
- shadcn/ui - UI components

**ML/AI:**
- Hugging Face Transformers
- Sentence Transformers
- Custom fine-tuned models (Module B)

## 📋 Prerequisites

- **Python**: 3.9+ (recommended: 3.13)
- **Node.js**: 18+ with pnpm
- **API Keys**: Mistral AI API key
- **System**: Linux/macOS/Windows

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/KhagendraN/Setu.git
cd Setu
```

### 2. Backend Setup

Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Create `.env` file in the project root:
```bash
MISTRAL_API_KEY=your_mistral_api_key_here
```

### 3. Build Vector Databases

**Module A (Law Explanation):**
```bash
# Place your legal PDFs in data/module-A/law/
python -m module_a.process_documents
python -m module_a.build_vector_db
```

**Module C (Letter Generation):**
```bash
# Templates are already in data/module-C/
python -m module_c.indexer
```

### 4. Frontend Setup
```bash
cd Frontend
pnpm install
cd ..
```

## 🚀 Running the Application

You need **TWO terminals** to run the full application:

### Terminal 1: Backend API
```bash
# Activate virtual environment
source venv/bin/activate

# Start the API server
uvicorn api.main:app --reload --port 8000
```

Backend will run at: `http://localhost:8000`
API docs available at: `http://localhost:8000/docs`

### Terminal 2: Frontend
```bash
cd Frontend
pnpm dev
```

Frontend will run at: `http://localhost:3000`

## 🐳 Docker Usage (Recommended)

The easiest way to run the entire platform is using Docker Compose.

### 1. Prerequisites
- Docker and Docker Compose installed
- `.env` file with `MISTRAL_API_KEY` in the root directory

### 2. Run with Docker Compose
```bash
docker-compose up --build
```

This will:
- Build and start the Backend API (port 8000)
- Build and start the Frontend (port 3000)
- Automatically run the vector database build scripts

The application will be available at `http://localhost:3000`.

## 📁 Project Structure

```
Setu/
├── api/                          # Main API endpoints
│   ├── main.py                   # FastAPI application
│   ├── routes/
│   │   ├── law_explanation.py    # Module A endpoints
│   │   ├── letter_generation.py  # Module C endpoints
│   │   ├── bias_detection.py     # Module B endpoints
│   │   └── pdf_processing.py     # PDF utility endpoints
│   └── schemas.py                # Pydantic models
│
├── module_a/                     # Law Explanation (RAG)
│   ├── rag_chain.py             # RAG pipeline
│   ├── vector_db.py             # ChromaDB interface
│   ├── process_documents.py     # Document processing
│   └── README.md
│
├── module_b/                     # Bias Detection
│   ├── inference.py             # Model inference
│   ├── fine_tuning/             # Training scripts
│   └── dataset/                 # Training data
│
├── module_c/                     # Letter Generation
│   ├── interface.py             # Main API
│   ├── retriever.py             # Template retrieval
│   ├── generator.py             # Letter generation
│   ├── indexer.py               # Vector DB indexing
│   └── README.md
│
├── utility/                      # PDF Processing
│   ├── pdf_processor.py         # PDF extraction
│   └── README.md
│
├── Frontend/                     # Next.js application
│   ├── app/
│   │   ├── chatbot/             # Module A UI
│   │   ├── letter-generator/    # Module C UI
│   │   ├── bias-checker/        # Module B UI
│   │   ├── dashboard/           # Main dashboard
│   │   └── login/               # Authentication pages
│   └── components/              # Reusable components
│
└── data/                        # Data storage
    ├── module-A/                # Law documents & vector DB
    ├── module-C/                # Letter templates & vector DB
    └── module-B/                # Bias detection datasets
```

## 🔌 API Endpoints

### Law Explanation (Module A)
- `POST /api/v1/explain` - Ask legal questions

### Letter Generation (Module C)
- `POST /api/v1/search-template` - Search for templates
- `POST /api/v1/get-template-details` - Get template requirements
- `POST /api/v1/fill-template` - Fill template with data
- `POST /api/v1/generate-letter` - Generate complete letter
- `POST /api/v1/analyze-requirements` - Analyze missing fields

### Bias Detection (Module B)
- `POST /api/v1/detect-bias` - Detect bias in text
- `POST /api/v1/detect-bias/batch` - Batch bias detection
- `POST /api/v1/debias-sentence` - Get debiased alternatives
- `POST /api/v1/debias-sentence/batch` - Batch debiasing
- `GET /api/v1/health` - Health check

### PDF Processing (Utility)
- `POST /api/v1/process-pdf` - Extract text from PDF
- `POST /api/v1/process-pdf-to-bias` - Extract PDF and detect bias
- `GET /api/v1/pdf-health` - Health check

Full API documentation: `http://localhost:8000/docs` (when server is running)

## 🎨 Frontend Features

- **Dashboard**: Overview of all modules
- **Chatbot**: Interactive law explanation interface
- **Letter Generator**: Step-by-step letter creation wizard
- **Bias Checker**: Upload documents or paste text for analysis
- **User Profile**: User account management
- **Responsive Design**: Works on desktop and mobile

## 🧪 Testing

### Test Module A (Law Explanation)
```bash
python -m module_a.test_rag
```

### Test Module C (Letter Generation)
```bash
python -m module_c.test_generation
python -m module_c.test_interactive
```

### Test PDF Processing
```bash
python -m utility.test_pdf_processor
```

### Test API Endpoints
```bash
python -m api.test_api
```

## 📝 Configuration

### Environment Variables (.env)
```bash
# Required
MISTRAL_API_KEY=your_api_key_here

# Optional - MongoDB (if using Auth Backend)
# MONGODB_URL=mongodb://localhost:27017
# SECRET_KEY=your_secret_key
```

### Module Configurations
- **Module A**: [module_a/config.py](module_a/config.py)
- **Module C**: [module_c/config.py](module_c/config.py)

## 🐛 Troubleshooting

### Backend Issues
- **Import errors**: Make sure virtual environment is activated
- **Vector DB empty**: Run the build scripts for modules A & C
- **API key errors**: Check `.env` file has valid `MISTRAL_API_KEY`

### Frontend Issues
- **Port 3000 in use**: Change port with `pnpm dev -- -p 3001`
- **Module not found**: Run `pnpm install` in Frontend directory
- **API connection failed**: Ensure backend is running on port 8000

### Common Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Rebuild vector databases
python -m module_a.build_vector_db
python -m module_c.indexer

# Clear pnpm cache
cd Frontend
pnpm store prune
pnpm install
```

## 📚 Documentation

- [Module A Documentation](module_a/README.md) - Law Explanation RAG Pipeline
- [Module C Documentation](module_c/README.md) - Letter Generation
- [PDF Processing Guide](utility/README.md) - PDF text extraction
- [Implementation Guides](docs/) - Detailed implementation workflows

---

> This project is under development as part of a hackathon.
