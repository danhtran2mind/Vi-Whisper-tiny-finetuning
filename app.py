import gradio as gr
import librosa
import torch
import numpy as np
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
import os

# Load model and processor (assuming Whisper model for transcription)
model_name = "danhtran2mind/Vi-Whisper-tiny-finetuning"  # Replace with your model if different
processor = AutoProcessor.from_pretrained(model_name)
model = AutoModelForSpeechSeq2Seq.from_pretrained(model_name)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def transcribe_audio(audio_file):
    try:
        # Load audio file
        audio, sr = librosa.load(audio_file, sr=16000)
        
        # Preprocess audio
        inputs = processor(audio, sampling_rate=16000, return_tensors="pt").to(device)
        
        # Perform inference
        with torch.no_grad():
            generated_ids = model.generate(
                inputs["input_features"],
                max_length=448,
            )
        
        # Decode the output
        transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        return f"Transcription:\n{transcription}"
    except Exception as e:
        return f"Error during transcription: {str(e)}"

def load_examples(directory):
    """Load all audio files from the specified directory as Gradio examples."""
    supported_extensions = ('.mp3', '.wav')  # Add other extensions if needed
    examples = []
    if os.path.exists(directory):
        for file in os.listdir(directory):
            if file.lower().endswith(supported_extensions):
                examples.append([os.path.join(directory, file)])
    return examples

# Create Gradio interface
iface = gr.Interface(
    fn=transcribe_audio,
    inputs=gr.Audio(type="filepath", label="Upload Audio File"),
    outputs=gr.Textbox(label="Transcription Result", lines=5),
    title="Vietnamese Whisper-tiny finetuning",
    description="Upload an audio file (e.g., WAV, MP3) to transcribe its content using a speech-to-text model.",
    examples=load_examples("assets/Vi-Whisper-tiny-finetuning")
)

# Launch the app
if __name__ == "__main__":
    iface.launch()