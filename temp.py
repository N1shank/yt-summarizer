# https://www.youtube.com/watch?v=EsVDjPdXNPk&t=11s  
# workplete team intro video


import os 
import openai

import tempfile

from moviepy.editor import *
from pytube import YouTube
from urllib.parse import urlparse, parse_qs


prompt_template = '''
You are a Youtube summarizer and time stamp generator tool, which helps in generating a summary and sub topics with appropriate 
time-stamps from the given transcript.The transcript contains the audio of the youtube video in text format. 
You are supposed to give out sub topics and a summary of the whole video as precise as possible  with time stamps

You can use this transcript which contains content of the youtube video in this format.
"Format : 
chunk_id
HH:MM:SS,MIL --> HH:MM:SS,MIL
Text transcription of the audio chunk from above time stamp"

You can refer to this one example :
"Example :
1
00:00:00,000 --> 00:00:03,520
My name is Jack and I'm the founder and CEO of Workplete."

Here you can see the trancript format comes in multiple chunks with specified timestamps and the text data of the youtube video in that particular timestamp.

Now you need to understand the content/ text information of all the chunks in the transcript and provide a precise summary of the youtube video in text format.
You should also provide sub topics with appropriate one liner summary and timestamps using transcript chunk's timestamps.
You are expected to give output in this format.
Output :
Summary - 
Subtopic - Topic 1 - HH:MM:SS --> HH:MM:SS - One liner of the sub topic
           Topic 2 - HH:MM:SS --> HH:MM:SS - One liner of the sub topic

Here is the transcript 
{transcript}
'''



# Transcripe MP3 Audio function
def transcribe_audio(file_path):
    file_size = os.path.getsize(file_path)
    file_size_in_mb = file_size / (1024 * 1024)
    if file_size_in_mb < 25:
        with open(file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file, response_format = "srt")

        return transcript
    else:
        print("Please provide a smaller audio file (max 25mb).")

def divide_segments():
    return

# Main application
def main(): 
    # Get YouTube video URL from user
    url = input("YouTube Video URL: ")
    # Extract the video ID from the url
    query = urlparse(url).query
    params = parse_qs(query)
    video_id = params["v"][0]

    with tempfile.TemporaryDirectory() as temp_dir:
        
        # Download video audio
        yt = YouTube(url)

        # Get the first available audio stream and download this stream
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_stream.download(output_path=temp_dir)

        # Convert the audio file to MP3
        audio_path = os.path.join(temp_dir, audio_stream.default_filename)
        audio_clip = AudioFileClip(audio_path)
        audio_clip.write_audiofile(os.path.join(temp_dir, f"{video_id}.mp3"))

        # Keep the path of the audio file
        audio_path = f"{temp_dir}/{video_id}.mp3"

        # Transscripe the MP3 audio to text
        transcript = transcribe_audio(audio_path)
        
        # Delete the original audio file
        os.remove(audio_path)
        
        #print(transcript)

        response = gpt_response(transcript)

        print(response)
        


def gpt_response(transcript):
    
    prompt = prompt_template
    prompt = prompt.replace("$transcript", transcript)

    response = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "system", "content": prompt}, {"role": "user", "content": "This is an example of an output:\nSubtopics - \nTopic : <Topic 1> - Timestamp : <HH:MM:SS --> HH:MM:SS> - <One liner of the sub topic>\nTopic : <Topic 2> - Timestamp : <HH:MM:SS --> HH:MM:SS> - <One liner of the next sub topic> , Now give your output for the given transcript."}])

    summary_and_timestamps = response['choices'][0]['message']['content']

    return summary_and_timestamps


if __name__ == "__main__":
    main()