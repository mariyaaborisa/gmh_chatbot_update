# Summary:
# This code generates a shareable URL for an interface where users can record their speech and receive a video response.
# It uses Gradio to create a user interface with a microphone input for capturing user's audio.
# The code performs speech-to-text on the user's audio and utilizes ChatGPT to generate a response.
# It then uses AWS Polly to convert ChatGPT's response to text-to-speech and generate an audio.
# The code provides a face image, audio/text response to D-ID, which generates a speaking head video.
# Finally, it plays the video in the Gradio user interface.

# Local directory to store the output video
directory = ""

# Credentials for D-ID, AWS, OpenAI, and Cloudinary; please fill in with your own credentials
did_key = ""
ACCESS_KEY = ""  # Access key for AWS (e.g., 'AKIARMTEUYUB6VL2XMXF')
SECRET_KEY = ""  # Secret key for AWS (e.g., 'Y2j8/V3Mllj5SoQtp4zEA8FzXLgpUapcG09te3ai')

# Initialize AWS Polly client with specified region and credentials
polly = boto3.client('polly', region_name='us-east-1', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

# Create an AWS session and S3 client with the same credentials
session = boto3.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
s3 = session.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

# Set the API key for ChatGPT, which is used to transcribe audio and generate AI text responses
openai.api_key = ""  # Your OpenAI API key

# Configure Cloudinary with your Cloudinary credentials, used for CDN services
cloudinary.config(
    cloud_name="your_cloud_name",
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# Define headers for API requests to D-ID
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Basic " + did_key
}

# Import necessary Python modules and libraries
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

# Define the URL for a face image (George Moses Horton) and the role set for ChatGPT
gmh = "https://i.imgur.com/7Nnvv7d.png"
role_set = "You are George Moses Horton, an African American Poet. Please speak like George Moses Horton."

# Ignore UserWarning messages
warnings.filterwarnings("ignore", category=UserWarning)

# Initialize a list of messages with a system message
messages = [{"role": "system", "content": role_set}]
