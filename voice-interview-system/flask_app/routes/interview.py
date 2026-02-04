from flask import Blueprint, request, jsonify
from models.session_store import create_session, get_session, update_session
from services.question_selector import get_question_by_id
from services.adaptive_engine import evaluate_and_select

interview_bp = Blueprint("interview", __name__)

@interview_bp.route("/start", methods=["POST"])
def start_interview():
    session_id = create_session()

    first_question = get_question_by_id(1)

    # initialize session state
    update_session(
        session_id=session_id,
        current_question_id=first_question["id"],
        answer=None,
        score=None
    )

    return jsonify({
        "session_id": session_id,
        "question": first_question
    })


@interview_bp.route("/answer", methods=["POST"])
def submit_answer():
    data = request.json
    session_id = data["session_id"]
    answer = data["answer"]

    session = get_session(session_id)

    if not session:
        return jsonify({"error": "Invalid session"}), 400

    current_question = get_question_by_id(session["current_question_id"])

    score, next_question = evaluate_and_select(answer, current_question)

    update_session(
        session_id=session_id,
        current_question_id=next_question["id"],
        answer=answer,
        score=score
    )

    return jsonify({
        "score": score,
        "next_question": next_question
    })

