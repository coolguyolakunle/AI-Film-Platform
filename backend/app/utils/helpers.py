def error_response(message: str, status_code: int = 400, error_code: str = None):
    """Standard error response shape used across all routes."""
    body = {"error": error_code or "bad_request", "message": message}
    return body, status_code


def success_response(data, status_code: int = 200):
    return data, status_code
