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
    
    # Get a list of available input devices
    device_list = [
        dev['name'] for dev in sd.query_devices() if dev['max_input_channels'] > 0
    ]
    selected_device = st.selectbox('Select Input Device', device_list)

    if st.session_state.recording:
        st.write("Recording in progress...")
    
    duration = st.number_input("Recording Duration (seconds):", min_value=1, max_value=600, value=600)

    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("Start Recording"):
            st.session_state.recording = True
            fs = 44100
            st.session_state.audio_data = sd.rec(
                int(duration * fs),
                samplerate=fs,
                channels=2,
                dtype='int16',
                device=device_list.index(selected_device)
            )
            st.write("Recording started...")

    with col_stop:
        if st.button("Stop Recording"):
            sd.stop()
            sd.wait()
            fs = 44100
            st.session_state.audio_buffer = BytesIO()
            sf.write(st.session_state.audio_buffer, st.session_state.audio_data, fs, format='WAV')
            st.session_state.audio_buffer.seek(0)
            st.session_state.recording = False
            st.success("Recording completed.")

# Right column: Playback functionality
with col2:
    st.subheader("Playback Your Explanation")

    if st.session_state.audio_buffer is not None:
        st.audio(st.session_state.audio_buffer, format="audio/wav")
    else:
        st.write("No recording available to play back.")
