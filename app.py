import streamlit as st
import random
import time
import streamlit.components.v1 as components
import base64
import requests
import urllib.request
import json
import os
import ssl
from dotenv import load_dotenv

load_dotenv()
LOGO_IMAGE = "images/NHS_England_logo.jpg"
API_KEY = os.getenv('API_KEY')

# Streamed response emulator
def response_generator(message, persona, language):

    data = {
        "language": language,
        "persona": persona,
        "question": message
    }
    body = str.encode(json.dumps(data))

    url = 'https://nhs-career-coach-2.uksouth.inference.ml.azure.com/score'
    # Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
    api_key = API_KEY
    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")

    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

    req = urllib.request.Request(url, body, headers)

    result = ""
    try:
        response = urllib.request.urlopen(req)

        result = response.read()
        print(result)
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))

    result = json.loads(result)
    result = result['output']

    for word in result.split(" "):
        yield word + " "
        time.sleep(0.05)


with open('./style.css') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)



st.markdown(
    f"""
    <div class="container">
        <img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()}">
        <p class="logo-text">Workforce, training and education</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("NHS Career coach")
st.subheader("Who are you?")

persona = st.selectbox(
    "Who are you?",
    (
        "Child", 
        "Adult",
    ),
    index=None,
    placeholder="I am a...",
)
language = st.selectbox(
    "Talk to me in...",
    (
        "English", 
        "Spanish", 
        "Korean",
        "Pirate",
    ),
    index=None,
    placeholder="I am a...",
)

st.subheader("Let's chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(st.session_state.messages[-1]['content'], persona, language))
        st.markdown(
            f"""
            <div class="container container--thumbs">
                <img class="thumb" src="data:image/png;base64,{base64.b64encode(open("./images/thumb-up.png", "rb").read()).decode()}" width=50 height=50>
                <img class="thumb" src="data:image/png;base64,{base64.b64encode(open("./images/thumb-down.png", "rb").read()).decode()}" width=50 height=50>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})