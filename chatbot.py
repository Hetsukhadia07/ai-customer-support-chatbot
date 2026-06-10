import uuid
from typing import Optional, List, Dict, Any
from langchain.llms import HuggingFaceHub
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from memory import PersistentMemory, ConversationMemory
import config
import logging

logger = logging.getLogger(__name__)

class CustomerSupportChatbot:
    """Main chatbot class for customer support"""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.memory = PersistentMemory(db_session)
        self.llm = None
        self.initialize_llm()
    
    def initialize_llm(self):
        """Initialize the Hugging Face LLM"""
        try:
            self.llm = HuggingFaceHub(
                repo_id=config.MODEL_NAME,
                model_kwargs={
                    "temperature": config.MODEL_TEMPERATURE,
                    "max_new_tokens": config.MODEL_MAX_TOKENS,
                }
            )
            logger.info(f"✓ LLM initialized with model: {config.MODEL_NAME}")
        except Exception as e:
            logger.error(f"✗ Failed to initialize LLM: {str(e)}")
            raise
    
    def create_prompt_template(self) -> PromptTemplate:
        """Create a custom prompt template for customer support"""
        template = """You are a professional customer support assistant. 
        
{history}

Customer: {input}
Support Assistant:"""
        
        return PromptTemplate(
            input_variables=["history", "input"],
            template=template
        )
    
    def chat(self, customer_id: str, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Main chat method - receives customer message and returns response
        
        Args:
            customer_id: Unique customer identifier
            message: Customer's message
            conversation_id: Optional specific conversation ID
        
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Create or use existing conversation
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            # Load existing conversation history from database
            self.memory.load_conversation_from_db(customer_id, conversation_id)
            
            # Get conversation context
            context = self.memory.in_memory.get_context_window(customer_id, conversation_id)
            
            # Store user message
            self.memory.save_message_to_db(customer_id, conversation_id, "user", message)
            
            # Create prompt with context
            prompt = self.create_prompt_template()
            
            # Generate response
            full_context = f"{config.SYSTEM_PROMPT}\n\n{context}"
            response_text = self.llm(prompt.format(history=full_context, input=message))
            
            # Clean response
            response_text = response_text.strip()
            
            # Store assistant response
            self.memory.save_message_to_db(customer_id, conversation_id, "assistant", response_text)
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "customer_id": customer_id,
                "message": response_text,
                "timestamp": str(uuid.uuid4())
            }
        
        except Exception as e:
            logger.error(f"✗ Error in chat: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "customer_id": customer_id,
                "conversation_id": conversation_id or "unknown"
            }
    
    def get_conversation_history(self, customer_id: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve conversation history
        
        Args:
            customer_id: Customer ID
            conversation_id: Optional specific conversation ID
        
        Returns:
            Conversation history
        """
        try:
            if conversation_id:
                history = self.memory.in_memory.get_conversation_history(customer_id, conversation_id)
                return {
                    "success": True,
                    "conversation_id": conversation_id,
                    "messages": history
                }
            else:
                all_history = self.memory.in_memory.get_customer_history(customer_id)
                return {
                    "success": True,
                    "customer_id": customer_id,
                    "conversations": all_history
                }
        except Exception as e:
            logger.error(f"✗ Error retrieving history: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_customer_context(self, customer_id: str, conversation_id: str) -> str:
        """Get formatted context for a specific conversation"""
        return self.memory.get_full_context(customer_id, conversation_id)
    
    def start_new_conversation(self, customer_id: str, subject: str = None) -> str:
        """Start a new conversation"""
        conversation_id = str(uuid.uuid4())
        
        # Save to database if session available
        if self.db_session:
            from database import add_conversation
            add_conversation(self.db_session, conversation_id, customer_id, subject)
        
        logger.info(f"New conversation started: {conversation_id} for customer: {customer_id}")
        return conversation_id
    
    def end_conversation(self, conversation_id: str, customer_id: str, resolution: str = "resolved"):
        """End a conversation and mark it as resolved"""
        if self.db_session:
            from database import update_conversation_status
            update_conversation_status(self.db_session, conversation_id, resolution)
        
        logger.info(f"Conversation ended: {conversation_id} - Status: {resolution}")
        return True
    
    def get_summary(self, customer_id: str, conversation_id: str) -> str:
        """Generate a summary of the conversation"""
        history = self.memory.in_memory.get_conversation_history(customer_id, conversation_id)
        
        if not history:
            return "No conversation history available."
        
        # Create summary prompt
        messages_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in history])
        
        summary_prompt = f"""Summarize the following customer support conversation in 2-3 sentences:

{messages_text}

Summary:"""
        
        try:
            summary = self.llm(summary_prompt)
            return summary.strip()
        except Exception as e:
            logger.error(f"✗ Error generating summary: {str(e)}")
            return "Unable to generate summary."
    
    def escalate_to_human(self, conversation_id: str, customer_id: str, reason: str = None) -> Dict[str, Any]:
        """Mark conversation for human handoff"""
        if self.db_session:
            from database import update_conversation_status
            update_conversation_status(self.db_session, conversation_id, "escalated")
        
        logger.info(f"Conversation escalated to human: {conversation_id} - Reason: {reason}")
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "status": "escalated",
            "reason": reason,
            "message": "This issue has been escalated to our human support team. A representative will contact you shortly."
        }
