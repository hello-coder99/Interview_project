from flask import Blueprint, request, jsonify
import os
from models.session_store import create_session, get_session, update_session
from services.question_selector import get_question_by_id
from services.adaptive_engine import evaluate_and_select
from services.redis_queue import enqueue_audio, get_transcription

UPLOAD_DIR = "/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

interview_bp = Blueprint("interview", __name__)

@interview_bp.route("/start", methods=["POST"])
def start_interview():
    session_id = create_session()
    first_question = get_question_by_id(1)

    update_session(session_id, first_question["id"], None, None)

    return jsonify({
        "session_id": session_id,
        "question": first_question
    })


@interview_bp.route("/answer/audio", methods=["POST"])
def submit_audio_answer():
    session_id = request.form["session_id"]
    audio = request.files["audio"]

    filename = f"{session_id}.wav"
    file_path = os.path.join(UPLOAD_DIR, filename)
    audio.save(file_path)

    job_id = enqueue_audio(file_path)

    return jsonify({
        "message": "Audio received",
        "job_id": job_id
    })


@interview_bp.route("/answer/text", methods=["POST"])
def submit_text_answer():
    data = request.json
    session_id = data["session_id"]
    job_id = data["job_id"]

    transcription = get_transcription(job_id)

    if not transcription:
        return jsonify({"status": "PROCESSING"}), 202

    session = get_session(session_id)
    current_q = get_question_by_id(session["current_question_id"])

    score, next_q = evaluate_and_select(transcription, current_q)

    update_session(session_id, next_q["id"], transcription, score)

    return jsonify({
        "transcription": transcription,
        "score": score,
        "next_question": next_q
    })

