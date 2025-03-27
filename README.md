# Chat Summarization API with MySQL

This project demonstrates a simple FastAPI-based REST API for handling chat messages and generating summaries, using MySQL as the storage backend. The key features include:

- **Storing chat messages:** `POST /chats`
- **Retrieving a conversation:** `GET /chats/{conversation_id}`
- **Adding messages:** `POST /chats/{conversation_id}`
- **Chat summarization:** `POST /chats/summarize`
- **User chat history (pagination):** `GET /users/{user_id}/chats?page=1&limit=10`
- **Deleting a conversation:** `DELETE /chats/{conversation_id}`

## Requirements

- Python 3.8+
- MySQL Server (with a database created)
- Dependencies:
  - FastAPI
  - Uvicorn
  - SQLAlchemy (1.4+)
  - aiomysql

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/fastapi-chat-mysql.git
   cd fastapi-chat-mysql
