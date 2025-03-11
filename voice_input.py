import whisper
import sounddevice as sd
import soundfile as sf  # <-- Import soundfile
import numpy as np
import speech_recognition as sr
import os
import warnings
import torch
import re

print(torch.__version__)

#DOWNLOAD FFMPEG ON WINDOWS
# Suppress Whisper and PyTorch warnings
warnings.filterwarnings("ignore")
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "garbage_collection_threshold:0.9,max_split_size_mb:512"
os.environ["TORCH_HOME"] = "/dev/null"
#torch._C._init_names()

# Load Whisper model
model = whisper.load_model("base")  # Choose from 'tiny', 'base', 'small', 'medium', 'large'

def record_audio(duration=5, sample_rate=16000):
    """Records audio from the default microphone"""
    audio = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    return np.squeeze(audio)

def transcribe_audio():
    print("Listening...")
    while(True):
        """Records and transcribes audio using Whisper"""
        audio_data = record_audio()

        # Save as a WAV file (Fixed issue!)
        temp_wav = "temp_audio.wav"
        sf.write(temp_wav, audio_data, 16000)  # <-- Use soundfile to save the file

        # Transcribe with Whisper
        result = model.transcribe(temp_wav)
        if result["text"] != "":
            return result["text"].lower().strip(".").strip(" ")



# # Example usage
if __name__ == "__main__":
    print("Say your move:")
    move = transcribe_audio()
    print(f"You said: {move}")
