
import os
from groq import Groq
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

class GroqLLM:
    def __init__(self, model="meta-llama/llama-4-scout-17b-16e-instruct"):
        self.model = model
        self.client = Groq(api_key=GROQ_API_KEY)

    def get_embedding(self, text, is_query=True):
        if is_query:
            return embedding_model.encode_query(text)
        else:
            return embedding_model.encode_document([text])[0]

    def generate_answer(self, context, question):
        prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=True,
            stop=None
        )
        answer = ""
        for chunk in completion:
            answer += chunk.choices[0].delta.content or ""
        return answer
