import os
import logging
from langchain_core.language_models.base import BaseLanguageModel
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_huggingface import HuggingFaceEndpoint

logger = logging.getLogger(__name__)

class LLMProviderManager:
    """
    Manages multiple LLM providers with automatic fallback.
    Tries providers in terms of a priority order until one works for robustness.
    """

    def __init__(self):
        self.current_provider = None
        self.current_llm = None


    def get_available_llm(self):
        """
        Tries to connect to the first llm instance based on the priority order
        """
        providers = [
            ("ollama", self._try_ollama),
            ("openai", self._try_openai),
            ("anthropic", self._try_anthropic),
            ("huggingface", self._try_huggingface),
        ]

        for provider_name, provider_func in providers:
            try:
                llm = provider_func()
                self.current_provider = provider_name
                self.current_llm = llm
                logger.info(f"Successfully initialized {provider_name}")
                return llm
            except Exception as e:
                logger.warning(f"Failed to Initialize {provider_name}: {str(e)}")

        raise Exception("No LLM Providers available - check dependencies and environment.")
        

    def _try_ollama(self):
        """
        Tries to connect to local Ollama instance.
        """
        model = "llama3.1:8b"
        try:
            llm = OllamaLLM(model=model, temperature=0.1)
            test_response = llm.invoke("Hello")
            if test_response:
                logger.info(f"Ollama {model} initialised and tested.")
                return llm
        except Exception as e:
            logger.debug(f"Model {model} failed: {str(e)}")


    def _try_openai(self):
        """
        Tries to connect to OpenAI with OpenAI key if available.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key: 
            raise Exception("OPENAI_API_KEY not found in environment.")
        models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        for model in models:
            try:
                llm = ChatOpenAI(
                    model=model,
                    temperature=0.1,
                    api_key=api_key
                )
                test_response = llm.invoke("Hello")
                if test_response:
                    logger.info(f"OpenAI {model} initialised and tested.")
                    return llm
            except Exception as e:
                logger.debug(f"Model {model} failed: {str(e)}")

        raise Exception("No OpenAI models accessible")
    
    def _try_anthropic(self):
        """
        Tries connecting to Anthropic Claude with key, if available
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise Exception("ANTHROPIC_API_KEY not found in environment.")
        
        models = ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]

        for model in models:
            try:
                llm = ChatAnthropic(model=model,
                                    temperature=0.1,
                                    api_key=api_key,
                                    timeout=30,
                                    max_tokens=4096)
                test_response = llm.invoke("Hello")
                if test_response:
                    logger.info(f"Model {model} initalised and tested.")
                    return llm
            except Exception as e:
                logger.debug(f"Model {model} failed: {str(e)}")

        raise Exception(f"No Anthropic models accessible.")
    

    def _try_huggingface(self):
        """
        Attempts touse HuggingGave Inference API
        Free Option
        """
        hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        models = [
            "microsoft/DialoGPT-large",
            "google/flan-t5-large",
            "mistralai/Mistral-7B-Instruct-v0.1"
        ]

        for model in models:
            try:
                kwargs = {
                    "repo_id": model,
                    "temperature": 0.1,
                    "max_length": 1024,
                    "timeout": 60
                }
                if hf_token:
                    kwargs["huggingfacehub_api_token"] = hf_token
                llm = HuggingFaceEndpoint(**kwargs)

                test_response = llm.invoke("Hello")
                if test_response:
                    logger.info(f"HF Model {model} Initialized and Tested.")
                    return llm
                
            except Exception as e:
                logger.debug(f"HF model {model} failed: {str(e)}")
                
        raise Exception("No HuggingFace models available.")

    def get_llm(self):
        """
        Return current llm instance or initializes one.
        """
        if self.current_llm is None:
            self.get_available_llm()

        return self.current_llm
    
    def get_provider_info(self):
        """
        Returns info about current provider for logging/debugging.
        """

        return {
            "provider": self.current_provider,
            "available": self.current_llm is not None
        }
    
    