from core.services.ai_service import generate_system_instruction, iter_tutor_response, load_google_api_keys

api_keys = load_google_api_keys()


def load_api_keys():
    return load_google_api_keys()


def get_response_stream(user_message, user_data=None, conversation_history=None):
    return iter_tutor_response(user_message, user_data, conversation_history)
