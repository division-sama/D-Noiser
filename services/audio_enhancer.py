from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
import torch


SUPPORTED_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".flac",
    ".ogg",
    ".opus",
    ".aac",
    ".wma",
}


class AudioEnhancer:
    """Application service around DeepFilterNet."""

    def __init__(self) -> None:
        self._model = None
        self._df_state = None

    def _load_model(self) -> None:
        if self._model is not None:
            return

        from df.enhance import init_df

        self._model, self._df_state, _ = init_df()

    def _convert_to_wav(
        self,
        input_path: Path,
        output_path: Path,
    ) -> None:
        """Convert input audio to mono 48 kHz PCM WAV using FFmpeg."""

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(input_path),
                "-ar",
                str(self._df_state.sr()),
                "-ac",
                "1",
                "-c:a",
                "pcm_s16le",
                str(output_path),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )

    def _load_wav(self, wav_path: Path) -> torch.Tensor:
        """Load WAV using soundfile instead of torchaudio."""

        audio, sample_rate = sf.read(
            str(wav_path),
            dtype="float32",
        )

        if sample_rate != self._df_state.sr():
            raise ValueError(
                f"Expected {self._df_state.sr()} Hz audio, "
                f"got {sample_rate} Hz"
            )

        # If soundfile returns stereo/multi-channel,
        # convert to mono.
        if audio.ndim == 2:
            audio = np.mean(audio, axis=1)

        # soundfile gives us:
        # (samples,)
        #
        # DeepFilterNet expects:
        # (channels, samples)
        audio = torch.from_numpy(audio).unsqueeze(0)

        return audio

    def enhance_file(
        self,
        input_path: Path,
        output_path: Path,
    ) -> dict[str, Any]:

        from df.enhance import enhance, save_audio

        self._load_model()

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_wav = Path(temp_dir) / "input.wav"

            # MP3/M4A/etc → 48 kHz mono WAV
            self._convert_to_wav(
                input_path,
                temp_wav,
            )

            # WAV → torch tensor
            audio = self._load_wav(temp_wav)

            # Run DeepFilterNet.
            enhanced = enhance(
                self._model,
                self._df_state,
                audio,
            )

            # Save enhanced audio.
            save_audio(
                str(output_path),
                enhanced,
                self._df_state.sr(),
            )

        return {
            "input": str(input_path),
            "output": str(output_path),
        }

    def enhance_folder(
        self,
        folder_path: str,
        *,
        recursive: bool = False,
        overwrite: bool = False,
    ) -> dict[str, Any]:

        source = Path(folder_path).expanduser().resolve()

        if not source.exists():
            raise ValueError(
                f"Folder does not exist: {source}"
            )

        if not source.is_dir():
            raise ValueError(
                f"Path is not a folder: {source}"
            )

        output_dir = (
            source.parent /
            f"{source.name}_enhanced"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        iterator = (
            source.rglob("*")
            if recursive
            else source.glob("*")
        )

        files = [
            p
            for p in iterator
            if p.is_file()
            and p.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

        results: list[dict[str, Any]] = []
        errors: list[dict[str, str]] = []

        for input_path in sorted(files):

            if recursive:
                relative_parent = (
                    input_path.parent.relative_to(source)
                )

                target_dir = (
                    output_dir / relative_parent
                )
            else:
                target_dir = output_dir

            output_path = (
                target_dir /
                f"{input_path.stem}_enhanced.wav"
            )

            if output_path.exists() and not overwrite:
                results.append(
                    {
                        "input": str(input_path),
                        "output": str(output_path),
                        "status": "skipped",
                    }
                )
                continue

            try:
                result = self.enhance_file(
                    input_path,
                    output_path,
                )

                result["status"] = "done"
                results.append(result)

            except Exception as exc:
                errors.append(
                    {
                        "input": str(input_path),
                        "error": str(exc),
                    }
                )

        return {
            "ok": len(errors) == 0,
            "source_folder": str(source),
            "output_folder": str(output_dir),
            "total": len(files),
            "processed": sum(
                1
                for item in results
                if item["status"] == "done"
            ),
            "skipped": sum(
                1
                for item in results
                if item["status"] == "skipped"
            ),
            "failed": len(errors),
            "results": results,
            "errors": errors,
        }