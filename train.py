import nltk
import numpy as np
import joblib
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

# Download NLTK resources
nltk.download('punkt')
nltk.download('wordnet')

# Load intents file
with open('model/intents.json', 'r') as file:
    intents = json.load(file)

lemmatizer = nltk.WordNetLemmatizer()

# Prepare training data
patterns = []
tags = []
for intent in intents['intents']:
    for pattern in intent['patterns']:
        tokens = nltk.word_tokenize(pattern)
        tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens]
        patterns.append(" ".join(tokens))
        tags.append(intent['tag'])

# Encode tags as labels
label_encoder = LabelEncoder()
labels = label_encoder.fit_transform(tags)

# Save label encoder
joblib.dump(label_encoder, 'model/label_encoder.pkl')

# Train a custom model
model = Pipeline([
    ('vectorizer', CountVectorizer()),
    ('classifier', MultinomialNB())
])

model.fit(patterns, labels)

# Save the trained model
joblib.dump(model, 'model/chatbot_model.pkl')
print("Model training complete. Saved to 'model/chatbot_model.pkl'")
