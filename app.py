import streamlit as st
from openai import OpenAI
import os
import tempfile
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
import csv
import math
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load other configuration variables
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")
MAX_CHUNK_SIZE_MB = int(os.getenv("MAX_CHUNK_SIZE_MB", 24))
TEST_MODE_DURATION = int(os.getenv("TEST_MODE_DURATION", 600))

def get_video_duration(video_path):
    with VideoFileClip(video_path) as video:
        return video.duration

def extract_audio(video_path, start_time=0, duration=None):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio_file:
        with VideoFileClip(video_path) as video:
            if duration:
                video = video.subclip(start_time, start_time + duration)
            video.audio.write_audiofile(
                temp_audio_file.name,
                codec='mp3',
                bitrate='64k',
                logger=None
            )
        return temp_audio_file.name

def split_audio_by_size(audio_path, max_size_mb=MAX_CHUNK_SIZE_MB):
    audio = AudioSegment.from_file(audio_path)
    chunks = []
    total_duration_ms = len(audio)
    start = 0
    while start < total_duration_ms:
        chunk_duration_ms = 60000  # Start with 1 minute
        while True:
            end = min(start + chunk_duration_ms, total_duration_ms)
            chunk = audio[start:end]
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_chunk:
                chunk.export(temp_chunk.name, format='mp3', bitrate='64k')
                chunk_size_mb = os.path.getsize(temp_chunk.name) / (1024 * 1024)
                if chunk_size_mb <= max_size_mb:
                    chunks.append((temp_chunk.name, start / 1000.0))  # Store start time in seconds
                    break
                else:
                    chunk_duration_ms = int(chunk_duration_ms * 0.9)
                    temp_chunk.close()
                    os.unlink(temp_chunk.name)
                    if chunk_duration_ms < 10000:
                        st.error("Cannot split audio into small enough chunks.")
                        return []
        start += chunk_duration_ms
    return chunks

def transcribe_audio(audio_file, time_offset):
    with open(audio_file, 'rb') as f:
        transcription = client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=f,
            response_format='verbose_json',
            timestamp_granularities=['segment']
        )
    return transcription, time_offset

def format_time(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"

def process_transcription(transcriptions):
    data = []
    for transcription, time_offset in transcriptions:
        for segment in transcription.segments:
            start_time = time_offset + segment.start
            end_time = time_offset + segment.end
            timestamp = f"{format_time(start_time)} - {format_time(end_time)}"
            text = segment.text.strip()
            data.append({'Timestamp': timestamp, 'Text': text})
    return data

def save_to_csv(data, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Timestamp', 'Text']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def estimate_cost(duration_seconds):
    # Whisper pricing: $0.006 / minute
    minutes = math.ceil(duration_seconds / 60)
    estimated_cost = minutes * 0.006
    return estimated_cost

def main():
    st.title("Video Transcription App with Minutes:Seconds Timestamps")

    if not os.getenv("OPENAI_API_KEY"):
        st.error("OpenAI API key not found. Please set it in your .env file.")
        return

    st.write("Enter the full path to your video file below:")
    video_path = st.text_input("Video file path")

    if video_path and os.path.isfile(video_path):
        video_duration = get_video_duration(video_path)
        st.info(f"Video duration: {format_time(video_duration)}")

        test_mode = st.checkbox("Test mode (process only first 10 minutes)")
        if test_mode:
            duration = min(TEST_MODE_DURATION, video_duration)
        else:
            duration = video_duration

        estimated_cost = estimate_cost(duration)
        st.warning(f"Estimated cost for processing: ${estimated_cost:.4f}")

        if st.button("Process Video"):
            with st.spinner("Processing video..."):
                st.info("Extracting and compressing audio from video...")
                audio_file = extract_audio(video_path, start_time=0, duration=duration)

                st.info("Splitting audio into chunks under 25 MB...")
                audio_chunks = split_audio_by_size(audio_file)
                if not audio_chunks:
                    st.error("Failed to split audio into appropriate chunks.")
                    return

                transcriptions = []
                progress_bar = st.progress(0)
                for idx, (chunk, time_offset) in enumerate(audio_chunks):
                    st.info(f"Transcribing chunk {idx+1}/{len(audio_chunks)}...")
                    transcription = transcribe_audio(chunk, time_offset)
                    transcriptions.append(transcription)
                    os.remove(chunk)  # Clean up the chunk file
                    progress_bar.progress((idx + 1) / len(audio_chunks))

                os.remove(audio_file)  # Clean up the extracted audio file

                st.info("Processing transcriptions...")
                data = process_transcription(transcriptions)

                output_csv = 'transcription.csv'
                save_to_csv(data, output_csv)

                st.success("Transcription completed!")
                st.download_button(
                    label="Download Transcription CSV",
                    data=open(output_csv, 'rb'),
                    file_name='transcription.csv',
                    mime='text/csv'
                )
    else:
        st.error("Please provide a valid video file path.")

if __name__ == '__main__':
    main()