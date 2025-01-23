import streamlit as st
import requests

st.title("Custom Chatbot")
st.write("Type your message below to chat with the bot.")

# Input box for user message
user_message = st.text_input("You:", placeholder="Type your message here...")

if st.button("Send"):
    if user_message.strip():
        try:
            # Send POST request to Flask API
            response = requests.post("https://maverick-ml-model.onrender.com/api/chat", json={"message": user_message})
            if response.status_code == 200:
                data = response.json()
                bot_response = data.get('botResponse', 'No response received.')
                st.text_area("Bot:", value=bot_response, height=150)
                options = data.get('options', [])
                if options:
                    st.write("Options available:")
                    for option in options:
                        st.write(f"- {option}")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a message.")

st.write("---")
st.caption("Custom chatbot powered by Flask and Streamlit.")
