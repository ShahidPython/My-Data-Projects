import os
import logging
import re
import random
import json
from datetime import datetime
from transformers import pipeline, set_seed
import requests

# Configure environment
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
logging.getLogger("transformers").setLevel(logging.ERROR)

# Enhanced user data storage
user_data = {
    "name": None,
    "interests": [],
    "mood": "neutral",
    "conversation_history": []
}

# Jokes database
JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the scarecrow win an award? He was outstanding in his field!",
    "Why don't skeletons fight each other? They don't have the guts!",
    "What do you call a fake noodle? An impasta!",
    "Why did the math book look so sad? Because it had too many problems!",
    "What do you call a bear with no teeth? A gummy bear!",
    "Why don't eggs tell jokes? They'd crack each other up!",
    "What do you call a sleeping bull? A bulldozer!",
    "Why did the coffee file a police report? It got mugged!",
    "What do you call a fish wearing a crown? King of the sea!"
]

# Fun facts
FUN_FACTS = [
    "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly good to eat!",
    "Octopuses have three hearts and blue blood!",
    "A day on Venus is longer than a year on Venus!",
    "Bananas are berries, but strawberries aren't!",
    "The shortest war in history was between Britain and Zanzibar in 1896. Zanzibar surrendered after 38 minutes!",
    "A group of flamingos is called a 'flamboyance'!",
    "The Eiffel Tower can be 15 cm taller during the summer due to thermal expansion!",
    "There's a species of jellyfish that is biologically immortal!",
    "A single cloud can weigh more than 1 million pounds!",
    "The inventor of the Frisbee was turned into a Frisbee after he died!"
]

# Initialize AI model
try:
    chat_ai = pipeline(
        "text-generation",
        model="microsoft/DialoGPT-medium",
        device=-1,
        max_length=150,
        do_sample=True,
        top_k=50,
        temperature=0.8,
        top_p=0.9
    )
    set_seed(42)
    print("🤖 AI model loaded successfully!")
except Exception as e:
    print(f"AI model failed to load: {e}")
    chat_ai = None

def clean_input(text):
    """Normalize user input"""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text)

def get_sentiment(text):
    """Simple sentiment analysis"""
    positive_words = ['happy', 'good', 'great', 'awesome', 'excellent', 'fantastic', 'amazing', 'wonderful']
    negative_words = ['sad', 'bad', 'terrible', 'awful', 'horrible', 'angry', 'upset']
    
    if any(word in text for word in positive_words):
        return "positive"
    elif any(word in text for word in negative_words):
        return "negative"
    return "neutral"

def get_weather(city="your city"):
    """Get weather information (simulated)"""
    weather_responses = [
        f"The weather in {city} is sunny and pleasant today! ☀️",
        f"It looks like {city} might have some rain later. Don't forget your umbrella! ☔",
        f"The forecast for {city} shows clear skies and mild temperatures!",
        f"Expect some clouds in {city} today, but it should be nice overall! ⛅"
    ]
    return random.choice(weather_responses)

def get_responses(user_input):
    text = clean_input(user_input)
    
    # Store conversation
    user_data["conversation_history"].append({"user": user_input, "timestamp": datetime.now().isoformat()})
    
    # Limit history size
    if len(user_data["conversation_history"]) > 50:
        user_data["conversation_history"] = user_data["conversation_history"][-50:]
    
    # Empty input
    if not text:
        return "Please type something! I'm here to chat with you. 😊"
    
    # Update mood based on sentiment
    user_data["mood"] = get_sentiment(text)
    
    # Name handling
    name_match = re.match(r"(?:my name is|i am|im|call me) (\w+)", text)
    if name_match:
        user_data["name"] = name_match.group(1)
        return f"Nice to meet you, {user_data['name']}! 😊 How can I help you today?"
    
    if re.match(r"(whats|what is) my name", text):
        if user_data.get("name"):
            return f"Your name is {user_data['name']}! Unless you'd like me to call you something else? 😊"
        return "You haven't told me your name yet. What would you like me to call you?"
    
    # Personal questions
    if "how are you" in text:
        responses = [
            "I'm doing great! Thanks for asking! How about you?",
            "I'm wonderful! Ready to help you with anything! 😊",
            "I'm feeling excellent today! What's on your mind?",
            "I'm doing awesome! Hope you're having a great day too!"
        ]
        return random.choice(responses)
    
    # Greetings
    if any(greet in text for greet in ["hi", "hello", "hey", "hola"]):
        greetings = [
            "Hello! 👋 How can I assist you today?",
            "Hi there! 😊 What can I help you with?",
            "Hey! Great to see you! What's up?",
            "Hello! Ready for some interesting conversation?",
            "Hi! I'm here and ready to chat! 🤗"
        ]
        return random.choice(greetings)
    
    # Weather
    if "weather" in text:
        city_match = re.search(r"weather in (\w+)", text)
        city = city_match.group(1) if city_match else "your city"
        return get_weather(city)
    
    # Date/time
    if any(word in text for word in ["date", "day", "today"]):
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')} 📅"
    
    if any(word in text for word in ["time", "clock"]):
        return f"It's currently {datetime.now().strftime('%I:%M %p')} ⏰"
    
    # Jokes
    if "joke" in text:
        return f"😂 {random.choice(JOKES)}"
    
    # Fun facts
    if any(phrase in text for phrase in ["fun fact", "interesting fact", "tell me something"]):
        return f"Did you know? {random.choice(FUN_FACTS)}"
    
    # Goodbyes
    if any(bye in text for bye in ["bye", "exit", "goodbye", "see you"]):
        goodbyes = [
            "Goodbye! 👋 It was great chatting with you!",
            "See you later! 😊 Take care!",
            "Farewell! Hope to talk with you again soon!",
            "Bye! Have a wonderful day! 🌟"
        ]
        return random.choice(goodbyes)
    
    # Thanks
    if "thank" in text:
        return random.choice([
            "You're welcome! 😊",
            "Happy to help! 🌟",
            "Anytime! That's what I'm here for!",
            "You're very welcome! Let me know if you need anything else!"
        ])
    
    # Help
    if "help" in text:
        return "I can help with: answering questions, telling jokes, fun facts, weather info, time/date, and having conversations! Just ask me anything! 💫"
    
    # Feelings/mood
    if any(word in text for word in ["sad", "unhappy", "depressed"]):
        return "I'm sorry you're feeling that way. 😔 Remember that it's okay to not be okay. Would you like to hear a joke to cheer you up? 🌈"
    
    if any(word in text for word in ["happy", "excited", "great"]):
        return "That's wonderful to hear! 😊 I'm glad you're feeling good! Let's make this day even better! 🎉"
    
    # AI fallback with context awareness
    if chat_ai:
        try:
            # Create context-aware prompt
            context = f"User: {user_input}\nAssistant:"
            
            response = chat_ai(
                context,
                max_length=100,
                num_return_sequences=1,
                pad_token_id=50256
            )[0]['generated_text']
            
            # Extract only the assistant's response
            assistant_response = response.split("Assistant:")[-1].strip()
            
            # Clean up the response
            assistant_response = re.split(r'[.!?]', assistant_response)[0] + '.'
            assistant_response = assistant_response.replace("User:", "").strip()
            
            if len(assistant_response) > 5:  # Ensure meaningful response
                return assistant_response
                
        except Exception as e:
            logging.error(f"AI error: {e}")
    
    # Default creative responses
    creative_responses = [
        "That's an interesting thought! Could you tell me more about that? 🤔",
        "I'd love to hear more about what you're thinking! 💭",
        "That's fascinating! What else is on your mind?",
        "I'm not sure I understand completely. Could you rephrase that?",
        "That's a great point! Let me think about how to respond to that...",
        "I'm always learning! Could you explain that in a different way?",
        "That's something worth discussing! What are your thoughts on this?"
    ]
    
    return random.choice(creative_responses)