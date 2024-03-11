from openai import OpenAI
import os
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

audio_file= open("joker2.mp4", "rb")
transcription = client.audio.transcriptions.create(
  model="whisper-1",
  language="es", 
  file=audio_file
)
print(transcription.text)