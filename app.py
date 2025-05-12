# if you dont use pipenv uncomment the following:
from dotenv import load_dotenv
load_dotenv()

import os
import gradio as gr
import logging

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import record_audio, transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts, text_to_speech_with_elevenlabs

# Load env variables (local dev only; Hugging Face uses os.environ directly)
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load API Keys with validation
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

# Validate API keys
if not GROQ_API_KEY:
    logging.error("GROQ_API_KEY not found in environment variables")
if not ELEVENLABS_API_KEY:
    logging.error("ELEVENLABS_API_KEY not found in environment variables")

def process_inputs(audio_filepath, image_filepath):
    try:
        speech_to_text_output = ""
        if audio_filepath:
            if not GROQ_API_KEY:
                return "GROQ API Key not configured", "API Key Error", None
            speech_to_text_output = transcribe_with_groq(
                stt_model="whisper-large-v3",
                audio_filepath=audio_filepath,
                GROQ_API_KEY=GROQ_API_KEY
            )

        if image_filepath:
            doctor_response = analyze_image_with_query(
                query=system_prompt + speech_to_text_output,
                encoded_image=encode_image(image_filepath),
                model="meta-llama/llama-4-scout-17b-16e-instruct"
            )
        else:
            doctor_response = "Please provide an image for me to analyze"

        if not ELEVENLABS_API_KEY:
            return speech_to_text_output, doctor_response, "ElevenLabs API Key not configured"

        output_filepath = "doctor_response.mp3"
        text_to_speech_with_elevenlabs(
            input_text=doctor_response,
            output_filepath=output_filepath,
            auto_play=False,
            api_key=ELEVENLABS_API_KEY
        )

        return speech_to_text_output, doctor_response, output_filepath

    except Exception as e:
        logging.error(f"Error in process_inputs: {str(e)}")
        return str(e), "An error occurred", None

system_prompt = """You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""

# Create the interface
# Custom CSS for medical theme
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

.gradio-container {
    background-color: #f5f8fa;
    font-family: 'Roboto', sans-serif;
}

.doctor-header {
    background: linear-gradient(135deg, #1e4d8c 0%, #2c5282 100%);
    color: white;
    padding: 25px;
    border-radius: 15px;
    margin-bottom: 30px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.doctor-header h1 {
    font-size: 2.5em;
    font-weight: 700;
    margin-bottom: 10px;
}

.doctor-header p {
    font-size: 1.2em;
    font-weight: 300;
    opacity: 0.9;
}

.input-section, .output-section {
    background-color: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    margin: 15px 0;
    border: 1px solid #e1e8ed;
}

.input-section h3, .output-section h3 {
    color: #1e4d8c;
    font-weight: 500;
    margin-bottom: 20px;
    border-bottom: 2px solid #e1e8ed;
    padding-bottom: 10px;
}

button.primary {
    background: #2c5282 !important;
    border: none !important;
    box-shadow: 0 2px 4px rgba(44,82,130,0.2) !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}

button.primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 8px rgba(44,82,130,0.3) !important;
}

.footer-note {
    background-color: #fff3cd;
    border: 1px solid #ffeeba;
    color: #856404;
    padding: 15px;
    border-radius: 10px;
    margin-top: 20px;
    font-size: 0.9em;
}

.textbox textarea {
    border: 1px solid #e1e8ed !important;
    border-radius: 8px !important;
    padding: 12px !important;
    font-family: 'Roboto', sans-serif !important;
}

.audio-input, .image-input {
    border: 2px dashed #e1e8ed;
    border-radius: 10px;
    padding: 20px;
    transition: all 0.3s ease;
}

.audio-input:hover, .image-input:hover {
    border-color: #2c5282;
}
"""

with gr.Blocks(css=custom_css) as iface:
    with gr.Column():
        gr.HTML("""
            <div class="doctor-header">
                <h1>🏥DiagnostiQ-AI Medical Consultation Assistant</h1>
                <p>Advanced Medical Image Analysis & Interactive Voice Consultation System</p>
            </div>
        """)
        
        with gr.Row():
            with gr.Column(elem_classes="input-section"):
                gr.Markdown("### 👤 Patient Input")
                audio_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="🎤 Record Your Symptoms",
                    elem_id="audio-input",
                    elem_classes="audio-input"
                )
                image_input = gr.Image(
                    type="filepath",
                    label="📷 Upload Medical Image",
                    elem_id="image-input",
                    elem_classes="image-input"
                )
                submit_btn = gr.Button("🔍 Get Medical Analysis", variant="primary", size="lg")

            with gr.Column(elem_classes="output-section"):
                gr.Markdown("### 👨‍⚕️ Medical Analysis")
                speech_output = gr.Textbox(
                    label="📝 Transcribed Symptoms",
                    elem_id="speech-output"
                )
                doctor_response = gr.Textbox(
                    label="💬 Doctor's Analysis",
                    elem_id="doctor-response"
                )
                audio_output = gr.Audio(
                    label="🔊 Doctor's Voice Response",
                    elem_id="audio-output"
                )

        gr.Markdown("""
            ### 📋 How to Use
            1. **Record Symptoms**: Click the microphone icon and clearly describe your symptoms
            2. **Upload Image**: Add any relevant medical images for analysis
            3. **Get Analysis**: Click the analysis button for professional medical consultation
            
            <div class="footer-note">
            ⚠️ <strong>Important Notice:</strong> This AI assistant is designed for educational purposes only. 
            For actual medical concerns, please consult with a qualified healthcare professional.
            </div>
        """)

        submit_btn.click(
            fn=process_inputs,
            inputs=[audio_input, image_input],
            outputs=[speech_output, doctor_response, audio_output]
        )

if __name__ == "__main__":
    iface.launch(debug=True)