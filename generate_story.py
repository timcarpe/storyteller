import streamlit as st
import openai
import os
import io
import warnings
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import urllib.request
import shutil


stability_api = client.StabilityInference(
    key="sk-y8k52RAAEUtxCrlbtJNeJyT1uioUKjZXEGRJP4gFx3caqz45", # API Key reference.
    verbose=True, # Print debug messages.
    engine="stable-diffusion-v1-5", # Set the engine to use for generation.
    # Available engines: stable-diffusion-v1 stable-diffusion-v1-5 stable-diffusion-512-v2-0 stable-diffusion-768-v2-0
    # stable-diffusion-512-v2-1 stable-diffusion-768-v2-1 stable-inpainting-v1-0 stable-inpainting-512-v2-0
)


#Define the class StoryPage
class StoryPage:
    def __init__(self, pagetext, question, image_prompt, image_url="", image_file=None):
        self.pagetext = pagetext
        self.question = question
        self.image_prompt = image_prompt
        self.image_url = image_url
        self.image_file = image_file

    def __str__(self):
        return f"Pagetext: {self.pagetext}\nQuestion: {self.question}\nImage: {self.image_prompt}\nURL: {self.image_url}\n\n"

#Generate the story response from OpenAI with optional topic
def generate_story_response(story_topic=""):
    if story_topic != "":
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You create scripts for stories for children to learn how to read. You use simple language and short sentences. You also use pictures to help the children understand the story. You only write stories for children with the following lines of output: [Pagetext:] [Question:] [Image:]"},
                {"role": "user", "content": "Create a children's story about " + story_topic + " for a child to learn how to read. Use ONLY the following lines of output: [Pagetext:] [Question:] [Image:].\n\n[Pagetext:] is the script for a mother to read to child using simple conversational language. Each time the mother speaks there should be two or three sentences. The mother should speak at least five times when reading the story.\n[Question:] is a followup question the pagetext can ask to check if the child understands. The questions should be for a 5 year old. They can be ANY simple comprehension question about the image or what the mother just read. Examples question starters: 'What was..' or 'What color was..'\n[Image:] is an image prompt which will be used by DALL-E 2 or Stable Difussion to generate an image. Explain what is happening in the picture with keywords describing the characters like 'a puppy' NOT 'Max the puppy'. Do NOT use names from the story and instead describe what they are, what they are doing and what they are wearing.\n\nUse ONLY the following format:\n\n[Pagetext:]\n[Question:]\n[Image:]\n\n[Pagetext:]\n[Question:]\n[Image:]\n\n"},
            ]
        )
    else:
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You create scripts for stories for children to learn how to read. You use simple language and short sentences. You also use pictures to help the children understand the story. You only write stories for children with the following lines of output: [Pagetext:] [Question:] [Image:]"},
                {"role": "user", "content": "Create a story about an animal OR a famous children's story for a child to learn how to read. Use ONLY the following lines of output: [Pagetext:] [Question:] [Image:].\n\n[Pagetext:] is the script for a mother to read to child using simple conversational language. Each time the mother speaks there should be two or three sentences. The mother should speak at least five times when reading the story.\n[Question:] is a followup question the pagetext can ask to check if the child understands. The questions should be for a 5 year old. They can be ANY simple comprehension question about the image or what the mother just read. Examples question starters: 'What was..' or 'What color was..'\n[Image:] is an image prompt which will be used by DALL-E 2 or Stable Difussion to generate an image. Explain what is happening in the picture with keywords describing the characters like 'a puppy' NOT 'Max the puppy'. Do NOT use names from the story and instead describe what they are, what they are doing and what they are wearing.\n\nUse ONLY the following format:\n\n[Pagetext:]\n[Question:]\n[Image:]\n\n[Pagetext:]\n[Question:]\n[Image:]\n\n"},
            ]
        )
    return ''.join(response.choices[0].message.content)

#Parse the story response into a list of StoryPage objects
def split_story(story):
    lines = [line.strip() for line in story.split("[Pagetext:]") if line]
    story_pages = []

    for line in lines:
        parts = line.split("[Question:]")
        pagetext = parts[0].strip() if len(parts) > 0 else ""
        
        if len(parts) > 1:
            subparts = parts[1].split("[Image:]")
            question = subparts[0].strip()
            image_prompt = subparts[1].strip() if len(subparts) > 1 else ""
        else:
            question, image_prompt = "", ""

        story_pages.append(StoryPage(pagetext, question, image_prompt))
    return story_pages

#Generate the images using DALL-E 2 or use placeholder image
def generate_images(story_pages, image_prompt_style, image_type):

    img = None
    url = ""

    for element in story_pages:

        #Generate image using DALL-E 2
        if image_type == "DALL-E-2":
            response = openai.Image.create(
            prompt=element.image_prompt+"\n"+image_prompt_style,
            n=1,
            size="256x256"
            )

            #Get web URL of image
            url = response['data'][0]['url']
            #Download image
            urllib.request.urlretrieve(url, str(story_pages.index(element)) + ".png")
            img = Image.open(str(story_pages.index(element)) + ".png")
            #set local image URL
            url = str(story_pages.index(element))+ ".png"

        #Generate image using Stable Difussion
        elif image_type == "Stable Diffusion":
            answers = stability_api.generate(
                prompt=element.image_prompt+"\n"+image_prompt_style,
                cfg_scale=8.0, # Influences how strongly your generation is guided to match your prompt.
                width=256,
                height=256,
                sampler=generation.SAMPLER_K_DPMPP_2M # (Available Samplers: ddim, plms, k_euler, k_euler_ancestral, k_heun, k_dpm_2, k_dpm_2_ancestral, k_dpmpp_2s_ancestral, k_lms, k_dpmpp_2m)
            )
            #Get web URL of image and save it locally
            for resp in answers:
                for artifact in resp.artifacts:
                    if artifact.finish_reason == generation.FILTER:
                        warnings.warn(
                            "Your request activated the API's safety filters and could not be processed."
                            "Please modify the prompt and try again.")
                    if artifact.type == generation.ARTIFACT_IMAGE:
                        img = Image.open(io.BytesIO(artifact.binary))
                        img.save(str(story_pages.index(element))+ ".png")
                        url = str(story_pages.index(element))+ ".png"
        else:
            #Use placeholder image URL
            url="placeholder.png"
            img = Image.open("placeholder.png")

        #Set image URL and image
        element.image_url = url
        if img:
            element.image_file = img
