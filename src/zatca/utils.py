

def extract_error_message_from_response(response: dict | None) -> str | None:
    try:
        errors_list: list = response.get("errors")
        error: dict = errors_list[0]
        message: str = error.get("message")
        return message
    except Exception as e:
        return None