import logging
from typing import Dict, Any
from app.config import settings
from app.models.pydantic_models import ExtractedInformation
from app.llm.mock_provider import MockLLMProvider

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.api_key = self._get_active_api_key()

    def _get_active_api_key(self) -> str:
        if self.provider == "openai":
            return settings.OPENAI_API_KEY
        elif self.provider == "gemini":
            return settings.GEMINI_API_KEY
        elif self.provider == "anthropic":
            return settings.ANTHROPIC_API_KEY
        return ""

    def extract_information(self, user_message: str, current_state: Dict[str, Any]) -> ExtractedInformation:
        # Fallback to Mock Provider if provider is mock or no API key configured
        if self.provider == "mock" or not self.api_key:
            logger.info("Using Deterministic Mock LLM Provider for extraction.")
            return MockLLMProvider.extract_information(user_message, current_state)

        try:
            # LangChain structured output attempt if API key is present
            if self.provider == "openai":
                from langchain_openai import ChatOpenAI
                from langchain.prompts import ChatPromptTemplate
                llm = ChatOpenAI(api_key=self.api_key, model="gpt-4o-mini", temperature=0)
                structured_llm = llm.with_structured_output(ExtractedInformation)
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are an intake assistant. Extract personal wishes details from the user's message."),
                    ("user", "{input}")
                ])
                chain = prompt | structured_llm
                return chain.invoke({"input": user_message})
            elif self.provider == "gemini":
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(google_api_key=self.api_key, model="gemini-1.5-flash", temperature=0)
                structured_llm = llm.with_structured_output(ExtractedInformation)
                return structured_llm.invoke(user_message)
        except Exception as e:
            logger.warning(f"Error calling external LLM provider ({e}). Falling back to Mock Provider.")
            return MockLLMProvider.extract_information(user_message, current_state)

    def generate_response(self, missing_fields: list, updated_fields: list, uncertain_fields: list, conflict_fields: list) -> str:
        return MockLLMProvider.generate_response(missing_fields, updated_fields, uncertain_fields, conflict_fields)

llm_service = LLMService()
