from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import config

# Database setup
Base = declarative_base()
engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Models
class Customer(Base):
    """Customer model for storing customer information"""
    __tablename__ = "customers"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(Text, nullable=True)  # JSON string for additional data

class Conversation(Base):
    """Conversation model for storing chat messages"""
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    subject = Column(String, nullable=True)
    status = Column(String, default="open")  # open, resolved, escalated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(Base):
    """Message model for storing individual messages in a conversation"""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, index=True)
    customer_id = Column(String, index=True)
    role = Column(String)  # "user" or "assistant"
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata = Column(Text, nullable=True)  # JSON string for additional data

class ConversationSummary(Base):
    """Stores summaries of long conversations for efficient retrieval"""
    __tablename__ = "conversation_summaries"
    
    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    summary = Column(Text)
    message_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized successfully")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_customer(db, customer_id: str, name: str = None, email: str = None, metadata: str = None):
    """Add a new customer"""
    customer = Customer(id=customer_id, name=name, email=email, metadata=metadata)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

def get_customer(db, customer_id: str):
    """Get customer by ID"""
    return db.query(Customer).filter(Customer.id == customer_id).first()

def add_conversation(db, conversation_id: str, customer_id: str, subject: str = None):
    """Create a new conversation"""
    conversation = Conversation(id=conversation_id, customer_id=customer_id, subject=subject)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

def get_conversation(db, conversation_id: str):
    """Get conversation by ID"""
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()

def get_customer_conversations(db, customer_id: str):
    """Get all conversations for a customer"""
    return db.query(Conversation).filter(Conversation.customer_id == customer_id).all()

def add_message(db, message_id: str, conversation_id: str, customer_id: str, role: str, content: str, metadata: str = None):
    """Add a message to a conversation"""
    message = Message(
        id=message_id,
        conversation_id=conversation_id,
        customer_id=customer_id,
        role=role,
        content=content,
        metadata=metadata
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_conversation_messages(db, conversation_id: str):
    """Get all messages in a conversation"""
    return db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.timestamp).all()

def get_customer_messages(db, customer_id: str, limit: int = 100):
    """Get recent messages for a customer across all conversations"""
    return db.query(Message).filter(Message.customer_id == customer_id).order_by(Message.timestamp.desc()).limit(limit).all()

def update_conversation_status(db, conversation_id: str, status: str):
    """Update conversation status"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.status = status
        db.commit()
    return conversation

def add_summary(db, summary_id: str, customer_id: str, summary: str, message_count: int):
    """Add a conversation summary"""
    summary_obj = ConversationSummary(
        id=summary_id,
        customer_id=customer_id,
        summary=summary,
        message_count=message_count
    )
    db.add(summary_obj)
    db.commit()
    db.refresh(summary_obj)
    return summary_obj

def get_customer_summaries(db, customer_id: str):
    """Get all summaries for a customer"""
    return db.query(ConversationSummary).filter(ConversationSummary.customer_id == customer_id).all()
