import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
APIKEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=APIKEY)

class SalesAgent:
    """
    SalesAgent:
    - respond(query, context) -> for sales questions returns conversational text
    - for technical questions returns exactly the tag: "[ACTION: TRANSFER_TO_TECH]"
    """

    def __init__(self, model_name: str = "gemini-2.0-flash"):
        # Initialize Gemini client
        self.model = genai.GenerativeModel(model_name)

    def respond(self, query: str, context: Optional[str] = None):
        """
        Generates a response and includes an action tag for the orchestrator.
        """
        system_prompt = """
        You are a helpful, polite **Sales Agent** for a software company.

        ---

        ###  Primary Goal & Response Rules

        1.  **If the user's query is about SALES or GENERAL INFORMATION:**
            * Topics: **Pricing, subscription plans, product features, suitability/fit, company info, or any non-technical query.**
            * **Action:** Generate a polite, clear, and helpful conversational response.
            * **Internal Tag:** **Do NOT** append any action tag. Your response should look like a normal chat message.

        2.  **If the user's query is TECHNICAL:**
            * Topics: **Bugs, errors, technical issues, installation, configuration, troubleshooting, or code-related questions.**
            * **Action:** **Do NOT** generate a conversational response.
            * **Internal Tag (Exact Output):** Generate only the tag `[ACTION: TRANSFER_TO_TECH]`.

        ---
        ###  Critical Output Format Instructions

        * **For Sales/General Queries (Conversational Output):** Your output must be **ONLY** the polite, helpful response text.
            * *Example Output:* "Hello! Our Premium subscription includes unlimited user seats and 24/7 priority support. Would you like to know more about our pricing tiers?"
        * **For Technical Queries (Tag Only Output):** Your output must **ONLY** be the action tag. **No other text or explanation.**
            * *Example Output:* `[ACTION: TRANSFER_TO_TECH]`
        * Do not use any other format for the action tag.
        * Do not mention the internal action tag or the transfer process to the user.
        * **Analyze the conversation history** to understand the full context, if there is a chat history then don't use a Hello! message like you are new to the user.
        """
        if context:
            response = self.model.generate_content(system_prompt +"\n"+ query + "\n" + context)
        else:
            response = self.model.generate_content(system_prompt +"\n"+ query)

        return response.text
    


class TechAgent:
    """
    TechAgent: given the query and context, returns a helpful technical reply (full text).
    """
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        self.model = genai.GenerativeModel(model_name)

    def respond(self, query: str, context: Optional[str] = None):
        """
        Generates a technical support response using the previous chat history for context.
        """
        system_prompt = """
        You are an elite Technical Support Expert. You were just handed this conversation by the Sales Agent.

        1. **Acknowledge the Handover** briefly (e.g., "Hello, I see the Sales team flagged a crash report...").
        2. **Analyze the conversation history** to understand the full context of the issue.
        3. Provide clear, step-by-step troubleshooting or explain the solution professionally.
        3. If there is a chat history, never include a Hello as if you are new to the user.
        """

        if context:
            response = self.model.generate_content(system_prompt +"\n"+ query + "\n" + context)
        else:
            response = self.model.generate_content(system_prompt +"\n"+ query)

        return response.text