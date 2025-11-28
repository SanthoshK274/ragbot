from flask import Flask, request, jsonify
from flask_cors import CORS

import os
import sys
import pathlib
import time
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))
import tempfile
from rag.doc_utils import extract_text_from_pdf, chunk_text
from rag.vector_db import VectorDB
from rag.groq_llm import GroqLLM
from dotenv import load_dotenv
from flask import session
from auth import register_user, login_user, verify_otp
from dotenv import load_dotenv
import tempfile

load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecret')
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)


vector_db = None
llm = GroqLLM()
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    success, msg = register_user(email, password)
    # Do NOT set session here; require 2FA verification first
    return jsonify({'success': success, 'message': msg}), (200 if success else 400)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    # Only allow login if user is verified
    from db import SessionLocal
    from models import User
    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    if not user:
        db.close()
        return jsonify({'success': False, 'message': 'User not found.'}), 401
    if not user.is_verified:
        db.close()
        return jsonify({'success': False, 'message': 'Account not verified. Please complete 2FA after signup.'}), 401
    db.close()
    # Now check password and send OTP
    success, msg = login_user(email, password)
    # Do NOT set session here; require OTP verification first
    return jsonify({'success': success, 'message': msg}), (200 if success else 401)

@app.route('/verify-2fa', methods=['POST'])
def verify_2fa():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    # Check if this is a signup or login verification
    from db import SessionLocal
    from models import User
    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    db.close()
    success, msg = verify_otp(email, otp)
    if success:
        # Only set session after successful OTP verification
        session['email'] = email
        session['verified'] = True
    return jsonify({'success': success, 'message': msg}), (200 if success else 401)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out.'})

@app.route('/upload', methods=['POST'])
def upload():
    global vector_db
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        file.save(tmp.name)
        temp_path = tmp.name
    # Now the file is closed, safe to process
    text = extract_text_from_pdf(temp_path)
    chunks = chunk_text(text)
    embeddings = [llm.get_embedding(chunk) for chunk in chunks]
    vector_db = VectorDB(dim=len(embeddings[0]))
    vector_db.add(embeddings, chunks)
    os.remove(temp_path)
    return jsonify({'message': f'Uploaded and indexed {len(chunks)} chunks.'})

@app.route('/ask', methods=['POST'])


def ask():
    global vector_db
    data = request.get_json()
    question = data.get('question', '')
    if not vector_db:
        return jsonify({'error': 'No document uploaded yet.'}), 400
    t0 = time.time()
    try:
        q_emb = llm.get_embedding(question)
    except Exception as e:
        print(f"[ERROR] Embedding: {e}")
        return jsonify({'error': f'Embedding error: {e}'}), 500
    t1 = time.time()
    results = vector_db.search(q_emb, top_k=2)  # Limit to top 2 chunks
    t2 = time.time()
    context = "\n".join([r[0] for r in results])[:2000]  # Limit context to 2000 chars
    try:
        answer = llm.generate_answer(context, question)
    except Exception as e:
        print(f"[ERROR] LLM answer: {e}")
        return jsonify({'error': f'LLM answer error: {e}'}), 500
    t3 = time.time()
    print(f"[TIMING] Embedding: {t1-t0:.2f}s, Vector search: {t2-t1:.2f}s, LLM answer: {t3-t2:.2f}s, Total: {t3-t0:.2f}s")
    return jsonify({
        'answer': answer,
        'context': [r[0] for r in results],
        'scores': [float(r[1]) for r in results]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
