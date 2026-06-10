from typing import List, Dict, Any
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from datetime import datetime
import json
import uuid

class ConversationMemory:
    """Custom conversation memory manager for storing and retrieving chat history"""
    
    def __init__(self, memory_type: str = "buffer", max_history: int = 10):
        self.memory_type = memory_type
        self.max_history = max_history
        self.conversations = {}  # {customer_id: {conversation_id: messages}}
    
    def add_message(self, customer_id: str, conversation_id: str, role: str, content: str):
        """Add a message to the conversation memory"""
        if customer_id not in self.conversations:
            self.conversations[customer_id] = {}
        
        if conversation_id not in self.conversations[customer_id]:
            self.conversations[customer_id][conversation_id] = []
        
        message = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.conversations[customer_id][conversation_id].append(message)
        
        # Enforce max history limit
        if len(self.conversations[customer_id][conversation_id]) > self.max_history * 2:
            self.conversations[customer_id][conversation_id] = self.conversations[customer_id][conversation_id][-self.max_history*2:]
    
    def get_conversation_history(self, customer_id: str, conversation_id: str) -> List[Dict[str, Any]]:
        """Retrieve conversation history"""
        if customer_id in self.conversations and conversation_id in self.conversations[customer_id]:
            return self.conversations[customer_id][conversation_id]
        return []
    
    def get_customer_history(self, customer_id: str) -> Dict[str, Any]:
        """Get all conversation history for a customer"""
        if customer_id in self.conversations:
            return self.conversations[customer_id]
        return {}
    
    def format_history_for_llm(self, messages: List[Dict[str, Any]]) -> str:
        """Format conversation history for LLM context"""
        formatted = "Previous Conversation History:\n"
        for msg in messages[-self.max_history:]:  # Only include recent history
            role = msg["role"].upper()
            formatted += f"{role}: {msg['content']}\n"
        return formatted
    
    def get_langchain_messages(self, messages: List[Dict[str, Any]]) -> List[BaseMessage]:
        """Convert messages to LangChain format"""
        langchain_messages = []
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            else:
                langchain_messages.append(AIMessage(content=msg["content"]))
        return langchain_messages
    
    def clear_conversation(self, customer_id: str, conversation_id: str):
        """Clear a specific conversation"""
        if customer_id in self.conversations and conversation_id in self.conversations[customer_id]:
            del self.conversations[customer_id][conversation_id]
    
    def clear_customer_history(self, customer_id: str):
        """Clear all conversations for a customer"""
        if customer_id in self.conversations:
            del self.conversations[customer_id]
    
    def get_context_window(self, customer_id: str, conversation_id: str, window_size: int = 5) -> str:
        """Get a context window of recent messages for LLM"""
        history = self.get_conversation_history(customer_id, conversation_id)
        recent = history[-window_size:] if len(history) > window_size else history
        
        context = "Recent Conversation Context:\n"
        for msg in recent:
            role = "CUSTOMER" if msg["role"] == "user" else "SUPPORT"
            context += f"{role}: {msg['content']}\n"
        
        return context if len(history) > 0 else "No previous conversation history."

class PersistentMemory:
    """Wrapper for persistent memory operations with database"""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.in_memory = ConversationMemory()
    
    def save_message_to_db(self, customer_id: str, conversation_id: str, role: str, content: str):
        """Save message to both memory and database"""
        from database import add_message
        
        # Add to in-memory storage
        self.in_memory.add_message(customer_id, conversation_id, role, content)
        
        # Add to database if session available
        if self.db_session:
            message_id = str(uuid.uuid4())
            add_message(
                self.db_session,
                message_id,
                conversation_id,
                customer_id,
                role,
                content
            )
    
    def load_conversation_from_db(self, customer_id: str, conversation_id: str):
        """Load conversation from database into memory"""
        from database import get_conversation_messages
        
        if self.db_session:
            db_messages = get_conversation_messages(self.db_session, conversation_id)
            for msg in db_messages:
                self.in_memory.add_message(
                    customer_id,
                    conversation_id,
                    msg.role,
                    msg.content
                )
    
    def get_full_context(self, customer_id: str, conversation_id: str) -> str:
        """Get complete context from both memory and database"""
        history = self.in_memory.get_conversation_history(customer_id, conversation_id)
        return self.in_memory.format_history_for_llm(history)
