import streamlit as st
import openai
from generate_story import *
import time
import dotenv
import os

# Load the values from the .env file into the environment variables
dotenv.load_dotenv()

# Get the API key from the environment variables
api_key = os.environ.get('API_KEY')
openai.api_key = api_key

image_prompt_style = "children's book style, watercolor, clear, simple, bright, colorful, cartoon"

st.title("Story Teller")

user_api_key = st.sidebar.text_input(label='You can optionally use your API key:', value='Enter your OpenAI API key')
user_topic = st.sidebar.text_input(label='You can optionally choose a story topic:', value='')
image_prompt_style = st.sidebar.text_input(label='You can optionally choose the style of images:', value="children's book style, watercolor, clear, simple, bright, colorful, cartoon")
use_dalle_images = st.sidebar.checkbox("Generate DALLE - 2 Images")

if st.button("Generate Story"):
    with st.spinner('Generating Story...'):
        #st.write('Generating Story...')
        text = generate_story_response(user_topic)
        story_pages = split_story(text)
        generate_images(story_pages, image_prompt_style=image_prompt_style, use_dalle_images=use_dalle_images)
        for element in story_pages:
            st.image(element.image_url, caption=element.pagetext)
            st.write("")
            st.write(element.question)
            st.write("")

