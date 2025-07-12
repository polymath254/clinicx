from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler that adds HTTP status code to the response.
    """
    response = exception_handler(exc, context)
    if response is not None:
        # Include status_code in payload for client use
        response.data['status_code'] = response.status_code
    return response
