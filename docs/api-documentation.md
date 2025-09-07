# API Documentation

## Overview

The Notes App Backend provides a RESTful API for note management with Firebase authentication and AI-powered features.

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All endpoints require Firebase ID token authentication in the Authorization header:

```
Authorization: Bearer <firebase_id_token>
```

## Endpoints

### Notes Management

#### GET /notes
Retrieve all notes for the authenticated user.

**Query Parameters:**
- `include_deleted` (boolean, optional): Include soft-deleted notes (default: false)
- `limit` (integer, optional): Number of notes to return (default: 20, max: 100)
- `offset` (integer, optional): Number of notes to skip (default: 0)

**Response:**
```json
[
  {
    "id": "string",
    "title": "string",
    "content": "string",
    "is_deleted": false,
    "user_id": "string",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized
- `500`: Internal Server Error

#### POST /notes
Create a new note.

**Request Body:**
```json
{
  "title": "string",
  "content": "string",
  "is_deleted": false
}
```

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "content": "string",
  "is_deleted": false,
  "user_id": "string",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `500`: Internal Server Error

#### PUT /notes/{note_id}
Update an existing note.

**Path Parameters:**
- `note_id` (string): ID of the note to update

**Request Body:**
```json
{
  "title": "string",
  "content": "string",
  "is_deleted": false
}
```

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "content": "string",
  "is_deleted": false,
  "user_id": "string",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `500`: Internal Server Error

#### DELETE /notes/{note_id}
Soft delete a note.

**Path Parameters:**
- `note_id` (string): ID of the note to delete

**Response:**
```
No Content (204)
```

**Status Codes:**
- `204`: No Content
- `401`: Unauthorized
- `404`: Not Found
- `500`: Internal Server Error

### AI Features

#### POST /ai/generate-title
Generate a title for note content using AI.

**Request Body:**
```json
{
  "content": "string"
}
```

**Response:**
```json
{
  "result": "string",
  "success": true
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `500`: Internal Server Error

#### POST /ai/summarize
Summarize note content using AI.

**Request Body:**
```json
{
  "content": "string"
}
```

**Response:**
```json
{
  "result": "string",
  "success": true
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `500`: Internal Server Error

#### POST /ai/improve-content
Improve note content using AI.

**Request Body:**
```json
{
  "content": "string"
}
```

**Response:**
```json
{
  "result": "string",
  "success": true
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `500`: Internal Server Error

#### POST /ai/suggest-tags
Suggest tags for note content using AI.

**Request Body:**
```json
{
  "content": "string"
}
```

**Response:**
```json
{
  "result": "string",
  "success": true
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `500`: Internal Server Error

## Data Models

### Note
```json
{
  "id": "string",
  "title": "string",
  "content": "string",
  "is_deleted": false,
  "user_id": "string",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### NoteCreate
```json
{
  "title": "string",
  "content": "string",
  "is_deleted": false
}
```

### NoteUpdate
```json
{
  "title": "string",
  "content": "string",
  "is_deleted": false
}
```

### AIRequest
```json
{
  "content": "string"
}
```

### AIResponse
```json
{
  "result": "string",
  "success": true
}
```

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message description"
}
```

### Common Error Codes
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

### Validation Errors
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Rate Limiting

### Limits
- **General API**: 1000 requests per hour per user
- **AI Features**: 100 requests per hour per user
- **Burst Limit**: 50 requests per minute

### Headers
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## CORS Configuration

### Allowed Origins
- `http://localhost:3000`
- `http://localhost:8080`
- Production domains (configured in environment)

### Allowed Methods
- `GET`
- `POST`
- `PUT`
- `DELETE`
- `OPTIONS`

### Allowed Headers
- `Authorization`
- `Content-Type`
- `Accept`

## WebSocket Support

### Real-time Updates
WebSocket endpoint for real-time note updates:

```
ws://localhost:8000/ws/notes
```

### Authentication
WebSocket connections require Firebase ID token in query parameter:

```
ws://localhost:8000/ws/notes?token=<firebase_id_token>
```

### Message Format
```json
{
  "type": "note_updated",
  "data": {
    "id": "string",
    "title": "string",
    "content": "string",
    "is_deleted": false,
    "user_id": "string",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

## SDK Examples

### JavaScript/TypeScript
```javascript
const apiClient = {
  baseURL: 'http://localhost:8000/api/v1',
  token: 'your-firebase-id-token',
  
  async getNotes() {
    const response = await fetch(`${this.baseURL}/notes`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  },
  
  async createNote(note) {
    const response = await fetch(`${this.baseURL}/notes`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(note)
    });
    return response.json();
  }
};
```

### Python
```python
import requests

class NotesAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def get_notes(self):
        response = requests.get(f'{self.base_url}/notes', headers=self.headers)
        return response.json()
    
    def create_note(self, note):
        response = requests.post(f'{self.base_url}/notes', 
                               json=note, headers=self.headers)
        return response.json()
```

### cURL Examples
```bash
# Get notes
curl -X GET "http://localhost:8000/api/v1/notes" \
  -H "Authorization: Bearer your-firebase-id-token" \
  -H "Content-Type: application/json"

# Create note
curl -X POST "http://localhost:8000/api/v1/notes" \
  -H "Authorization: Bearer your-firebase-id-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Note",
    "content": "This is my note content",
    "is_deleted": false
  }'

# Update note
curl -X PUT "http://localhost:8000/api/v1/notes/note-id" \
  -H "Authorization: Bearer your-firebase-id-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Note",
    "content": "Updated content",
    "is_deleted": false
  }'

# Delete note
curl -X DELETE "http://localhost:8000/api/v1/notes/note-id" \
  -H "Authorization: Bearer your-firebase-id-token"
```

## Testing

### Postman Collection
Import the Postman collection for easy API testing:

```json
{
  "info": {
    "name": "Notes App API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get Notes",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{firebase_token}}"
          }
        ],
        "url": {
          "raw": "{{base_url}}/notes",
          "host": ["{{base_url}}"],
          "path": ["notes"]
        }
      }
    }
  ]
}
```

### Test Environment
- **Base URL**: `http://localhost:8000/api/v1`
- **Test Token**: Use Firebase test user token
- **Test Data**: Pre-populated test notes

## Monitoring

### Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "ai_service": "healthy"
  }
}
```

### Metrics
```
GET /metrics
```

**Response:**
```json
{
  "requests_total": 1000,
  "requests_per_second": 10.5,
  "average_response_time": 150,
  "error_rate": 0.01
}
```

## Changelog

### Version 1.0.0
- Initial API release
- Notes CRUD operations
- Firebase authentication
- AI features integration
- Offline-first support

### Future Versions
- Real-time updates via WebSocket
- Advanced search capabilities
- Bulk operations
- Export/import functionality
