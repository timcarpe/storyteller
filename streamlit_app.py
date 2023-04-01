import streamlit as st
import openai
from generate_story import *
from generate_file import *

openai.api_key = st.secrets["API_KEY"]
image_prompt_style = "vintage, in the art style of Maurice Sendak"

st.title("Story Teller")

user_api_key = st.sidebar.text_input(label='You can optionally use your API key:', value='Enter your OpenAI API key')
user_topic = st.sidebar.text_input(label='You can optionally choose a story topic:', value='')
image_prompt_style = st.sidebar.text_area(label='You can optionally choose the style of images:', value=image_prompt_style)
image_type = st.sidebar.radio(
    "Image Generation Method",
    ('Placeholder', 'DALL-E-2', 'Stable Diffusion'))

if st.button("Generate Story"):
    with st.spinner('Generating Story...'):

        #Generate the story
        text = generate_story_response(user_topic)

        #Split the story into pages
        story_pages = split_story(text)

        #Generate the images
        generate_images(story_pages, image_prompt_style=image_prompt_style, image_type=image_type)

        #Display the story
        for element in story_pages:
            if element.image_file != None: 
                st.image(element.image_file, caption=element.pagetext)
            else:
                st.image(element.image_url, caption=element.pagetext)
            st.write("")
            st.write(element.question)
            st.write("")

        #Generate the .docx file
        filename = "Story Teller Output"
        generate_document(story_pages, filename)

        #Download button
        st.sidebar.download_button(label="Download Story", data=open(filename+".docx", "rb").read(), file_name=filename+".docx", mime="application/docx")

