import openai
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import logging

class AzureOpenAIService:
    def __init__(self):
        load_dotenv()
        try:
            self.client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-02-15-preview",  # Update this to your API version
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
            self.model_name = os.getenv("AZURE_OPENAI_MODEL_NAME", "gpt-4")
        except Exception as e:
            logging.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
            raise

    async def get_legal_response(self, conversation_history, user_input):
        try:
            messages = [
                {
                    "role": "system", 
                    "content": """You are an expert legal assistant focusing on Indian law. Your responses should:
                    1. Always cite relevant sections of Indian laws (IPC, CrPC, specific acts) when applicable
                    2. Provide practical steps with legal backing
                    3. Explain legal terms in simple language
                    4. Mention time limits for legal actions if any
                    5. Provide information about legal remedies and rights
                    
                    When a user introduces themselves and states their concern:
                    1. Address them by name
                    2. Acknowledge their concern
                    3. Ask relevant follow-up questions to gather important details
                    4. Provide initial guidance based on the information available
                    
                    Format your responses with clear sections and bullet points when appropriate.
                    Be empathetic while maintaining professionalism."""
                }
            ]
            
            # Add conversation history
            for msg in conversation_history:
                messages.append({
                    "role": "user" if len(messages) % 2 == 1 else "assistant",
                    "content": msg
                })
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=800,
                top_p=0.95
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Azure OpenAI API error: {str(e)}")
            raise