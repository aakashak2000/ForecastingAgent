import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_llm_manager():

    try:
        from app.llm_manager import LLMProviderManager

        manager = LLMProviderManager()
        llm = manager.get_llm()
        info = manager.get_provider_info()
        print(f"LLM Info: {info}")
        response = llm.invoke(f"Tell me something about Tata Consultance Services")
        print(f"Response: {response}")
        return True
    
    except Exception as e:
        print(f"LLM Manager failed to load model {str(e)}")
        return False
    
test_llm_manager()


