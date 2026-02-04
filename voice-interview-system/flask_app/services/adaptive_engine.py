from services.question_selector import get_next_question

def evaluate_answer(answer, keywords):
    score = 0
    answer_lower = answer.lower()

    for kw in keywords:
        if kw.lower() in answer_lower:
            score += 1

    if score >= 2:
        return "HIGH"
    elif score == 1:
        return "MEDIUM"
    return "LOW"

def evaluate_and_select(answer, current_question):
    score = evaluate_answer(answer, current_question["keywords"])

    next_question = get_next_question(current_question["id"])

    if not next_question:
        return score, {
            "id": None,
            "question": "Interview finished"
        }

    return score, next_question

