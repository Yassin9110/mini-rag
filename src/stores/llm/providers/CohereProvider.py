from stores.llm.LLMInterface import LLMInterface
from stores.llm.LLMEnums import LLMEnums, CohereEnums, DocumentTypeEnum
import cohere
import logging

class CohereProvider(LLMInterface):
    def __init__(self, api_key: str,
                  default_max_input_tokens: int = 1000, default_max_output_tokens: int = 1000, temperature: float = 0.7):
        
        self.api_key = api_key
        
        self.default_max_input_tokens = default_max_input_tokens
        self.default_max_output_tokens = default_max_output_tokens
        self.temperature = temperature
        self.embedding_model = None
        self.embedding_dim= None
        self.generation_model = None

        self.client = cohere.ClientV2(self.api_key)

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
            self.logger.error("Cohere client not initialized.")
            return None
        
        input_type = CohereEnums.DOCUMENT.value
        if doc_type == DocumentTypeEnum.QUERY.value:
            input_type = CohereEnums.QUERY.value
        
        response = self.client.embed(model= self.embedding_model, input_type= input_type, texts=[self.process_text(text)])

        if not response or not response.embeddings:
            self.logger.error("Invalid response from embedding API.")
            return None
        
        return response.embeddings.float_[0]
    
    def process_text(self, text: str):
        return text[:self.default_max_input_tokens].strip()

    def generate_text(self, prompt: str, **kwargs):
        if not self.generation_model:
            self.logger.error("Generation model not set.")
            return None
        if not self.client:
            self.logger.error("Cohere client not initialized.")
            return None
        
        chat_history = kwargs.get('chat_history', [])

        chat_history.append(self.construct_prompt(prompt, CohereEnums.USER.value))

        
        response = self.client.chat(
            model = self.generation_model,
            messages = chat_history,
            max_tokens = kwargs.get('max_output_tokens', self.default_max_output_tokens),
            temperature = kwargs.get('temperature', self.temperature)
        )

        if not response:
            self.logger.error("Invalid response from generation API.")
            return None
        
        return response.message.content[0].text
        

    def construct_prompt(self, prompt: str, role: str):
        return {"role": role, "content": self.process_text(prompt)}
