from abc import ABC, abstractmethod

class LLMInterface(ABC):

    @abstractmethod
    def set_generation_model(self, model_id: str):
        """Set the generation model by its identifier.

        Args:
            model_id (str): The identifier of the model to set.
        """
        pass

    @abstractmethod
    def set_embedding_model(self, model_id: str, embed_dim: int):
        """Set the embedding model by its identifier.

        Args:
            model_id (str): The identifier of the model to set.
        """
        pass

    @abstractmethod
    def embed_text(self, text:str, doc_type:str):

        pass

    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text based on the given prompt.

        Args:
            prompt (str): The input prompt for text generation.
            **kwargs: Additional parameters for text generation.

        Returns:
            str: The generated text.
        """
        pass

    @abstractmethod
    def construct_prompt(self, prompt: str, role: str):
        
        pass