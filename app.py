import streamlit as st
import sounddevice as sd
import soundfile as sf
from io import BytesIO

# App configuration
st.set_page_config(page_title="Vent", layout="wide")

# Sidebar
st.sidebar.title("Vent")
st.sidebar.write("Record and playback your project explanations.")

# Main page
st.title("Vent")
st.write("Easily record yourself explaining your projects and play them back.")

# Layout
col1, col2 = st.columns(2)

# Variables to manage state
if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = None

if "recording" not in st.session_state:
    st.session_state.recording = False

# Left column: Recording functionality
with col1:
    st.subheader("Record Your Explanation")
    
    if st.session_state.recording:
        st.write("Recording in progress...")
    
    duration = st.number_input("Recording Duration (seconds):", min_value=1, max_value=600, value=10)

    if st.button("Start Recording"):
        st.session_state.recording = True
        st.write("Recording...")
        fs = 44100  # Sampling frequency
        # try:
        audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype='int16')
        sd.wait()  # Wait for recording to complete
        st.session_state.audio_buffer = BytesIO()
        sf.write(st.session_state.audio_buffer, audio_data, fs, format='WAV')
        st.session_state.audio_buffer.seek(0)
        st.session_state.recording = False
        st.success("Recording completed.")
        # except Exception as e:
        #     st.error(f"An error occurred while recording: {e}")

# Right column: Playback functionality
with col2:
    st.subheader("Playback Your Explanation")

    if st.session_state.audio_buffer is not None:
        st.audio(st.session_state.audio_buffer, format="audio/wav")
    else:
        st.write("No recording available to play back.")
