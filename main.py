import uuid
import os
import json
from typing import List, Optional, AsyncGenerator

from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# Database Configuration
DATABASE_URL = "mysql+aiomysql://<username>:<password>@localhost:3306/<database_name>"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# Database Model
class Chat(Base):
    __tablename__ = "chats"
    conversation_id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(50), index=True)
    messages = Column(JSON, nullable=False)  # Storing messages as a JSON list

# Pydantic Models
class ChatMessage(BaseModel):
    user_id: str
    message: str

class ChatConversation(BaseModel):
    conversation_id: str
    user_id: str
    messages: List[str]

class SummarizeRequest(BaseModel):
    conversation_id: str

class SummaryResponse(BaseModel):
    conversation_id: str
    summary: str

# FastAPI App Initialization
app = FastAPI(title="Chat Summarization API with MySQL & Gemini AI")

# Dependency for acquiring the session
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

# Create Database Tables on Startup
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Store Chat Messages (Insert Heavy Operation)
@app.post("/chats", response_model=ChatConversation)
async def store_chat(message: ChatMessage, session: AsyncSession = Depends(get_session)):
    conv_id = str(uuid.uuid4())
    chat = Chat(conversation_id=conv_id, user_id=message.user_id, messages=[message.message])
    
    session.add(chat)
    try:
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    
    return ChatConversation(conversation_id=conv_id, user_id=message.user_id, messages=[message.message])

# Retrieve Conversation by ID (Heavy SELECT Operation)
@app.get("/chats/{conversation_id}", response_model=ChatConversation)
async def get_chat(conversation_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Chat).filter_by(conversation_id=conversation_id))
    chat = result.scalars().first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return ChatConversation(conversation_id=chat.conversation_id, user_id=chat.user_id, messages=chat.messages)

# Add a Message to Existing Conversation
@app.post("/chats/{conversation_id}")
async def add_message(conversation_id: str, message: ChatMessage, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Chat).filter_by(conversation_id=conversation_id))
    chat = result.scalars().first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if chat.user_id != message.user_id:
        raise HTTPException(status_code=400, detail="User mismatch")
    
    chat.messages.append(message.message)
    try:
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    
    return {"detail": "Message added successfully"}

# Gemini AI Summarization Function
async def generate_summary(text: str) -> str:
    """Generates a summary using Gemini AI."""
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"Summarize this chat: {text}")
        return response.text.strip() if response and response.text else "No summary available."
    except Exception as e:
        return f"Error generating summary: {str(e)}"

# Chat Summarization Endpoint (LLM-Based)
@app.post("/chats/summarize", response_model=SummaryResponse)
async def summarize_chat(req: SummarizeRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Chat).filter_by(conversation_id=req.conversation_id))
    chat = result.scalars().first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    full_chat = " ".join(chat.messages)
    summary = await generate_summary(full_chat)
    
    return SummaryResponse(conversation_id=req.conversation_id, summary=summary)

# Get User's Chat History with Pagination
@app.get("/users/{user_id}/chats", response_model=List[ChatConversation])
async def get_user_chats(user_id: str, page: int = Query(1, ge=1), limit: int = Query(10, ge=1), session: AsyncSession = Depends(get_session)):
    stmt = select(Chat).filter_by(user_id=user_id)
    result = await session.execute(stmt)
    chats = result.scalars().all()
    
    start = (page - 1) * limit
    end = start + limit
    
    return [
        ChatConversation(conversation_id=chat.conversation_id, user_id=chat.user_id, messages=chat.messages)
        for chat in chats[start:end]
    ]

# Delete Conversation (Heavy DELETE Operation)
@app.delete("/chats/{conversation_id}")
async def delete_chat(conversation_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Chat).filter_by(conversation_id=conversation_id))
    chat = result.scalars().first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    await session.delete(chat)
    try:
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    
    return {"detail": "Conversation deleted successfully"}
