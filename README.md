# D-Noiser

A simple local audio denoising application powered by **DeepFilterNet3**.

D-Noiser lets you clean up audio files directly on your machine without uploading your recordings to a cloud service.

## Features

* 🎙️ Denoise individual audio files
* 📁 Denoise an entire folder of audio files
* 💾 Choose the exact output location and filename for individual files
* 📂 Automatically create an enhanced output folder when processing a directory
* 🔒 Runs locally — your audio stays on your machine
* ⚡ Uses DeepFilterNet3 for real-time speech enhancement
* 🌐 Simple local web interface built with FastAPI and Jinja2

## How it works

D-Noiser uses DeepFilterNet3 as the underlying speech enhancement model.

For supported audio files, the application:

1. Converts the input audio to the format required by DeepFilterNet.
2. Runs the audio through DeepFilterNet3.
3. Saves the enhanced audio to the location you specify.

For folder processing, D-Noiser automatically creates an `_enhanced` folder next to the original folder.

### Example

```text
Recordings/
├── interview.mp3
├── meeting.wav
└── podcast.mp3

        ↓ D-Noiser

Recordings_enhanced/
├── interview_enhanced.wav
├── meeting_enhanced.wav
└── podcast_enhanced.wav
```

## Requirements

* Python 3.9+
* FFmpeg
* DeepFilterNet3
* PyTorch

## Installation

Clone the repository and create a virtual environment:

```bash
git clone <your-repository-url>
cd D-Noiser

python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Make sure FFmpeg is installed and available on your PATH.

On macOS with Homebrew:

```bash
brew install ffmpeg
```

## Running D-Noiser

Start the FastAPI application:

```bash
uvicorn app:app --reload
```

Then open the local URL shown by Uvicorn in your browser.

## Usage

### Enhance a folder

Select a folder containing audio files.

D-Noiser will process the supported audio files and create:

```text
<original_folder>_enhanced/
```

next to the original folder.

### Enhance a single file

You can also provide:

* The complete input file path
* The complete output file path
* The output filename
* Whether an existing output file should be overwritten

This is useful when you want precise control over where the enhanced recording is saved.

## Supported Audio Formats

D-Noiser currently supports common audio formats including:

```text
.wav
.mp3
.m4a
.flac
.ogg
.opus
.aac
.wma
```

FFmpeg is used to convert input audio into the format required for processing.

## Privacy

D-Noiser is designed to run locally.

Your audio files are processed on your own machine and are not sent to a remote audio-processing service by D-Noiser.

## Credits

D-Noiser uses **DeepFilterNet3**, developed by:

* Hendrik Schröter
* Tobias Rosenkranz
* Alberto N. Escalante-B.
* Andreas Maier

DeepFilterNet is an open-source project released under either the **MIT License** or **Apache License 2.0**, at the user's option.

If you use D-Noiser in academic or research work, please also cite the original DeepFilterNet3 research paper.

### DeepFilterNet3 Citation

```bibtex
@inproceedings{schroeter2023deepfilternet3,
  title = {{DeepFilterNet}: Perceptually Motivated Real-Time Speech Enhancement},
  author = {Schröter, Hendrik and Rosenkranz, Tobias and Escalante-B., Alberto N. and Maier, Andreas},
  booktitle = {INTERSPEECH},
  year = {2023},
}
```

The DeepFilterNet project and its authors deserve credit for the underlying speech enhancement technology. D-Noiser is an independent application built around that technology.

## License

D-Noiser's application code is provided under the license specified in this repository.

DeepFilterNet and its associated components remain subject to their respective original licenses. Please refer to the upstream DeepFilterNet project for the complete license terms.

## Disclaimer

D-Noiser is an independent project and is not affiliated with or endorsed by the DeepFilterNet authors.
