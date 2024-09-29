# Video Transcription App

This Streamlit-based application provides an easy-to-use interface for transcribing video files using OpenAI's Whisper API. It offers features such as test mode, cost estimation, and generates transcriptions with timestamps in a CSV format.

## Features

- Transcribe video files of any length
- Test mode for processing only the first 10 minutes
- Cost estimation before processing
- Timestamps in minutes:seconds format
- Easy-to-use Streamlit interface
- Output in CSV format for easy editing and further processing

## Requirements

- Python 3.7+
- Streamlit
- OpenAI Python Client
- MoviePy
- PyDub
- python-dotenv

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/miekki-jerry/transtamps.git
   cd transtamps
   ```

2. Install the required packages:
   ```
   pip install streamlit openai moviepy pydub python-dotenv
   ```

3. Create a `.env` file in the root directory of the project and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Usage

1. Ensure your `.env` file is set up with your OpenAI API key.

2. Run the Streamlit app:
   ```
   streamlit run transtamps.py
   ```

3. Open your web browser and go to the URL provided by Streamlit (usually `http://localhost:8501`).

4. Enter the full path to your video file in the text input field.

5. (Optional) Check the "Test mode" box if you want to process only the first 10 minutes of the video.

6. Review the estimated cost for processing.

7. Click the "Process Video" button to start the transcription.

8. Once the transcription is complete, you can download the CSV file containing the transcription with timestamps.

## How It Works

1. The app loads the API key from the `.env` file.
2. The app extracts the audio from the video file.
3. The audio is split into chunks to comply with Whisper API's file size limits.
4. Each chunk is sent to the Whisper API for transcription.
5. The transcriptions are combined and processed to create a single CSV file with continuous timestamps.

## Limitations

- The app requires an OpenAI API key with access to the Whisper model.
- Processing long videos can be time-consuming and may incur significant API costs.
- The accuracy of the transcription depends on the Whisper model and the quality of the audio in the video.


## Acknowledgments

- OpenAI for providing the Whisper API
- Streamlit for the excellent web app framework
- MoviePy and PyDub for audio processing capabilities