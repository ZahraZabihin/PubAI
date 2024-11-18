# extractor_utils.py

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI 
from langchain.schema import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

class OpenAIExtractor:
    def __init__(self):
        """Initialize the extractor with OpenAI API key from environment."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found in environment. Please set 'OPENAI_API_KEY'.")

    def query_openai_with_custom_prompt(self, text, custom_prompt):
        """Queries OpenAI API with a custom prompt using Langchain's ChatOpenAI.
        Automatically appends the chunk text at the end of the prompt.
        """
        # Initialize the model with GPT-4
        model = ChatOpenAI(
            model_name="gpt-4o",
            openai_api_key=self.api_key
        )
        
        # Automatically append {text} after the prompt
        formatted_prompt = f"{custom_prompt} {text}"
        
        # Correct message formatting using Langchain's message objects
        messages = [
            SystemMessage(content="You are a research assistant."),
            HumanMessage(content=formatted_prompt)
        ]
        
        # Get the response using the invoke method
        response = model.invoke(messages)
        
        # Return the response's content after trimming any excess spaces
        return response.content.strip()
