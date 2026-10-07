import os
import ffmpeg


def get_duration(filepath):
    """Retourne la durée d'un fichier média via ffmpeg probe."""
    try:
        probe = ffmpeg.probe(filepath)
        return float(probe["format"]["duration"])
    except Exception:
        return 0.0


def escape_path_for_filter(path):
    """Échappe un chemin de fichier pour les filtres FFmpeg."""
    escaped = str(path).replace("\\", "/")
    escaped = escaped.replace(":", "\\:")
    escaped = escaped.replace("'", r"\'")
    return escaped


def escape_drawtext(text):
    """Échappe les caractères sensibles pour le filtre drawtext."""
    return (
        str(text)
        .replace("\\", r"\\")
        .replace(":", r"\:")
        .replace("'", r"\'")
        .replace(",", r"\,")
    )


def ensure_pair(image_pair):
    """Garantit qu'on obtient un tuple (path_a, path_b)."""
    if isinstance(image_pair, dict):
        path_a = image_pair.get("a")
        return path_a, image_pair.get("b", path_a)

    if isinstance(image_pair, (list, tuple)) and len(image_pair) >= 2:
        return image_pair[0], image_pair[1]

    if image_pair:
        return str(image_pair), str(image_pair)

    return None, None


def is_video_file(path):
    """Vérifie si le fichier est une vidéo."""
    return str(path).lower().endswith(
        (".mp4", ".mov", ".webm", ".avi", ".mkv", ".m4v")
    )


def cleanup_temp_files(filepaths, keep=None):
    """Supprime les fichiers temporaires proprement."""
    for filepath in filepaths:
        if not filepath or filepath == keep:
            continue
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass


def pick_dominant_mood(script_data):
    """Détermine le mood le plus fréquent parmi les scènes du script."""
    from collections import Counter
    moods = [
        str(s.get("mood", "")).strip().lower()
        for s in script_data
        if s.get("mood")
    ]
    if not moods:
        return "intriguing"
    return Counter(moods).most_common(1)[0][0]
