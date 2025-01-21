from flask import Flask, request, jsonify
import logging
import os
import string
import nltk
from utils import predict_intent, generate_response
from flask_caching import Cache
import shutil
import gc

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

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize caching (disable for testing)
app.config['CACHE_TYPE'] = 'null'
cache = Cache(app)

# Track irrelevant messages
irrelevant_question_count = {}
MAX_IRRELEVANT_QUESTIONS = 3


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle incoming messages and respond based on intent."""
    try:
        # Parse incoming JSON
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        user_message = data['message'].strip().lower()
        user_ip = request.remote_addr  # Track users by IP

        # Remove punctuation
        user_message = user_message.translate(str.maketrans('', '', string.punctuation))

        # Predict intent
        intent = predict_intent(user_message)

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
        app.logger.debug(f'Predicted Intent: {intent}')
        app.logger.debug(f'Bot Response: {bot_response}')
        app.logger.debug(f'Options: {options}')

        # Return response
        return jsonify({
            'userMessage': user_message,
            'botResponse': bot_response,
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



# from flask import Flask, request, jsonify
# import logging
# import os
# import string
# import nltk
# from utils import predict_intent, generate_response
# # from memory_profiler import profile 
# # import gc 
# from flask_caching import Cache

# nltk_data_path = os.path.join(os.getcwd(), 'nltk_data')
# os.makedirs(nltk_data_path, exist_ok=True)  # Ensure the directory exists
# nltk.data.path.clear()
# nltk.data.path.append(nltk_data_path)

# # Download the punkt tokenizer if not already present
# if not os.path.exists(os.path.join(nltk_data_path, 'tokenizers/punkt_tab')):
#     nltk.download('punkt_tab', download_dir=nltk_data_path)
# if not os.path.exists(os.path.join(nltk_data_path, 'corpora/wordnet')): 
#     nltk.download('wordnet', download_dir=nltk_data_path)

# # nltk.download('punkt')
# # C:\Users\Dell\Downloads\Chatbot-Scratch\custom-ml-project\app\nltk_data\tokenizers\punkt
# # Your code continues...
# # Initialize Flask app
# app = Flask(__name__)

# # Setup logging
# logging.basicConfig(level=logging.DEBUG)

# # Initialize cache
# # cache = Cache(app, config={'CACHE_TYPE': 'simple'})
# app.config['CACHE_TYPE'] = os.getenv('CACHE_TYPE', 'SimpleCache')
# cache = Cache(app)

# # Track irrelevant messages per user (by IP address)
# irrelevant_question_count = {}
# MAX_IRRELEVANT_QUESTIONS = 3

# @app.route('/api/chat', methods=['POST'])

# # @cache.cached(timeout=300)
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
#     app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False, use_reloader=False)

