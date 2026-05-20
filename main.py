# Step 1: Open microphone and capture audio
import pyaudio
import wave
import os
from dotenv import load_dotenv
load_dotenv()
from groq import Groq
import pyttsx3


client = Groq(
    api_key = os.getenv('GROQ_API_KEY')
)

def record_audio(filename='input.wav', sample_rate=44100, chunk=1024, channels=1, duration=5):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=chunk,
                        input_device_index=1)
    
    print(f'Recording for {duration} seconds....')

    frames = []
    
# Step 2: Detect end of speech (VAD)
    try:
        one_sec = sample_rate*chunk
        stop_point = duration*one_sec
        counter = 0
        while counter < stop_point:
            data = stream.read(chunk)
            frames.append(data)
            counter += 1

    except KeyboardInterrupt:
        pass

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))

    print(f'Saved to {filename}')
    return filename


# Step 3: Transcribe audio with Whisper
def transcribe_audio(filename):
    with open(filename, 'rb') as file:
       respones = client.audio.transcriptions.create(
           model = 'whisper-large-v3-turbo',
           file = file
       )
       return respones.text
       
   

# Step 4: Send Transcript to Groq LLM
def get_response(text):
    text_reply = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[
            {'role':'system', 'content':'Your are helpful Voice Agent with special experties in Medical field'},
            {'role': 'user', 'content': text}
        ]
    )
    reply= text_reply.choices[0].message.content
    return reply

# Step 5: Convert respones to Speech with Piper
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


while True:
    audio_file = record_audio(duration=3)
    text = transcribe_audio(audio_file)
    print(f'You Said: {text}')
    
    if 'exit' in text.lower() or 'goodbye' in text.lower():
        speak('Goodbye')
        break


    respones = get_response(text)
    print(f'Agent: {respones}')
    speak(respones)

# Step 6: Play audio back
