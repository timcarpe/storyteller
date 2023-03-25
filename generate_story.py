import streamlit as st
import openai

#Define the class StoryPage
class StoryPage:
    def __init__(self, pagetext, question, image_prompt, image_url=""):
        self.pagetext = pagetext
        self.question = question
        self.image_prompt = image_prompt
        self.image_url = image_url

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
def generate_images(story_pages, image_prompt_style, use_dalle_images=False):
    for element in story_pages:
        if use_dalle_images:
            response = openai.Image.create(
            prompt=element.image_prompt+"\n"+image_prompt_style,
            n=1,
            size="256x256"
            )
            url = response['data'][0]['url']
        else:
            url="https://th.bing.com/th/id/OIP.w3UA6Hh9MDv2u0rts8rwqQHaHa?pid=ImgDet&rs=1"
        element.image_url = url
        #st.image(url, caption=element.pagetext)
