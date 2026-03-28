print("AI Chatbot: Hello! I am your chatbot. Type 'bye' to exit.")

while True:
    user_input = input("You: ").lower()

    if user_input == "hello" or user_input == "hi":
        print("Bot: Hello! How can I help you?")
    
    elif "your name" in user_input:
        print("Bot: I am a Python AI Chatbot.")
    
    elif "how are you" in user_input:
        print("Bot: I am fine. Thanks for asking!")
    
    elif "course" in user_input:
        print("Bot: You are studying AIML. Great choice!")
    
    elif "python" in user_input:
        print("Bot: Python is great for AI and Machine Learning.")
    
    elif user_input == "bye":
        print("Bot: Goodbye! Have a nice day.")
        break
    
    else:
        print("Bot: Sorry, I didn't understand that.")