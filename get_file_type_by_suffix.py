from pathlib import Path


def get_file_type_by_suffix(file_path: str) -> str:
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv']
    audio_extensions = ['.mp3', '.wav', '.aac', '.flac', '.ogg']

    file_extension = Path(file_path).suffix

    if file_extension in video_extensions:
        return 'video'
    elif file_extension in audio_extensions:
        return 'audio'
    else:
        raise Exception(f"Unsupported file type with extension: {file_extension}")
