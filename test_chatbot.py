import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from backend.app.chatbot.code import get_chatbot_response

if __name__ == "__main__":
    print(get_chatbot_response("Any achievements in Machine Learning?"))
