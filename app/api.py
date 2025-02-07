# add translate
# from flask import Flask, request, jsonify
# import logging
# import os
# import string
# import nltk
# from utils import predict_intent, generate_response
# from flask_caching import Cache
# from flask_cors import CORS
# import shutil
# import gc
# from googletrans import Translator

# translator = Translator()

# # Initialize Flask app
# app = Flask(__name__)
# CORS(app)
# logging.basicConfig(level=logging.DEBUG)
# app.config['CACHE_TYPE'] = 'simple'
# cache = Cache(app)

# def detect_language(text):
#     return translator.detect(text).lang

# def translate_text(text, src_lang, dest_lang):
#     return translator.translate(text, src=src_lang, dest=dest_lang).text

# @app.route('/api/chat', methods=['POST'])
# def chat():
#     try:
#         data = request.get_json()
#         if not data or 'message' not in data:
#             return jsonify({'error': 'No message provided'}), 400

#         user_message = data['message'].strip()
#         detected_lang = detect_language(user_message)
#         translated_message = translate_text(user_message, detected_lang, 'en')
        
#         print(f"Translated User Message: {translated_message}")

#         intent = predict_intent(translated_message)
#         bot_response = generate_response(intent)
#         translated_response = translate_text(bot_response, 'en', detected_lang)

#         app.logger.debug(f'User Message: {user_message}')
#         app.logger.debug(f'Translated Message: {translated_message}')
#         app.logger.debug(f'Predicted Intent: {intent}')
#         app.logger.debug(f'Bot Response (English): {bot_response}')
#         app.logger.debug(f'Translated Bot Response: {translated_response}')

#         return jsonify({
#             'userMessage': user_message,
#             'botResponse': translated_response,
#             'options': []
#         })
    
#     except Exception as e:
#         app.logger.error(f'Error: {str(e)}')
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8080, debug=False)



from flask import Flask, request, jsonify
import logging
import os
import string
import nltk
from app.utils import predict_intent, generate_response
from flask_caching import Cache
from flask_cors import CORS
import shutil
import gc
from googletrans import Translator


translator = Translator()
# Clear the NLTK data folder before downloading new resources
nltk_data_path = os.path.join(os.getcwd(), 'nltk_data')
if os.path.exists(nltk_data_path):
    shutil.rmtree(nltk_data_path)

# Create the NLTK data path
os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.clear()  # Clear any existing NLTK data paths
nltk.data.path.append(nltk_data_path)

# Download the necessary NLTK data
try:
    nltk.download('punkt_tab', download_dir=nltk_data_path)
    nltk.download('wordnet', download_dir=nltk_data_path)
except Exception as e:
    print(f"Error downloading NLTK data: {e}")

# Initialize Flask app
app = Flask(__name__)
CORS(app)
# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize caching (disable for testing)
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)

def detect_language(text):
    return translator.detect(text).lang

def translate_text(text, src_lang, dest_lang):
    return translator.translate(text, src=src_lang, dest=dest_lang).text

# Track irrelevant messages
irrelevant_question_count = {}
MAX_IRRELEVANT_QUESTIONS = 3

@app.route('/api/ping', methods=['GET'])
def ping():
    """Health check endpoint."""
    return jsonify({'status': 'Model is running'}), 200


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle incoming messages and respond based on intent."""
    try:
        # Parse incoming JSON
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        user_message = data['message'].strip().lower()
        detected_lang = detect_language(user_message)
        translated_message = translate_text(user_message, detected_lang, 'en')
        user_ip = request.remote_addr  # Track users by IP

        # Remove punctuation
        user_message = user_message.translate(str.maketrans('', '', string.punctuation))

        # Predict intent
        intent = predict_intent(translated_message)

        # Initialize or increment irrelevant question count
        if user_ip not in irrelevant_question_count:
            irrelevant_question_count[user_ip] = 0

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
            # Reset irrelevant count for valid intents
            irrelevant_question_count[user_ip] = 0

        # Generate a response
        bot_response = generate_response(intent)
        translated_response = translate_text(bot_response, 'en', detected_lang)
        # Add options if intent is "services"
        options = []
        if intent == 'services':
            if "What services are you interested in?" in bot_response:
                options = [
                    "Digital Presence Management",
                    "IT Core Services"
                ]

        # Debug logs
        app.logger.debug(f'User Message: {user_message}')
        app.logger.debug(f'Translated Message: {translated_message}')
        app.logger.debug(f'Predicted Intent: {intent}')
        app.logger.debug(f'Bot Response (English): {bot_response}')
        app.logger.debug(f'Translated Bot Response: {translated_response}')
        # Return response
        return jsonify({
            'userMessage': user_message,
            'botResponse': translated_response,
            'options': options
        })

    except MemoryError:
        gc.collect()  # Attempt to free memory
        app.logger.error("MemoryError: Memory usage exceeded")
        return jsonify({'error': 'Server out of memory. Please try again later.'}), 500

    except Exception as e:
        app.logger.error(f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

    finally:
        # Collect garbage to free memory after each request
        gc.collect()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False, use_reloader=False)



