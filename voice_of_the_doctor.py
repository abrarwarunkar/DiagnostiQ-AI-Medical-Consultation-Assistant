from dotenv import load_dotenv
load_dotenv()

import os
import subprocess
import platform
from gtts import gTTS
import elevenlabs
from elevenlabs.client import ElevenLabs

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

def text_to_speech_with_gtts_old(input_text, output_filepath):
    language = "en"
    audioobj = gTTS(
        text=input_text,
        lang=language,
        slow=False
    )
    audioobj.save(output_filepath)

def text_to_speech_with_elevenlabs_old(input_text, output_filepath):
    print(f"Using API key: {ELEVENLABS_API_KEY}")
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio = client.generate(
        text=input_text,
        voice="Aria",
        output_format="mp3_22050_32",
        model="eleven_turbo_v2"
    )
    elevenlabs.save(audio, output_filepath)
    print(f"Audio saved to: {output_filepath}")
    
    # Add autoplay functionality
    os_name = platform.system()
    try:
        if os_name == "Windows":
            os.startfile(output_filepath)  # This will use the default media player
        elif os_name == "Linux":
            subprocess.run(['aplay', output_filepath])
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"Error playing audio: {e}")

def text_to_speech_with_gtts(input_text, output_filepath):
    if not input_text:
        raise ValueError("Input text cannot be empty")
        
    language = "en"
    try:
        audioobj = gTTS(
            text=input_text,
            lang=language,
            slow=False
        )
        audioobj.save(output_filepath)
        os_name = platform.system()
        
        if os_name == "Windows":
            os.startfile(output_filepath)  # This will use the default media player
        elif os_name == "Linux":
            subprocess.run(['aplay', output_filepath])
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"Error in text to speech conversion: {e}")
        raise

def text_to_speech_with_elevenlabs(input_text, output_filepath, auto_play=False):
    try:
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        audio = client.generate(
            text=input_text,
            voice="Aria",
            output_format="mp3_22050_32",
            model="eleven_turbo_v2"
        )
        elevenlabs.save(audio, output_filepath)
        
        if auto_play:
            os_name = platform.system()
            if os_name == "Windows":
                os.startfile(output_filepath)
            elif os_name == "Linux":
                subprocess.run(['aplay', output_filepath])
            else:
                raise OSError("Unsupported operating system")
                
        return output_filepath
        
    except Exception as e:
        print(f"Error in text to speech conversion: {e}")
        raise

# Test the functions
if __name__ == "__main__":
    # Test gTTS
    input_text = "Hi this is Abrar!"
    text_to_speech_with_gtts_old(input_text=input_text, output_filepath="gtts_testing.mp3")
    
    # Test ElevenLabs
    text_to_speech_with_elevenlabs_old(input_text=input_text, output_filepath="elevenlabs_testing.mp3")
    
   