# Local DeepFilterNet Audio Enhancer

A small local FastAPI + Jinja2 application for batch-enhancing audio with DeepFilterNet.

## What it does

1. Enter a local folder path in the web UI.
2. The backend scans that folder for supported audio files.
3. DeepFilterNet is loaded once and reused for the batch.
4. Each file is enhanced locally.
5. Results are written as WAV files into a sibling folder named `<source>_enhanced`.

Example:

```text
Recordings/
  interview.mp3
  meeting.wav

Recordings_enhanced/
  interview_enhanced.wav
  meeting_enhanced.wav
```

With **Include subfolders**, the relative directory structure is preserved.

## Install

Use Python 3.10/3.11 in a virtual environment if possible.

```bash
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
# .venv\\Scripts\\activate    # Windows

python -m pip install --upgrade pip
pip install -r requirements.txt
```

DeepFilterNet's Python implementation is documented by the upstream project. It exposes `init_df()`, `load_audio()`, `enhance()`, and `save_audio()` for programmatic use.

## Run

```bash
uvicorn app:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

## Important: first run

The first enhancement initializes/downloads the model used by DeepFilterNet. Subsequent files in the same process reuse the loaded model.

## Audio formats

The service accepts common formats such as WAV, MP3, M4A, FLAC, OGG, OPUS, AAC and WMA, subject to the audio decoder available to the installed DeepFilterNet/torchaudio stack. Output is always WAV.

If your environment has trouble decoding a particular format, convert it to WAV first or add FFmpeg/torchaudio support for that format.

## Architecture

```text
Browser
   |
   | folder path
   v
FastAPI
   |
   v
AudioEnhancer service
   |
   +--> scan folder
   |
   +--> load DeepFilterNet once
   |
   +--> enhance each file
   |
   v
<folder>_enhanced/*.wav
```

The service layer intentionally contains the DeepFilterNet logic so the API/UI can later be replaced without changing the enhancement code.
