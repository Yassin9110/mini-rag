from .LLMEnums import *
from .providers import OpenAIProvider, CohereProvider, GeminiProvider

class LLMProviderFactory:

    def __init__(self, config: dict):

        self.config = config

    def create_provider(self, provider: str):
        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                api_key= self.config.OPENAI_API_KEY,
                api_url= self.config.OPENAI_API_URL,
                default_max_input_tokens= self.config.MAX_INPUT_TOKENS,
                default_max_output_tokens= self.config.MAX_OUTPUT_TOKENS,
                default_temperature= self.config.TEMPERATURE
                )
        elif provider == LLMEnums.COHERE.value:
            return CohereProvider(
                api_key= self.config.COHERE_API_KEY,
                default_max_input_tokens= self.config.MAX_INPUT_TOKENS,
                default_max_output_tokens= self.config.MAX_OUTPUT_TOKENS,
                temperature= self.config.TEMPERATURE
            )
        elif provider == LLMEnums.GEMINI.value:
            return GeminiProvider(
                api_key= self.config.GEMINI_API_KEY,
                default_max_input_tokens= self.config.MAX_INPUT_TOKENS,
                default_max_output_tokens= self.config.MAX_OUTPUT_TOKENS,
                temperature= self.config.TEMPERATURE
            )
        return None

