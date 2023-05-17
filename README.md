# Summary
A face-to-face chatbot that speaks like George Moses Horton.
# How to Use
- in the python file, enter credentials of cloud services such as d-id and openai
- run the file, and a url will be printed to the terminal
- open the url with any web browser

# How It Works
- produces a share-able url where user can record their speech and get a video response
- uses gradio to build a user interface, has a mic input that takes in user's audio
- speech-to-text the user audio, and use chatgpt to generate a response
- use aws polly to text-to-speech chatgpt's response, and generate an audio
- give face image, audio/text response to d-id, which generates a speaking head video
- play the video in gradio user interface
# Acknowledgement
Thanks to oller2.scott who answered my question on D-ID's forum.