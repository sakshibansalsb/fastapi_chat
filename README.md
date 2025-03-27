# Chat Summarization API with MySQL & Gemini AI

## Project Overview
This project is a FastAPI-based chat summarization system that stores and retrieves chat conversations in a MySQL database and utilizes Google Gemini AI for generating summaries of chat conversations.

## Features
- Store and retrieve chat conversations
- Add messages to existing conversations
- Summarize chat conversations using Google Gemini AI
- Paginated retrieval of user chat history
- Delete conversations from the database

## Technologies Used
- **FastAPI** for API development
- **MySQL** with SQLAlchemy & aiomysql for async database operations
- **Google Gemini AI** for chat summarization
- **Pydantic** for data validation
- **Uvicorn** for ASGI server

## Installation
### Prerequisites
- Python 3.8+
- MySQL database
- Google Gemini API Key

### Steps to Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file and add the following:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   ```
5. Update the `DATABASE_URL` in `main.py` with your MySQL credentials:
   ```python
   DATABASE_URL = "mysql+aiomysql://<username>:<password>@localhost:3306/<database_name>"
   ```
6. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints
### Store Chat Messages
```http
POST /chats
```
#### Request Body:
```json
{
  "user_id": "user123",
  "message": "Hello, how are you?"
}
```
#### Response:
```json
{
  "conversation_id": "uuid-generated",
  "user_id": "user123",
  "messages": ["Hello, how are you?"]
}
```

### Retrieve Conversation by ID
```http
GET /chats/{conversation_id}
```
#### Response:
```json
{
  "conversation_id": "uuid-generated",
  "user_id": "user123",
  "messages": ["Hello, how are you?"]
}
```

### Add a Message to Existing Conversation
```http
POST /chats/{conversation_id}
```
#### Request Body:
```json
{
  "user_id": "user123",
  "message": "I'm doing well!"
}
```
#### Response:
```json
{
  "detail": "Message added successfully"
}
```

### Summarize Chat Conversation
```http
POST /chats/summarize
```
#### Request Body:
```json
{
  "conversation_id": "uuid-generated"
}
```
#### Response:
```json
{
  "conversation_id": "uuid-generated",
  "summary": "Shortened summary of the chat."
}
```

### Get User's Chat History (Paginated)
```http
GET /users/{user_id}/chats?page=1&limit=10
```
#### Response:
```json
[
  {
    "conversation_id": "uuid-generated",
    "user_id": "user123",
    "messages": ["Hello", "How are you?"]
  }
]
```

### Delete a Conversation
```http
DELETE /chats/{conversation_id}
```
#### Response:
```json
{
  "detail": "Conversation deleted successfully"
}
```

## License
This project is for educational purposes and is open-source. Modify and use it as needed.

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

