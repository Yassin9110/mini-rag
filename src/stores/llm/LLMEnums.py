from enum import Enum

class LLMEnums(Enum):
    OPENAI = "OPENAI"
    ANTHROPIC = "anthropic"
    COHERE = "COHERE"
    AI21 = "ai21"
    CUSTOM = "custom"
    GEMINI = "GEMINI"

class OpenAIEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class CohereEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    DOCUMENT = "search_document"
    QUERY = "search_query"


class GeminiEnums(Enum):
    USER = "user"
    MODEL = "model"

class DocumentTypeEnum(Enum):
    DOCUMENT = "document"
    QUERY = "query"