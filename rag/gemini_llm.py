import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

class GeminiLLM:
    def __init__(self, model="models/text-embedding-004"):
        self.model = model
        self.generation_model = "gemini-2.0-flash-exp"


    def get_embedding(self, text, timeout=10):
        # Gemini embedding API with timeout
        import threading
        result = {}
        def call():
            try:
                response = genai.embed_content(model=self.model, content=text)
                result['embedding'] = response['embedding']
            except Exception as e:
                result['error'] = str(e)
        t = threading.Thread(target=call)
        t.start()
        t.join(timeout)
        if t.is_alive():
            raise TimeoutError('Gemini embedding API timed out')
        if 'error' in result:
            raise RuntimeError(f"Gemini embedding error: {result['error']}")
        return result['embedding']


    def generate_answer(self, context, question, timeout=20):
        prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
        model = genai.GenerativeModel(self.generation_model)
        import threading
        result = {}
        def call():
            try:
                response = model.generate_content(prompt)
                result['text'] = response.text if hasattr(response, 'text') else str(response)
            except Exception as e:
                result['error'] = str(e)
        t = threading.Thread(target=call)
        t.start()
        t.join(timeout)
        if t.is_alive():
            raise TimeoutError('Gemini LLM answer API timed out')
        if 'error' in result:
            raise RuntimeError(f"Gemini LLM error: {result['error']}")
        return result.get('text', '')
