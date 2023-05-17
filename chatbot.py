# summary: 
# produces a share-able url to the interface where user can record their speech and get a video response
# uses gradio to build a user interface, has a mic input that takes in user's audio
# speech-to-text the user audio, and use chatgpt to generate a response 
# use aws polly to text-to-speech chatgpt's response, and generate an audio
# give face image, audio/text response to d-id, which generates a speaking head video
# play the video in gradio user interface


# local directory to store output video
directory = ""
# credentials for d_id, aws, openai, and cloudinary, please fill it in yourself
did_key = ""
ACCESS_KEY = "" #open_file('accesskey.txt')
SECRET_KEY = "" #open_file('secretkey.txt')
polly = boto3.client('polly', region_name='us-east-1',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
session = boto3.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
s3 = session.client('s3',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
# ChatGPT的key，这里chatGPT主要用来将提问的语音转文本形式，然后通过文本形式的问题获取对应的AI文字回答
openai.api_key = "" #open_file('openaiapikey.txt')
# Cloudinary的Key，这里Cloudinary是做CDN，用来存文本、音频、视频这些东西，并能通过网络访问到
cloudinary.config(
cloud_name = "",
api_key = "",
api_secret = ""
)
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Basic " + did_key
}

import sys
print(sys.executable)
import urllib.request
import requests
import openai
import boto3
import cloudinary
import cloudinary.uploader
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
import gradio as gr
from gtts import gTTS
import os
import requests
import subprocess
import webbrowser
import time
import warnings

gmh = "https://i.imgur.com/7Nnvv7d.png" # face image of george moses horton
role_set = "You are George Moses Horton, an African American Poet. Please speak like George Moses Horton." # role set for chatgpt
warnings.filterwarnings("ignore", category=UserWarning)
messages = [{"role": "system", "content": role_set}] # initialize messages

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()



def upload_to_cloudinary(file_path):
    response = cloudinary.uploader.upload(file_path, resource_type="video")
    return response["secure_url"]

	

# get video url / download video based on talk id
def check_video_status(video_id, headers):
    
    get_url = f"https://api.d-id.com/talks/{video_id}"
    while True:
        

        headers = {
            "accept": "application/json",
            "authorization": "Basic " + did_key
        }
        get_response = requests.get(get_url, headers=headers)
        video_status = get_response.json().get("status")

        print(f"Video status: {get_response.json()}")
        if video_status == "done":
            return get_response.json().get("result_url")
        elif video_status == "failed":
            print("Video generation failed.")
            return None
        time.sleep(5)
        print(get_url)

def startfile(fn):
    os.system('open %s' % fn)

# process function for gradio, takes in audio to chatgpt and generate video from d_id
def decipher(audio):
    global messages
    global audio_file
    audio_file = open(audio, "rb")
    # Using OpenAI's speech-to-text model
    # speech to text the audio file
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    messages.append({"role": "user", "content": transcript["text"]})
    # lets chatgpt to chat complete based on user's input
    response =  openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    system_message = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": system_message})

    # use AWS Polly to tts chatgpt's response
    voice_stream = polly.synthesize_speech(Text=system_message, VoiceId='Joey', OutputFormat='mp3')
    with open('system_message.mp3', 'wb') as f:
        f.write(voice_stream['AudioStream'].read())
        f.close()

    # Upload the audio file to cloudinary and get the public URL
    audio_public_url = upload_to_cloudinary('system_message.mp3')

    # D-ID API call
    url = "https://api.d-id.com/talks"

    payload = {
    "script": {
        "type": "text",
        "provider": {
            "type": "amazon",
            "voice_id": "Joey"
        },
        "input": system_message,
        "audio_url": audio_public_url
    },
    "source_url": "https://i.imgur.com/7Nnvv7d.png",
    "driver_url": "bank://lively/driver-05",
    "config": {
        "stitch": "true"
    }
    }

    # create video using d_id api call
    response = requests.post(url, json=payload, headers=headers)
    video_id = response.json().get("id")

    # Make a GET request using the video_id
    video_url = check_video_status(video_id, headers)
    if video_url is not None:
        webbrowser.open(video_url)
    
    chat_transcript = ""
    for message in messages:
        if message['role'] != "system":
            chat_transcript += message['role'] + ": " + message['content'] + "\n\n"

    urllib.request.urlretrieve(video_url, 'video_name.mp4') 
    return chat_transcript, directory + "/video_name.mp4"

# main function to launch the gradio interface, output is a shareable url.
interface = gr.Interface(share=True, fn=decipher, inputs=gr.Audio(source="microphone", type="filepath"), outputs=["text", "playablevideo"])
interface.launch()