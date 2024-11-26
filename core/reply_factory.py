
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST
import consumers


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''

    # Validate the user's response
    if current_question_id is None or answer is None:
        return False, "No current question."

    consumers.ChatConsumer.add_to_history({
        'type':'chat_message',
        'is_user':True,
        'question_id':current_question_id,
        'text':answer
    })

    return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    if current_question_id is None:
        return PYTHON_QUESTION_LIST[0], 0
    next_question_id = current_question_id + 1
    if next_question_id < len(PYTHON_QUESTION_LIST):
        return PYTHON_QUESTION_LIST[next_question_id], next_question_id
    else:
        return None, None

def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    answers_from_user = session.get("message_history", [])
    score = 0

    for user_answer in answers_from_user:
        correct_answer = PYTHON_QUESTION_LIST[user_answer.get("question_id","")]
        if user_answer.get("answer","") == correct_answer:
            score += 1

    result_message = f"Your final score is {score} out of {len(PYTHON_QUESTION_LIST)}"
    return result_message
