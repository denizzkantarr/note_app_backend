# Notes App Backend

A FastAPI-based backend service for the Notes App, providing comprehensive authentication, notes management, and AI-powered features with Firebase integration.

## Features

- **🔐 Authentication**: Firebase Authentication integration with JWT token validation and password security
- **📝 Notes CRUD**: Complete Create, Read, Update, Delete operations with full validation
- **🗑️ Soft Delete**: Notes are marked as deleted instead of being permanently removed
- **🔄 Restore**: Deleted notes can be restored
- **👤 User Isolation**: Users can only access their own notes (secure data separation)
- **🤖 AI Features**: AI-powered note summarization, content improvement, idea generation, and tag suggestions
- **📊 Pagination**: Efficient data loading with configurable page sizes
- **🔍 Search & Filter**: Advanced note filtering and search capabilities
- **📱 RESTful API**: Clean and well-documented API endpoints with OpenAPI/Swagger
- **⚡ Performance**: Optimized database queries and caching support
- **🛡️ Error Handling**: Comprehensive error handling with meaningful messages
- **🌐 CORS Support**: Configured for cross-origin requests from frontend
- **📈 Health Monitoring**: Built-in health check endpoints for monitoring
- **🎨 Color Support**: Notes support different color themes (primary, secondary, tertiary)
- **📌 Pin Support**: Notes can be pinned for quick access

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs with automatic OpenAPI documentation
- **Firebase Admin SDK**: For authentication and Firestore database operations
- **Pydantic**: Data validation and settings management with type hints
- **Python 3.8+**: Programming language (tested with Python 3.13)
- **Uvicorn**: ASGI server for production deployment
- **Hugging Face API**: AI-powered features integration (optional)
- **NLTK & TextBlob**: Natural language processing for AI features
- **Requests**: HTTP client for external API calls

## Project Structure

```
notes_app_backend/
├── app/
│   ├── api/                    # API routes
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── notes.py           # Notes CRUD endpoints
│   │   └── ai_features.py     # AI-powered features endpoints
│   ├── core/                  # Core functionality
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Firebase database setup
│   │   ├── security.py        # Authentication utilities
│   │   └── cache.py           # Caching layer
│   ├── models/                # Pydantic models
│   │   └── note.py            # Note data models
│   ├── schemas/               # API schemas
│   │   └── user.py            # User schemas
│   ├── services/              # Business logic
│   │   ├── note_service_optimized.py  # Optimized notes service
│   │   ├── firebase_auth_service.py   # Firebase authentication service
│   │   └── local_ai_service.py        # Local AI service with Hugging Face
│   └── utils/                 # Utility functions
├── config/                    # Configuration files
│   └── firebase-service-account.json  # Firebase service account
├── docs/                      # Documentation
│   ├── ai-features.md         # AI features documentation
│   ├── api-documentation.md   # API documentation
│   └── architecture.md        # Architecture documentation
├── tests/                     # Test files
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── firestore_structure.md     # Firestore database structure
└── .env.example              # Environment variables template
```

## Quick Start

### Prerequisites

- **Python 3.8+** (Tested with Python 3.13)
- **Firebase project** with Authentication and Firestore enabled
- **Firebase service account key** (JSON file)

### Installation & Setup

1. **Clone and navigate to the project**
   ```bash
   git clone <repository-url>
   cd notes_app_backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   
   **Important:** Edit `.env` file with your actual Firebase credentials:
   ```env
   # Firebase Configuration (Required)
   FIREBASE_PROJECT_ID=your_actual_project_id
   FIREBASE_PRIVATE_KEY_ID=your_actual_private_key_id
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_ACTUAL_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
   FIREBASE_CLIENT_EMAIL=your_actual_client_email@project.iam.gserviceaccount.com
   FIREBASE_CLIENT_ID=your_actual_client_id
   FIREBASE_CLIENT_X509_CERT_URL=your_actual_cert_url
   
   # JWT Configuration
   SECRET_KEY=your_super_secret_key_here_change_this_in_production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # CORS Configuration
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:8000
   
   # AI Configuration (Optional)
   HUGGINGFACE_TOKEN=your_huggingface_token_here
   
   # Environment
   ENVIRONMENT=development
   ```

5. **Start the server**
   ```bash
   python main.py
   ```
   
   **Alternative with uvicorn:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Verify the server is running**
   ```bash
   curl http://localhost:8000/health
   # Expected response: {"status":"healthy","environment":"development"}
   ```

## API Documentation

Once the server is running, you can access:

- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc
- **OpenAPI schema**: http://localhost:8000/openapi.json

## API Endpoints

### Authentication
All endpoints require Firebase ID token in the Authorization header:
```
Authorization: Bearer <firebase_id_token>
```

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password",
  "confirm_password": "secure_password",
  "name": "User Name"
}
```

#### Login User
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

#### Get Current User
```http
GET /api/v1/auth/me
```

#### Update User Profile
```http
PUT /api/v1/auth/profile
Content-Type: application/json

{
  "name": "Updated Name"
}
```

### Notes Endpoints

#### Get Notes
```http
GET /api/v1/notes
Query Parameters:
- include_deleted (boolean, optional): Include deleted notes
- limit (integer, optional): Number of notes to return (default: 20)
- offset (integer, optional): Number of notes to skip (default: 0)
```

#### Get Single Note
```http
GET /api/v1/notes/{note_id}
```

#### Create Note
```http
POST /api/v1/notes
Content-Type: application/json

{
  "title": "Note Title",
  "content": "Note content here",
  "is_deleted": false,
  "is_pinned": false,
  "format": "text",
  "color": "primary"
}
```

#### Update Note
```http
PUT /api/v1/notes/{note_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "content": "Updated content",
  "is_deleted": false,
  "is_pinned": true,
  "format": "text",
  "color": "secondary"
}
```

#### Delete Note (Soft Delete)
```http
DELETE /api/v1/notes/{note_id}
```

#### Restore Note
```http
POST /api/v1/notes/{note_id}/restore
```

### AI Features Endpoints

#### Generate Title
```http
POST /api/v1/ai/generate-title
Content-Type: application/json

{
  "content": "Note content to generate title from"
}
```

#### Summarize Content
```http
POST /api/v1/ai/summarize
Content-Type: application/json

{
  "content": "Long content to summarize"
}
```

#### Improve Content
```http
POST /api/v1/ai/improve-content
Content-Type: application/json

{
  "content": "Content with grammar and style issues"
}
```

#### Generate Ideas
```http
POST /api/v1/ai/generate-ideas
Content-Type: application/json

{
  "content": "Content to generate ideas from"
}
```

#### Suggest Tags
```http
POST /api/v1/ai/suggest-tags
Content-Type: application/json

{
  "content": "Content to suggest tags for"
}
```

### Test Endpoints (No Authentication Required)

#### Test Generate Title
```http
POST /api/v1/ai/test/generate-title
Content-Type: application/json

{
  "content": "Test content"
}
```

#### Test Improve Content
```http
POST /api/v1/ai/test/improve-content
Content-Type: application/json

{
  "content": "Test content"
}
```

#### Test Generate Ideas
```http
POST /api/v1/ai/test/generate-ideas
Content-Type: application/json

{
  "content": "Test content"
}
```

## Data Models

### Note Model
```json
{
  "id": "string",
  "title": "string",
  "content": "string",
  "is_deleted": false,
  "is_pinned": false,
  "user_id": "string",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "format": "text",
  "color": "primary"
}
```

### Note Create Model
```json
{
  "title": "string",
  "content": "string",
  "is_deleted": false,
  "is_pinned": false,
  "format": "text",
  "color": "primary"
}
```

### Note Update Model
```json
{
  "title": "string (optional)",
  "content": "string (optional)",
  "is_deleted": "boolean (optional)",
  "is_pinned": "boolean (optional)",
  "format": "string (optional)",
  "color": "string (optional)"
}
```

### User Model
```json
{
  "uid": "string",
  "email": "string",
  "name": "string",
  "email_verified": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### AI Request Model
```json
{
  "content": "string"
}
```

### AI Response Model
```json
{
  "result": "string",
  "success": true
}
```

## Error Handling

The API returns standardized error responses:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `204`: No Content
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
isort .
```

### Linting
```bash
flake8
```

## Deployment

### Environment Variables for Production
- Set `ENVIRONMENT=production`
- Use strong `SECRET_KEY`
- Configure proper `ALLOWED_ORIGINS`
- Ensure Firebase credentials are properly set

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Services

### Note Service (`note_service_optimized.py`)
- **CRUD Operations**: Create, read, update, delete notes
- **Soft Delete**: Mark notes as deleted instead of permanent removal
- **Restore**: Restore deleted notes
- **User Isolation**: Ensure users only access their own notes
- **Pagination**: Efficient data loading with configurable limits
- **Search & Filter**: Advanced filtering capabilities

### Firebase Auth Service (`firebase_auth_service.py`)
- **User Registration**: Create new user accounts
- **User Login**: Authenticate users
- **Token Validation**: Verify Firebase ID tokens
- **User Profile Management**: Update user information

### Local AI Service (`local_ai_service.py`)
- **Title Generation**: Generate titles from content using NLTK
- **Content Summarization**: Summarize long content using TextBlob
- **Content Improvement**: Fix grammar, punctuation, and style issues
- **Idea Generation**: Generate ideas using Hugging Face API or local fallback
- **Tag Suggestions**: Suggest relevant tags for content
- **Sentiment Analysis**: Analyze content sentiment

## Security Considerations

- Firebase ID tokens are validated on every request
- Users can only access their own notes
- CORS is configured for specific origins
- Input validation using Pydantic models
- Soft delete prevents accidental data loss
- Password security with strength validation

## Troubleshooting

### Common Issues

#### 1. **"python: command not found"**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate
# Or use python3 instead of python
python3 main.py
```

#### 2. **Firebase Authentication Errors**
- Verify your `.env` file has correct Firebase credentials
- Check that Firebase project has Authentication and Firestore enabled
- Ensure service account has proper permissions

#### 3. **Port Already in Use**
```bash
# Kill existing process
pkill -f uvicorn
# Or use a different port
uvicorn main:app --port 8001
```

#### 4. **Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 5. **CORS Issues**
- Check `ALLOWED_ORIGINS` in `.env` file
- Ensure frontend URL is included in the list

#### 6. **AI Features Not Working**
```bash
# Install NLTK data
python -m textblob.download_corpora

# Check Hugging Face token
echo $HUGGINGFACE_TOKEN

# Test AI endpoints
curl -X POST "http://localhost:8000/api/v1/ai/test/generate-title" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test content"}'
```

#### 7. **TextBlob Missing Data**
```bash
# Download required NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
```

### Health Check
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","environment":"development"}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Additional Documentation

For more detailed information, please refer to the documentation in the `/docs` folder:

- [Architecture Documentation](docs/architecture.md) - Detailed system architecture and design patterns
- [AI Features Documentation](docs/ai-features.md) - AI-powered features and product vision
- [API Documentation](docs/api-documentation.md) - Complete API reference and examples

## License

This project is licensed under the MIT License.
