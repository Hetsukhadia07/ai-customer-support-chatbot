# AI Customer Support Chatbot

A Python-based customer support chatbot using LangChain and Hugging Face. Features intelligent conversation handling with persistent memory storage, context-aware responses, multi-turn dialog support, and conversation history retrieval. Includes REST API for seamless integration, real-time chat capabilities, and analytics for support automation.

## Features

- 🤖 **AI Intelligence**: Powered by Hugging Face language models via LangChain
- 💾 **Conversation Memory**: Stores and retrieves customer conversations
- 🔄 **Context-Aware Responses**: Understands customer intent from dialog history
- 🛠️ **REST API**: Easy integration with web and mobile applications
- 📊 **Conversation Analytics**: Track and analyze support interactions
- 🔐 **Secure**: Environment-based configuration

## Tech Stack

- **Python 3.8+**
- **LangChain**: LLM orchestration framework
- **Hugging Face**: Pre-trained language models
- **FastAPI**: Modern web framework
- **SQLite**: Lightweight database (can upgrade to PostgreSQL)
- **Pydantic**: Data validation

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Hetsukhadia07/ai-customer-support-chatbot.git
   cd ai-customer-support-chatbot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Hugging Face API token
   ```

5. **Initialize the database**
   ```bash
   python -c "from database import init_db; init_db()"
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

### Chat
- **POST** `/api/chat` - Send a message to the chatbot
  ```json
  {
    "customer_id": "cust_123",
    "message": "I need help with my order"
  }
  ```

### Conversation History
- **GET** `/api/conversations/{customer_id}` - Get all conversations for a customer
- **GET** `/api/conversations/{customer_id}/history` - Get conversation history with context

### Health Check
- **GET** `/health` - Check if the service is running

## Usage Example

```python
from chatbot import CustomerSupportChatbot

# Initialize the chatbot
chatbot = CustomerSupportChatbot()

# Have a conversation
response = chatbot.chat(customer_id="cust_123", message="How do I track my order?")
print(response)

# Get conversation history
history = chatbot.get_conversation_history(customer_id="cust_123")
print(history)
```

## Configuration

Edit `config.py` to customize:
- Model selection
- Temperature and other LLM parameters
- Database settings
- API port and host
- Conversation memory limits

## Project Structure

```
ai-customer-support-chatbot/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── config.py              # Configuration settings
├── database.py            # Database setup and models
├── chatbot.py             # Core chatbot logic with LangChain
├── memory.py              # Conversation memory management
├── api.py                 # REST API endpoints
├── utils.py               # Helper functions
└── README.md              # Documentation
```

## Environment Variables

Create a `.env` file with:
```
HUGGING_FACE_API_KEY=your_token_here
DATABASE_URL=sqlite:///./chatbot.db
MODEL_NAME=meta-llama/Llama-2-7b-chat
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions, please create a GitHub issue.

## Roadmap

- [ ] Multi-language support
- [ ] Sentiment analysis
- [ ] Emotion detection
- [ ] Handoff to human agents
- [ ] Admin dashboard
- [ ] Advanced analytics
- [ ] Webhook integration
