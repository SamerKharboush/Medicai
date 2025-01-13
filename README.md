# Clinical History (CH) App

An AI-powered Clinical History application that enables physicians to capture and process patient history through voice input.

## Features

- Voice-to-text conversion using OpenAI Whisper
- Natural Language Processing for medical text extraction
- Structured data storage
- Secure API endpoints
- Real-time transcription

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configurations
```

4. Run migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn app.main:app --reload
```

## Project Structure

```
medicai/
├── alembic/              # Database migrations
├── app/
│   ├── api/             # API endpoints
│   ├── core/            # Core functionality
│   ├── db/              # Database models and schemas
│   ├── services/        # Business logic
│   └── utils/           # Utility functions
├── tests/               # Test cases
└── requirements.txt     # Project dependencies
```

## Security

- HIPAA compliant
- Encrypted data in transit and at rest
- Secure authentication and authorization
