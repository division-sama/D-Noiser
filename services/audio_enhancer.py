from __future__ import annotations

from pathlib import Path
from typing import Any

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
    """Application service around DeepFilterNet.

    The model is loaded once per application process and then reused for every
    file in a batch. DeepFilterNet's Python API handles the resampling needed
    for the model's 48 kHz processing pipeline.
    """

    def __init__(self) -> None:
        self._model = None
        self._df_state = None
        self._device = None

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def _load_model(self) -> None:
        if self._model is not None:
            return

        from df.enhance import init_df

        self._model, self._df_state, self._device = init_df()

    def enhance_file(self, input_path: Path, output_path: Path) -> dict[str, Any]:
        """Enhance one audio file and write a WAV result."""
        from df.enhance import enhance, load_audio, save_audio

        self._load_model()

        output_path.parent.mkdir(parents=True, exist_ok=True)

        audio, _ = load_audio(str(input_path), sr=self._df_state.sr())
        enhanced = enhance(self._model, self._df_state, audio)
        save_audio(str(output_path), enhanced, self._df_state.sr())

        return {
            "input": str(input_path),
            "output": str(output_path),
        }

    def enhance_single_file(
        self,
        input_file: str,
        output_file: str,
        *,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        """Enhance exactly one audio file to the exact output path supplied."""
        input_path = Path(input_file).expanduser().resolve()
        output_path = Path(output_file).expanduser().resolve()

        if not input_path.exists():
            raise ValueError(f"Input file does not exist: {input_path}")
        if not input_path.is_file():
            raise ValueError(f"Input path is not a file: {input_path}")
        if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported input format: {input_path.suffix or '[no extension]'}"
            )
        if output_path.suffix.lower() != ".wav":
            raise ValueError(
                "DeepFilterNet output must be a WAV file. "
                "Please use an output filename ending in .wav."
            )
        if output_path.exists() and not overwrite:
            raise ValueError(
                f"Output file already exists: {output_path}. "
                "Enable overwrite to replace it."
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            result = self.enhance_file(input_path, output_path)
            result["status"] = "done"
            return {
                "ok": True,
                "input": str(input_path),
                "output": str(output_path),
                "result": result,
            }
        except Exception as exc:
            return {
                "ok": False,
                "input": str(input_path),
                "output": str(output_path),
                "error": str(exc),
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
            raise ValueError(f"Folder does not exist: {source}")
        if not source.is_dir():
            raise ValueError(f"Path is not a folder: {source}")

        # The result is a sibling folder: /recordings -> /recordings_enhanced
        output_dir = source.parent / f"{source.name}_enhanced"
        output_dir.mkdir(parents=True, exist_ok=True)

        iterator = source.rglob("*") if recursive else source.glob("*")
        files = [
            p for p in iterator
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

        # Never process a previous output directory if it happens to be nested.
        files = [p for p in files if output_dir not in p.parents]

        results: list[dict[str, Any]] = []
        errors: list[dict[str, str]] = []

        for input_path in sorted(files):
            # Always emit WAV. This makes output deterministic and avoids
            # codec-specific issues when writing enhanced audio.
            if recursive:
                relative_parent = input_path.parent.relative_to(source)
                target_dir = output_dir / relative_parent
            else:
                target_dir = output_dir

            output_path = target_dir / f"{input_path.stem}_enhanced.wav"

            if output_path.exists() and not overwrite:
                results.append({
                    "input": str(input_path),
                    "output": str(output_path),
                    "status": "skipped",
                })
                continue

            try:
                item = self.enhance_file(input_path, output_path)
                item["status"] = "done"
                results.append(item)
            except Exception as exc:
                errors.append({
                    "input": str(input_path),
                    "error": str(exc),
                })

        return {
            "ok": len(errors) == 0,
            "source_folder": str(source),
            "output_folder": str(output_dir),
            "total": len(files),
            "processed": sum(1 for x in results if x["status"] == "done"),
            "skipped": sum(1 for x in results if x["status"] == "skipped"),
            "failed": len(errors),
            "results": results,
            "errors": errors,
        }
