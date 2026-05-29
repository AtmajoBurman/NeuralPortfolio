import asyncio
from app.chatbot.code import get_chatbot_response

async def test_chat():
    print("Sending message to Chatbot (Riku)...")
    message = "tell me something about the projects of atmajo burman"
    print(f"User: {message}")
    
    # Simulating the endpoint behavior
    response = await asyncio.to_thread(get_chatbot_response, message)
    print(f"Riku: {response}")

if __name__ == "__main__":
    asyncio.run(test_chat())
