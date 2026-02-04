import uuid

# In-memory session store (Redis later)
SESSIONS = {}

def create_session():
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "current_question_id": None,
        "history": []
    }
    return session_id

def get_session(session_id):
    return SESSIONS.get(session_id)

def update_session(session_id, current_question_id, answer, score):
    session = SESSIONS.get(session_id)

    if not session:
        return

    if answer is not None:
        session["history"].append({
            "question_id": session["current_question_id"],
            "answer": answer,
            "score": score
        })

    session["current_question_id"] = current_question_id

