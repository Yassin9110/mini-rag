from stores.llm.LLMInterface import LLMInterface
from stores.llm.LLMEnums import LLMEnums, OpenAIEnums
from openai import OpenAI
import logging

class OpenAIProvider(LLMInterface):
    def __init__(self, api_key: str, api_url: str = None,
                  default_max_input_tokens: int = 1000, default_max_output_tokens: int = 1000, temperature: float = 0.7):
        
        self.api_key = api_key
        self.api_url = api_url
        self.default_max_input_tokens = default_max_input_tokens
        self.default_max_output_tokens = default_max_output_tokens
        self.temperature = temperature
        self.embedding_model = None
        self.embedding_dim= None
        self.generation_model = None

        self.client = OpenAI(api_key=self.api_key, base_url=self.api_url)
        self.enums = OpenAIEnums
        self.logger = logging.getLogger(__name__)

    
    def set_generation_model(self, model_id):
        self.generation_model = model_id

    def set_embedding_model(self, model_id, embed_dim: int):
        self.embedding_model = model_id
        self.embedding_dim = embed_dim

    def embed_text(self, text:str, doc_type:str = None):
        if not self.embedding_model:
            self.logger.error("Embedding model not set.")
            return None
        if not self.client:
            self.logger.error("OpenAI client not initialized.")
            return None
        
        response = self.client.embeddings.create(
            model = self.embedding_model,
            input = text
        )

        if not response or response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Invalid response from embedding API.")
            return None
        
        return response.data[0].embedding
    
    def process_text(self, text: str):
        return text[:self.default_max_input_tokens].strip()

    def generate_text(self, prompt: str, **kwargs):
        if not self.generation_model:
            self.logger.error("Generation model not set.")
            return None
        if not self.client:
            self.logger.error("OpenAI client not initialized.")
            return None
        
        max_output_tokens = kwargs.get('max_output_tokens', self.default_max_output_tokens)
        temperature = kwargs.get('temperature', self.temperature)
        chat_history = kwargs.get('chat_history', [])

        chat_history.append(self.construct_prompt(prompt, OpenAIEnums.USER.value))

        response = self.client.chat.completions.create(
            model = self.generation_model,
            messages = chat_history,
            max_tokens = max_output_tokens,
            temperature = temperature
        )

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("Invalid response from generation API.")
            return None
        
        return response.choices[0].message["content"]
        

    def construct_prompt(self, prompt: str, role: str):
        return {"role": role, "content": self.process_text(prompt)}
