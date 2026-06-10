import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import SessionLocal, init_db, get_db, add_customer, get_customer, get_conversation_messages
from chatbot import CustomerSupportChatbot
import config

# Logging setup
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    debug=config.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    customer_id: str
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    success: bool
    conversation_id: str
    customer_id: str
    message: Optional[str] = None
    error: Optional[str] = None

class HistoryRequest(BaseModel):
    customer_id: str
    conversation_id: Optional[str] = None

class StartConversationRequest(BaseModel):
    customer_id: str
    subject: Optional[str] = None

class EndConversationRequest(BaseModel):
    conversation_id: str
    customer_id: str
    resolution: str = "resolved"

class EscalateRequest(BaseModel):
    conversation_id: str
    customer_id: str
    reason: Optional[str] = None

# Global chatbot instance
chatbot = None

def get_chatbot():
    """Get chatbot instance with database session"""
    global chatbot
    if chatbot is None:
        db = SessionLocal()
        chatbot = CustomerSupportChatbot(db)
    return chatbot

# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": config.APP_NAME,
        "version": config.APP_VERSION
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - sends a message and receives a response
    
    Args:
        customer_id: Unique customer identifier
        message: Customer's message
        conversation_id: Optional conversation ID
    
    Returns:
        ChatResponse with AI response
    """
    try:
        if not request.customer_id or not request.message:
            raise HTTPException(status_code=400, detail="customer_id and message are required")
        
        bot = get_chatbot()
        response = bot.chat(
            customer_id=request.customer_id,
            message=request.message,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(**response)
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{customer_id}")
async def get_conversations(customer_id: str):
    """
    Get all conversations for a customer
    
    Args:
        customer_id: Customer identifier
    
    Returns:
        List of conversations
    """
    try:
        bot = get_chatbot()
        result = bot.get_conversation_history(customer_id)
        return result
    except Exception as e:
        logger.error(f"Error retrieving conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{customer_id}/{conversation_id}")
async def get_conversation(customer_id: str, conversation_id: str):
    """
    Get messages from a specific conversation
    
    Args:
        customer_id: Customer identifier
        conversation_id: Conversation identifier
    
    Returns:
        Conversation messages
    """
    try:
        bot = get_chatbot()
        result = bot.get_conversation_history(customer_id, conversation_id)
        return result
    except Exception as e:
        logger.error(f"Error retrieving conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversations/start")
async def start_conversation(request: StartConversationRequest):
    """
    Start a new conversation
    
    Args:
        customer_id: Customer identifier
        subject: Conversation subject (optional)
    
    Returns:
        Conversation ID
    """
    try:
        bot = get_chatbot()
        conversation_id = bot.start_new_conversation(request.customer_id, request.subject)
        return {
            "success": True,
            "conversation_id": conversation_id,
            "customer_id": request.customer_id
        }
    except Exception as e:
        logger.error(f"Error starting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversations/end")
async def end_conversation(request: EndConversationRequest):
    """
    End a conversation
    
    Args:
        conversation_id: Conversation identifier
        customer_id: Customer identifier
        resolution: Resolution status (resolved, escalated, etc.)
    
    Returns:
        Success status
    """
    try:
        bot = get_chatbot()
        bot.end_conversation(request.conversation_id, request.customer_id, request.resolution)
        return {
            "success": True,
            "conversation_id": request.conversation_id,
            "status": request.resolution
        }
    except Exception as e:
        logger.error(f"Error ending conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversations/escalate")
async def escalate_conversation(request: EscalateRequest):
    """
    Escalate a conversation to human support
    
    Args:
        conversation_id: Conversation identifier
        customer_id: Customer identifier
        reason: Reason for escalation (optional)
    
    Returns:
        Escalation confirmation
    """
    try:
        bot = get_chatbot()
        result = bot.escalate_to_human(request.conversation_id, request.customer_id, request.reason)
        return result
    except Exception as e:
        logger.error(f"Error escalating conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/summary/{customer_id}/{conversation_id}")
async def get_summary(customer_id: str, conversation_id: str):
    """
    Get a summary of a conversation
    
    Args:
        customer_id: Customer identifier
        conversation_id: Conversation identifier
    
    Returns:
        Summary text
    """
    try:
        bot = get_chatbot()
        summary = bot.get_summary(customer_id, conversation_id)
        return {
            "success": True,
            "conversation_id": conversation_id,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error getting summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
