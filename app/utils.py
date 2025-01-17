import nltk
import numpy as np
import joblib
import json
import string
import os
import logging

from sklearn.preprocessing import LabelEncoder

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the NLTK Lemmatizer
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
lemmatizer = nltk.WordNetLemmatizer()

# Define the base directory and paths to the files
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, '../model/chatbot_model.pkl')
label_encoder_path = os.path.join(base_dir, '../model/label_encoder.pkl')
intents_path = os.path.join(base_dir, '../model/intents.json')

logger.debug(f"Loading model from {model_path}")
model = joblib.load(model_path)
logger.debug("Model loaded successfully")

logger.debug(f"Loading label encoder from {label_encoder_path}")
label_encoder = joblib.load(label_encoder_path)
logger.debug("Label encoder loaded successfully")

logger.debug(f"Loading intents from {intents_path}")
with open(intents_path, 'r') as file:
    intents = json.load(file)
logger.debug("Intents loaded successfully")

def preprocess_text(input_text):
    """Preprocess input text by tokenizing and lemmatizing."""
    tokens = nltk.word_tokenize(input_text)
    tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens]
    return " ".join(tokens)

def predict_intent(user_message, logger=None):
    """Predict the intent of the user's message."""
    processed_message = preprocess_text(user_message)
    intent_idx = model.predict([processed_message])[0]
    intent = label_encoder.inverse_transform([intent_idx])[0]
    
    # Log if logger is provided
    if logger:
        logger.debug(f"Predicted Intent: {intent}")
    
    return intent

def generate_response(intent):
    """Generate a response based on the predicted intent."""
    # Direct responses for known intents
    if intent == 'services':
        return "We provide IT services such as Digital Presence Management and Core Technical Services. What services are you interested in?"
    elif intent == 'service_info':
        return "Here are the details of our services:\n- Digital Presence Management\n- IT Core Services"
    
    # General response generation from the intents.json file
    for intent_data in intents['intents']:
        if intent_data['tag'] == intent:
            return np.random.choice(intent_data['responses'])

    return "I'm sorry, I don't understand."




# import nltk
# import numpy as np
# import joblib
# import json
# import string

# from sklearn.preprocessing import LabelEncoder

# # Initialize the NLTK Lemmatizer
# nltk.download('punkt')
# nltk.download('wordnet')
# lemmatizer = nltk.WordNetLemmatizer()

# # Load required files
# model = joblib.load('../model/chatbot_model.pkl')
# label_encoder = joblib.load('../model/label_encoder.pkl')

# with open('../model/intents.json', 'r') as file:
#     intents = json.load(file)

# def preprocess_text(input_text):
#     """Preprocess input text by tokenizing and lemmatizing."""
#     tokens = nltk.word_tokenize(input_text)
#     tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens]
#     return " ".join(tokens)

# def predict_intent(user_message, logger=None):
#     """Predict the intent of the user's message."""
#     processed_message = preprocess_text(user_message)
#     intent_idx = model.predict([processed_message])[0]
#     intent = label_encoder.inverse_transform([intent_idx])[0]
    
#     # Log if logger is provided
#     if logger:
#         logger.debug(f"Predicted Intent: {intent}")
    
#     return intent

# def generate_response(intent):
#     """Generate a response based on the predicted intent."""
#     # Direct responses for known intents
#     if intent == 'services':
#         return "We provide IT services such as Digital Presence Management and Core Technical Services. What services are you interested in?"
#     elif intent == 'service_info':
#         return "Here are the details of our services:\n- Digital Presence Management\n- IT Core Services"
    
#     # General response generation from the intents.json file
#     for intent_data in intents['intents']:
#         if intent_data['tag'] == intent:
#             return np.random.choice(intent_data['responses'])

#     return "I'm sorry, I don't understand."