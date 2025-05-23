# if you dont use pipenv uncomment the following:
from dotenv import load_dotenv
load_dotenv()

#Step1: Setup Audio recorder (ffmpeg & portaudio)
# ffmpeg, portaudio, pyaudio
import logging
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
import os
import groq
import requests  # Add this import

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def record_audio(file_path, timeout=20, phrase_time_limit=None):
    """
    Simplified function to record audio from the microphone and save it as an MP3 file.

    Args:
    file_path (str): Path to save the recorded audio file.
    timeout (int): Maximum time to wait for a phrase to start (in seconds).
    phrase_time_limit (int): Maximum time for the phrase to be recorded (in seconds).
    """
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            logging.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            logging.info("Start speaking now...")
            
            # Record the audio
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            logging.info("Recording complete.")
            
            # Convert the recorded audio to an MP3 file
            wav_data = audio_data.get_wav_data()
            audio_segment = AudioSegment.from_wav(BytesIO(wav_data))
            audio_segment.export(file_path, format="mp3", bitrate="128k")
            
            logging.info(f"Audio saved to {file_path}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

audio_filepath="patient_voice_test_for_patient.mp3"
#record_audio(file_path=audio_filepath)

#Step2: Setup Speech to text–STT–model for transcription
import os
import groq

GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
stt_model="whisper-large-v3"

def transcribe_with_groq(stt_model, audio_filepath, GROQ_API_KEY):
    try:
        if not GROQ_API_KEY:
            logging.error("GROQ_API_KEY is missing")
            raise ValueError("GROQ API key not found or invalid")
        
        # Open and read the audio file
        with open(audio_filepath, "rb") as audio_file:
            files = {
                'file': ('audio.mp3', audio_file, 'audio/mpeg')
            }
            
            # Prepare the data payload
            data = {
                'model': stt_model,
                'language': 'en',
                'response_format': 'text',
                'temperature': 0
            }
            
            # Set up headers
            headers = {
                'Authorization': f'Bearer {GROQ_API_KEY}'
            }
            
            # Make the API request
            response = requests.post(
                'https://api.groq.com/openai/v1/audio/transcriptions',
                headers=headers,
                files=files,
                data=data
            )
            
            # Enhanced error handling
            if response.status_code == 401:
                logging.error("Authentication failed: Invalid API key")
                raise ValueError("Invalid GROQ API key")
            elif response.status_code != 200:
                error_message = f"API request failed: {response.status_code} - {response.text}"
                logging.error(error_message)
                raise Exception(error_message)
            
            return response.text
            
    except Exception as e:
        logging.error(f"Transcription error: {str(e)}")
        raise

