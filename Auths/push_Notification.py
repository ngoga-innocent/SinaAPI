# notifications/utils.py
import requests

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

def send_push_notification(expo_push_token, title, message, data=None):
    """
    Send push notification via Expo.
    """
    if not expo_push_token:
        return False  # No token, can't send

    payload = {
        "to": expo_push_token,
        "sound": "default",
        "title": title,
        "body": message,
        "data": data or {},
    }

    response = requests.post(EXPO_PUSH_URL, json=payload)
    return response.json()
