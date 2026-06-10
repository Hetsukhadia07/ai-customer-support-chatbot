import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def format_response(success: bool, data: Dict[str, Any], error: Optional[str] = None) -> Dict[str, Any]:
    """
    Format a standardized response
    
    Args:
        success: Whether the operation was successful
        data: Response data
        error: Error message if applicable
    
    Returns:
        Formatted response dictionary
    """
    response = {
        "success": success,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data
    }
    
    if error:
        response["error"] = error
    
    return response

def validate_customer_id(customer_id: str) -> bool:
    """Validate customer ID format"""
    if not customer_id or len(customer_id.strip()) == 0:
        return False
    return True

def validate_message(message: str) -> bool:
    """Validate message content"""
    if not message or len(message.strip()) == 0:
        return False
    if len(message) > 5000:  # Max message length
        return False
    return True

def clean_response_text(text: str) -> str:
    """Clean and normalize response text"""
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove multiple spaces
    text = " ".join(text.split())
    
    return text

def truncate_history(history: list, max_messages: int = 10) -> list:
    """Truncate conversation history to recent messages"""
    if len(history) > max_messages:
        return history[-max_messages:]
    return history

def format_conversation_for_display(messages: list) -> str:
    """Format conversation messages for display"""
    formatted = ""
    for msg in messages:
        role = "Customer" if msg.get("role") == "user" else "Support"
        content = msg.get("content", "")
        timestamp = msg.get("timestamp", "")
        
        formatted += f"\n[{timestamp}] {role}: {content}"
    
    return formatted

def get_intent_keywords(message: str) -> list:
    """Extract potential intent keywords from message"""
    keywords = []
    
    # Common support intent keywords
    intent_map = {
        "help": ["help", "assist", "support", "how"],
        "billing": ["bill", "payment", "charge", "invoice", "refund"],
        "account": ["account", "login", "password", "reset"],
        "technical": ["error", "bug", "crash", "not working", "broken"],
        "order": ["order", "delivery", "shipped", "tracking"],
        "complaint": ["complaint", "unhappy", "not satisfied", "issue"]
    }
    
    message_lower = message.lower()
    
    for intent, words in intent_map.items():
        for word in words:
            if word in message_lower:
                keywords.append(intent)
                break
    
    return list(set(keywords))

def calculate_sentiment(message: str) -> str:
    """
    Simple sentiment analysis based on keywords
    Returns: positive, neutral, or negative
    """
    negative_words = ["bad", "poor", "terrible", "awful", "hate", "disappointed", "angry"]
    positive_words = ["good", "great", "thank", "appreciate", "happy", "excellent", "love"]
    
    message_lower = message.lower()
    
    negative_count = sum(1 for word in negative_words if word in message_lower)
    positive_count = sum(1 for word in positive_words if word in message_lower)
    
    if negative_count > positive_count:
        return "negative"
    elif positive_count > negative_count:
        return "positive"
    else:
        return "neutral"

def extract_customer_info(message: str) -> Dict[str, str]:
    """Extract potential customer information from message"""
    info = {}
    
    # This is a simple example - in production, you'd use NER or regex patterns
    words = message.split()
    
    # Look for email pattern
    for word in words:
        if "@" in word and "." in word:
            info["email"] = word.lower()
            break
    
    return info

def rate_limit_check(customer_id: str, max_messages: int = 100, time_window: int = 60) -> bool:
    """
    Check if customer has exceeded message rate limit
    This is a placeholder - in production, use Redis or similar
    """
    # TODO: Implement proper rate limiting with Redis/cache
    return True

def log_conversation_event(event_type: str, customer_id: str, conversation_id: str, details: Dict[str, Any] = None):
    """Log important conversation events"""
    log_data = {
        "event_type": event_type,
        "customer_id": customer_id,
        "conversation_id": conversation_id,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details or {}
    }
    
    logger.info(f"Conversation Event: {json.dumps(log_data)}")

def validate_conversation_id(conversation_id: str) -> bool:
    """Validate conversation ID format (UUID)"""
    if not conversation_id:
        return False
    
    try:
        # Simple UUID validation
        parts = conversation_id.split("-")
        if len(parts) != 5:
            return False
        return True
    except:
        return False

def calculate_response_time(start_time: float, end_time: float) -> float:
    """Calculate response time in milliseconds"""
    return (end_time - start_time) * 1000
