from data.questions import QUESTIONS

def get_question_by_id(qid):
    for q in QUESTIONS:
        if q["id"] == qid:
            return q
    return None

def get_next_question(current_qid):
    for q in QUESTIONS:
        if q["id"] > current_qid:
            return q
    return None

