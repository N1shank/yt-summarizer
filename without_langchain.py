import os 
import openai
import faiss
import tempfile

from moviepy.editor import *
from pytube import YouTube
from urllib.parse import urlparse, parse_qs

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.chains import RetrievalQAWithSourcesChain
from langchain import OpenAI



# Transcripe MP3 Audio function
def transscribe_audio(file_path):
    file_size = os.path.getsize(file_path)
    file_size_in_mb = file_size / (1024 * 1024)
    if file_size_in_mb < 25:
        with open(file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)

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
        transcript = transscribe_audio(audio_path)
        
        # Delete the original audio file
        os.remove(audio_path)
        
        print(transcript.text)

    # Splitting the text
    textsplitter = CharacterTextSplitter(chunk_size=512, chunk_overlap=0)

    texts = textsplitter.split_text(transcript.text)

    store = FAISS.from_texts(
        texts, OpenAIEmbeddings(), metadatas=[{"source": f"Text chunk {i} of {len(texts)}"} for i in range(len(texts))]
    )

    faiss.write_index(store.index, "docs.faiss")

    llm = OpenAI(temperature=0)
    chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm, chain_type="stuff", retriever=store.as_retriever()
    )

    # Enter question / answer loop
    while True:
        question = input("Question: ")
        answer = chain({"question": question}, return_only_outputs=True)
        print("Answer: ", answer["answer"])
        print("Sources: ", answer["sources"])
        print("\n")


if __name__ == "__main__":
    main()