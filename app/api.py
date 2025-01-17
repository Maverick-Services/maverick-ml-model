from flask import Flask, request, jsonify
import logging
import os
import string
import nltk
from app.utils import predict_intent, generate_response

# Set the NLTK data path manually
nltk_data_path = os.path.join(os.getcwd(), 'nltk_data')
if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path)
nltk.data.path.append(nltk_data_path)

# Attempt to find the 'punkt' tokenizer
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("punkt not found, downloading...")
    nltk.download('punkt', download_dir=nltk_data_path)

# Your code continues...
# Initialize Flask app
app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Track irrelevant messages per user (by IP address)
irrelevant_question_count = {}
MAX_IRRELEVANT_QUESTIONS = 3

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle incoming messages and respond based on intent."""
    try:
        # Get the incoming message
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        user_message = data['message'].strip().lower()
        user_ip = request.remote_addr  # Track users by IP

        # Clean up punctuation in the message
        user_message = user_message.translate(str.maketrans('', '', string.punctuation))

        # Predict the intent
        intent = predict_intent(user_message)

        # Initialize count if not already present
        if user_ip not in irrelevant_question_count:
            irrelevant_question_count[user_ip] = 0

        # Handle unknown (irrelevant) intent
        if intent == 'unknown':
            irrelevant_question_count[user_ip] += 1
            if irrelevant_question_count[user_ip] <= MAX_IRRELEVANT_QUESTIONS:
                return jsonify({
                    'userMessage': user_message,
                    'botResponse': "I didn't understand that.",
                    'options': []
                })
            elif irrelevant_question_count[user_ip] == MAX_IRRELEVANT_QUESTIONS + 1:
                return jsonify({
                    'userMessage': user_message,
                    'botResponse': "I am understanding.",
                    'options': []
                })
        else:
            # Reset count if the input is relevant
            irrelevant_question_count[user_ip] = 0

        # Generate a response for known intents
        bot_response = generate_response(intent)

        # Add options for "services" intent
        options = []
        if intent == 'services':
            if "What services are you interested in?" in bot_response:
                options = [
                    "Digital Presence Management",
                    "IT Core Services"
                ]

        # Debug logs
        app.logger.debug(f'User Message: {user_message}')
        app.logger.debug(f'Predicted Intent: {intent}')
        app.logger.debug(f'Bot Response: {bot_response}')
        app.logger.debug(f'Options: {options}')

        # Return the response and options
        return jsonify({
            'userMessage': user_message,
            'botResponse': bot_response,
            'options': options
        })

    except Exception as e:
        app.logger.error(f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False, use_reloader=False)

# import nltk
# from flask import Flask, request, jsonify
# import logging
# import os
# import string
# from utils import predict_intent, generate_response

# # Initialize Flask app
# app = Flask(__name__)
# # Setup logging
# logging.basicConfig(level=logging.DEBUG)

# # Track irrelevant messages per user (by IP address)
# irrelevant_question_count = {}
# MAX_IRRELEVANT_QUESTIONS = 3

# @app.route('/api/chat', methods=['POST'])
# def chat():
#     """Handle incoming messages and respond based on intent."""
#     try:
#         # Get the incoming message
#         data = request.get_json()
#         if not data or 'message' not in data:
#             return jsonify({'error': 'No message provided'}), 400

#         user_message = data['message'].strip().lower()
#         user_ip = request.remote_addr  # Track users by IP

#         # Clean up punctuation in the message
#         user_message = user_message.translate(str.maketrans('', '', string.punctuation))

#         # Predict the intent
#         intent = predict_intent(user_message)

#         # Initialize count if not already present
#         if user_ip not in irrelevant_question_count:
#             irrelevant_question_count[user_ip] = 0

#         # Handle unknown (irrelevant) intent
#         if intent == 'unknown':
#             irrelevant_question_count[user_ip] += 1
#             if irrelevant_question_count[user_ip] <= MAX_IRRELEVANT_QUESTIONS:
#                 return jsonify({
#                     'userMessage': user_message,
#                     'botResponse': "I didn't understand that.",
#                     'options': []
#                 })
#             elif irrelevant_question_count[user_ip] == MAX_IRRELEVANT_QUESTIONS + 1:
#                 return jsonify({
#                     'userMessage': user_message,
#                     'botResponse': "I am understanding.",
#                     'options': []
#                 })
#         else:
#             # Reset count if the input is relevant
#             irrelevant_question_count[user_ip] = 0

#         # Generate a response for known intents
#         bot_response = generate_response(intent)

#         # Add options for "services" intent
#         options = []
#         if intent == 'services':
#             if "What services are you interested in?" in bot_response:
#                 options = [
#                     "Digital Presence Management",
#                     "IT Core Services"
#                 ]

#         # Debug logs
#         app.logger.debug(f'User Message: {user_message}')
#         app.logger.debug(f'Predicted Intent: {intent}')
#         app.logger.debug(f'Bot Response: {bot_response}')
#         app.logger.debug(f'Options: {options}')

#         # Return the response and options
#         return jsonify({
#             'userMessage': user_message,
#             'botResponse': bot_response,
#             'options': options
#         })

#     except Exception as e:
#         app.logger.error(f'Error: {str(e)}')
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)) , debug=False ,use_reloader=False)
