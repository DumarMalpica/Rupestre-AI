"""Transcribe entrevistas de tradición oral con Whisper."""

from pathlib import Path
from core.logger import get_logger

logger = get_logger("corpus.audio_transcriber")


def transcribe(audio_path: str, model_size: str = "medium") -> dict:
    """
    Transcribe un archivo de audio a texto.

    Args:
        audio_path: ruta al archivo .mp3, .wav o .m4a
        model_size: tamaño del modelo Whisper (tiny/base/medium/large)

    Returns:
        Dict con keys: text, language, segments, source
    """
    try:
        import whisper

        logger.info(f"Cargando modelo Whisper ({model_size})...")
        model = whisper.load_model(model_size)

        logger.info(f"Transcribiendo: {audio_path}")
        result = model.transcribe(audio_path, language="es")

        return {
            "text": result["text"],
            "language": result.get("language", "es"),
            "segments": result.get("segments", []),
            "source": Path(audio_path).name,
            "metadata": {
                "source_type": "audio_transcription",
                "file": audio_path,
                "model": model_size,
            },
        }

    except ImportError:
        logger.warning("Whisper no instalado. Instalar con: pip install openai-whisper")
        return {}
    except Exception as e:
        logger.error(f"Error transcribiendo {audio_path}: {e}")
        return {}
