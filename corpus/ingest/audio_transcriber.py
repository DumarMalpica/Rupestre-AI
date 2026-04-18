"""Transcribe entrevistas de tradición oral con faster-whisper."""

from pathlib import Path
from core.logger import get_logger

logger = get_logger("corpus.audio_transcriber")


def transcribe(audio_path: str, model_size: str = "medium") -> dict:
    """
    Transcribe un archivo de audio a texto.

    Args:
        audio_path: ruta al archivo .mp3, .wav o .m4a
        model_size: tamaño del modelo Whisper (tiny/base/medium/large-v3)

    Returns:
        Dict con keys: text, language, segments, source, metadata
    """
    try:
        from faster_whisper import WhisperModel

        logger.info(f"Cargando modelo faster-whisper ({model_size})...")
        model = WhisperModel(model_size, device="cpu", compute_type="int8")

        logger.info(f"Transcribiendo: {audio_path}")
        segments, info = model.transcribe(audio_path, language="es")

        segments_list = [
            {"start": s.start, "end": s.end, "text": s.text} for s in segments
        ]
        full_text = " ".join(s["text"].strip() for s in segments_list)

        return {
            "text": full_text,
            "language": info.language,
            "segments": segments_list,
            "source": Path(audio_path).name,
            "metadata": {
                "source_type": "audio_transcription",
                "file": audio_path,
                "model": model_size,
            },
        }

    except ImportError:
        logger.warning(
            "faster-whisper no instalado. Instalar con: pip install faster-whisper"
        )
        return {}
    except Exception as e:
        logger.error(f"Error transcribiendo {audio_path}: {e}")
        return {}
