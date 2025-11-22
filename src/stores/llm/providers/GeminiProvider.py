from stores.llm.LLMInterface import LLMInterface
from stores.llm.LLMEnums import LLMEnums, GeminiEnums
from google import genai
from google.genai import types
from typing import List, Union
import logging

class GeminiProvider(LLMInterface):
    def __init__(self, api_key: str,
                  default_max_input_tokens: int = 1000, default_max_output_tokens: int = 1000, temperature: float = 0.7):
        
        self.api_key = api_key
        self.default_max_input_tokens = default_max_input_tokens
        self.default_max_output_tokens = default_max_output_tokens
        self.temperature = temperature
        self.embedding_model = None
        self.embedding_dim= None
        self.generation_model = None

        self.client = genai.Client(api_key=self.api_key)

        self.logger = logging.getLogger(__name__)

    
    def set_generation_model(self, model_id):
        self.generation_model = model_id

    def set_embedding_model(self, model_id, embed_dim: int):
        self.embedding_model = model_id
        self.embedding_dim = embed_dim

    def embed_text(self, text: Union[str, List[str]], doc_type: str = None) -> Union[List[float], List[List[float]], None]:
    
        if not self.embedding_model:
            self.logger.error("Embedding model not set.")
            return None
        if not self.client:
            self.logger.error("Gemini client not initialized.")
            return None

        # 1. Prepare contents for the API
        is_single_query = isinstance(text, str)
        
        # The API always expects a list for 'contents'
        if is_single_query:
            contents_to_embed = [text]
        else:
            # 'text' is already a List[str]
            contents_to_embed = text
            
        # 2. Call the embedding API
        try:
            response = self.client.models.embed_content(
                model=self.embedding_model, 
                contents=contents_to_embed,
                config=types.EmbedContentConfig(output_dimensionality=self.embedding_dim)
            )
        except Exception as e:
            self.logger.error(f"Error calling embedding API: {e}")
            return None

        if not response or not response.embeddings:
            self.logger.error("Invalid response from embedding API.")
            return None
        
        # 3. Process and return the results
        # Extract the numeric vectors from the response objects
        all_embeddings = [embedding.values for embedding in response.embeddings]

        # If the input was a single string, return just the single vector (List[float])
        if is_single_query:
            # We know all_embeddings contains exactly one list, so we return the first element
            return all_embeddings[0]
        else:
            # If the input was a list of strings, return the list of vectors (List[List[float]])
            return all_embeddings
    
    def process_text(self, text: str):
        return text[:self.default_max_input_tokens].strip()

    def generate_text(self, prompt: str, **kwargs):
        """
        Generates text using the Gemini model, incorporating chat history.
        
        Args:
            prompt: The new message from the user.
            kwargs: Optional parameters including 'chat_history', 'max_output_tokens', etc.
            
        Returns:
            The generated text string or None on error.
        """
        if not self.generation_model:
            self.logger.error("Generation model not set.")
            return None
        if not self.client:
            self.logger.error("Gemini client not initialized.")
            return None
        
        # 1. Retrieve generation parameters
        max_output_tokens = kwargs.get('max_output_tokens', self.default_max_output_tokens)
        temperature = kwargs.get('temperature', self.temperature)
        chat_history = kwargs.get('chat_history', [])

        # 2. Convert history and new prompt into the API-required 'contents' list
        # This is where your construct_prompt function is crucial.
        try:
            full_contents = self.construct_prompt(chat_history=chat_history, prompt=prompt)
        except Exception as e:
            self.logger.error(f"Error constructing prompt contents: {e}")
            return None

        # 3. Define generation configuration
        config = types.GenerateContentConfig(
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )

        # 4. Call the Gemini API
        try:
            response = self.client.models.generate_content(
                model=self.generation_model,
                contents=full_contents,
                config=config
            )
            
            # 5. Return the text response
            return response.text
            
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during generation: {e}")
            return None        

    def construct_prompt(self, chat_history: list, prompt: str) -> list[types.Content]:
        """
        Converts custom history format and the new prompt into the Gemini API 'contents' format.
        
        Args:
            chat_history: A list of dictionaries [{'role': 'user'|'model', 'text': '...'}].
            prompt: The new user message to append.
            
        Returns:
            A list of types.Content objects ready for the API call.
        """
        
        # 1. Convert historical messages
        gemini_contents = []
        for message in chat_history:
            # Ensure roles are strictly 'user' or 'model' and the 'text' key exists
            role = message.get('role')
            text = message.get('text')
            
            if role and text:
                gemini_contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text)]
                    )
                )

        # 2. Append the new user prompt as the final Content object
        gemini_contents.append(
            types.Content(
                role=GeminiEnums.USER.value,
                parts=[types.Part.from_text(self.process_text(prompt))]
            )
        )
        
        return gemini_contents
        
