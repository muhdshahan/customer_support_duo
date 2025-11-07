# Customer Support Duo - Backend Documentation

## 📋 Overview

A FastAPI-based intelligent customer support system for Jio that uses LangGraph to orchestrate between two specialized AI agents:
- **Sales Agent**: Handles general inquiries, plan information, pricing, and subscriptions
- **Tech Agent**: Manages technical support issues, troubleshooting, and device configuration

The system intelligently routes conversations between agents based on query classification, ensuring customers receive specialized assistance.

---

## 🏗️ Architecture

### System Flow

```
User Query → FastAPI Endpoint → LangGraph Orchestrator
                                        ↓
                                   Sales Agent
                                   /          \
                          Sales Response    Technical Query?
                                 ↓               ↓
                               END          Tech Agent
                                               ↓
                                          Tech Response
                                               ↓
                                              END
```

### Components

1. **FastAPI Application** (`main.py`)
   - Exposes REST API endpoint `/ask`
   - Handles conversation history management
   - Routes requests to LangGraph orchestrator

2. **LangGraph Orchestrator** (`support_graph.py`)
   - Implements state machine for agent routing
   - Manages conversation flow between agents
   - Tracks which agent handled each response

3. **AI Agents** (`agents.py`)
   - **SalesAgent**: Uses Gemini 2.0 Flash for sales/general queries
   - **TechAgent**: Uses Gemini 2.0 Flash for technical support

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8+
- Google Gemini API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install fastapi uvicorn python-dotenv google-generativeai langgraph pydantic
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the `app/agents/` directory:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

---

## 📡 API Endpoints

### POST `/ask`

Handles customer support queries with conversation history context.

#### Request Schema

```json
{
  "history": [
    {
      "role": "user",
      "content": "string",
      "agent": "string (optional)"
    }
  ]
}
```

**Fields:**
- `history` (optional): Array of previous messages in the conversation
  - `role`: Either "user" or "assistant"
  - `content`: The message text
  - `agent`: (optional) Which agent handled the message ("sales_agent" or "tech_agent")

#### Response Schema

```json
{
  "response": "string",
  "agent": "string"
}
```

**Fields:**
- `response`: The agent's reply to the user
- `agent`: Which agent generated the response ("sales_agent" or "tech_agent")

---

## ✅ Success Test Cases

### Test Case 1: Sales Query - Plan Information

**Request:**
```json
POST /ask
Content-Type: application/json

{
  "history": [
    {
      "role": "user",
      "content": "Hi, I want to know about Jio prepaid plans with good data benefits"
    }
  ]
}
```

**Expected Response:**
```json
{
  "response": "Sure! I can help you with that. We have several great prepaid plans:\n\n- ₹239 plan offers 1.5GB/day for 28 days with unlimited calling\n- ₹299 plan gives you 2GB/day for 28 days, plus access to all Jio apps\n- ₹666 plan provides 1.5GB/day for a longer 84-day validity\n\nAll plans include unlimited voice calls and SMS. Which data allowance works best for you?",
  "agent": "sales_agent"
}
```

**Verification:**
- ✅ Response contains plan details
- ✅ Agent is "sales_agent"
- ✅ Response is conversational and helpful
- ✅ Status code: 200

---

### Test Case 2: Technical Query with Agent Transfer

**Request:**
```json
POST /ask
Content-Type: application/json

{
  "history": [
    {
      "role": "user",
      "content": "I'm having issues with my JioFiber connection. The router has a red light blinking"
    }
  ]
}
```

**Expected Response (First from Sales Agent):**
```json
{
  "response": "That sounds like a technical issue. Connecting you to a Tech Expert...",
  "agent": "sales_agent"
}
```

**Then automatically transitions to Tech Agent's response:**
```json
{
  "response": "I can help you with that. A red blinking light on your JioFiber router typically indicates a connection issue. Let's troubleshoot:\n\n1. First, check if all cables are properly connected - especially the fiber optic cable\n2. Power cycle the router: unplug it, wait 30 seconds, then plug it back in\n3. Wait 2-3 minutes for the router to fully restart\n4. The light should turn green once connected\n\nIf the issue persists after trying these steps, there might be a service disruption in your area or a hardware issue. Would you like me to help you check the connection status or report this to our technical team?",
  "agent": "tech_agent"
}
```

**Verification:**
- ✅ System recognizes technical query
- ✅ Agent transitions from "sales_agent" to "tech_agent"
- ✅ Tech agent provides step-by-step troubleshooting
- ✅ Status code: 200

---

## ❌ Failure Test Cases

### Test Case 3: Invalid Request - Missing Required Fields

**Request:**
```json
POST /ask
Content-Type: application/json

{
  "history": [
    {
      "role": "user"
    }
  ]
}
```

**Expected Response:**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "history", 0, "content"],
      "msg": "Field required",
      "input": {"role": "user"}
    }
  ]
}
```

**Verification:**
- ✅ Status code: 422 (Unprocessable Entity)
- ✅ Error message indicates missing "content" field
- ✅ Proper validation error structure

---

### Test Case 4: Empty History Array

**Request:**
```json
POST /ask
Content-Type: application/json

{
  "history": []
}
```

**Expected Response:**
```json
{
  "response": "Hello! I'm here to help you with Jio services. How may I assist you today?",
  "agent": "sales_agent"
}
```

**Alternative Behavior:**
If the system doesn't handle empty context gracefully, you might receive:

```json
{
  "response": "I didn't receive any query. How can I help you today?",
  "agent": "sales_agent"
}
```

**Verification:**
- ✅ Status code: 200 (Request is valid, just empty)
- ✅ Agent provides default greeting or prompts for input
- ✅ System doesn't crash with empty history

---

## 🔧 Agent Behavior

### Sales Agent
- **Triggers on**: Plan inquiries, pricing questions, general information, subscription queries
- **Capabilities**: 
  - Provides information about Jio prepaid, postpaid, JioFiber, and JioAirFiber plans
  - Answers questions about offers and recharges
  - Transfers to Tech Agent when detecting technical issues
- **Transfer Trigger**: Returns `[ACTION: TRANSFER_TO_TECH]` when query is technical

### Tech Agent
- **Triggers on**: Technical problems, connectivity issues, device configuration, app errors
- **Capabilities**:
  - Troubleshoots JioFiber connectivity issues
  - Helps with JioMobile network problems
  - Resolves JioTV/JioCinema streaming issues
  - Guides through Jio app login and setup problems
- **Response Style**: Step-by-step technical guidance with empathetic tone

---

## 🧪 Testing the API

### Using cURL

**Sales Query:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "history": [
      {
        "role": "user",
        "content": "What is the best JioFiber plan for streaming?"
      }
    ]
  }'
```

**Technical Query:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "history": [
      {
        "role": "user",
        "content": "My Jio SIM is not connecting to the network"
      }
    ]
  }'
```

### Using Python Requests

```python
import requests

url = "http://localhost:8000/ask"

# Sales query
response = requests.post(url, json={
    "history": [
        {
            "role": "user",
            "content": "Tell me about Jio postpaid plans"
        }
    ]
})

print(response.json())
```

---

## 📊 State Management

The LangGraph orchestrator maintains the following state:

```python
{
    "context": str,          # Full conversation history as formatted text
    "response": str,         # Generated response from agent
    "next_agent": str,       # Routing decision: "tech_agent", "end"
    "agent": str            # Agent that handled the query: "sales_agent" or "tech_agent"
}
```

---

## 🔐 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key for AI models | Yes |

---

## 🛠️ Tech Stack

- **FastAPI**: Modern web framework for building APIs
- **LangGraph**: State machine for orchestrating AI agent workflows
- **Google Gemini 2.0 Flash**: Large language model for agent responses
- **Pydantic**: Data validation using Python type annotations
- **Python-dotenv**: Environment variable management

---

## 📝 Notes

- The system maintains conversation context across multiple turns
- Agent transfers are transparent to the user through natural language
- All responses are generated in real-time using Google's Gemini API
- The system uses the latest Gemini 2.0 Flash model for optimal performance

---

## 🐛 Troubleshooting

**Issue**: "API Key not found" error
- **Solution**: Ensure `.env` file exists in `app/agents/` directory with valid `GOOGLE_API_KEY`

**Issue**: Agent not transferring properly
- **Solution**: Check that the transfer tag `[ACTION: TRANSFER_TO_TECH]` is correctly detected in `support_graph.py`

**Issue**: Slow response times
- **Solution**: Gemini API calls may take 2-5 seconds. Consider implementing caching or response streaming for production

---

## 📄 License

[Add your license information here]

---

## 👥 Contributors

[Add contributor information here]