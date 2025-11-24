from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_ollama.llms import OllamaLLM
from app.config.env import (GROQ_API_KEY, OPENAI_API_KEY)


class LLM:
    def __init__(self):
        self.llm = None
        self.platform = None

    def groq(self, model: str):
        self.llm = ChatGroq(groq_api_key=GROQ_API_KEY, model=model)
        self.platform = "Groq"
        return self.llm

    def openai(self, model: str):
        self.llm = ChatOpenAI(api_key=OPENAI_API_KEY, model=model)
        self.platform = "OpenAi"
        return self.llm

    def ollama(self, model: str):
        self.llm = OllamaLLM(model=model)
        self.platform = "Ollama"
        return self.llm

    def get_llm(self):
        return self.llm

    def invoke(self, prompt: str):
        return self.llm.invoke(prompt)