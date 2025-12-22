"""
Практическая работа 1. Вариант 12
Анализатор мультимедийных файлов
"""

import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from tinytag import TinyTag
except ImportError:
    print("Ошибка: библиотека tinytag не установлена.")
    print(
        "Убедитесь, что виртуальное окружение активировано "
        "(source venv/bin/activate)"
    )
    print("Затем установите: pip install tinytag")
    print(f"Используемый Python: {sys.executable}")
    sys.exit(1)

try:
    import cv2
except ImportError:
    print("Ошибка: библиотека opencv-python не установлена.")
    print(
        "Убедитесь, что виртуальное окружение активировано "
        "(source venv/bin/activate)"
    )
    print("Затем установите: pip install opencv-python")
    print(f"Используемый Python: {sys.executable}")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("Ошибка: библиотека Pillow не установлена.")
    print(
        "Убедитесь, что виртуальное окружение активировано "
        "(source venv/bin/activate)"
    )
    print("Затем установите: pip install Pillow")
    print(f"Используемый Python: {sys.executable}")
    sys.exit(1)


def format_duration(seconds):
    """Форматирует длительность в читаемый вид"""
    if seconds is None:
        return "Неизвестно"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def get_file_info(file_path):
    """Получает базовую информацию о файле"""
    path = Path(file_path)
    stat = path.stat()

    return {
        "name": path.name,
        "size": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    }


def analyze_audio(file_path):
    """Анализирует аудиофайл"""
    print("\n" + "=" * 60)
    print("АНАЛИЗ АУДИОФАЙЛА")
    print("=" * 60)

    file_info = get_file_info(file_path)
    print(f"Название файла: {file_info['name']}")
    size_mb = file_info['size'] / 1024 / 1024
    print(
        f"Размер файла: {file_info['size']:,} байт "
        f"({size_mb:.2f} МБ)"
    )
    print(f"Дата последнего изменения: {file_info['modified']}")

    try:
        tag = TinyTag.get(file_path)

        if tag is None:
            print("\nОшибка: Не удалось определить формат аудиофайла")
            return

        # Определяем формат по расширению
        ext = Path(file_path).suffix.lower()
        format_map = {
            ".mp3": "MP3",
            ".m4a": "M4A",
            ".mp4": "MP4 (аудио)",
            ".flac": "FLAC",
            ".wav": "WAV",
            ".ogg": "OGG",
            ".wma": "WMA",
            ".aac": "AAC",
        }
        format_name = format_map.get(ext, ext.upper().replace(".", ""))

        print(f"\nФормат: {format_name}")

        # Битрейт
        if tag.bitrate:
            print(f"Битрейт: {tag.bitrate} kbps")

        # Длительность
        if tag.duration:
            print(f"Длительность: {format_duration(tag.duration)}")

        # Дополнительные теги
        if tag.title:
            print(f"Название: {tag.title}")
        if tag.artist:
            print(f"Исполнитель: {tag.artist}")
        if tag.album:
            print(f"Альбом: {tag.album}")
        if tag.year:
            print(f"Год: {tag.year}")
        if tag.genre:
            print(f"Жанр: {tag.genre}")

        # Детальная информация
        print("\n--- Детальная информация ---")
        if tag.channels:
            print(f"Каналы: {tag.channels}")
        if tag.samplerate:
            print(f"Частота дискретизации: {tag.samplerate} Hz")
        if tag.bitrate:
            print(f"Битрейт: {tag.bitrate} kbps")
        if tag.filesize:
            print(f"Размер файла (из метаданных): {tag.filesize:,} байт")

    except (IOError, OSError, ValueError, AttributeError) as e:
        print(f"\nОшибка при анализе аудиофайла: {e}")


def analyze_video(file_path):
    """Анализирует видеофайл"""
    print("\n" + "=" * 60)
    print("АНАЛИЗ ВИДЕОФАЙЛА")
    print("=" * 60)

    file_info = get_file_info(file_path)
    print(f"Название файла: {file_info['name']}")
    size_mb = file_info['size'] / 1024 / 1024
    print(
        f"Размер файла: {file_info['size']:,} байт "
        f"({size_mb:.2f} МБ)"
    )
    print(f"Дата последнего изменения: {file_info['modified']}")

    try:
        # OpenCV для анализа видео
        cap = cv2.VideoCapture(file_path)

        if not cap.isOpened():
            print("\nОшибка: Не удалось открыть видеофайл")
            return

        # Получаем свойства видео
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else None

        # Получаем кодек
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])

        print(f"\nРазрешение: {width} x {height}")
        print(f"Частота кадров: {fps:.2f} fps")
        if duration:
            print(f"Длительность: {format_duration(duration)}")
        print(f"Количество кадров: {frame_count:,}")
        print(f"Кодек: {codec}")

        # Доп информация
        print("\n--- Дополнительная информация ---")
        bitrate = cap.get(cv2.CAP_PROP_BITRATE)
        if bitrate > 0:
            print(f"Битрейт: {bitrate / 1000:.0f} kbps")

        cap.release()

    except (cv2.error, IOError, OSError, ValueError) as e:
        print(f"\nОшибка при анализе видеофайла: {e}")


def analyze_image(file_path):
    """Анализирует изображение"""
    print("\n" + "=" * 60)
    print("АНАЛИЗ ИЗОБРАЖЕНИЯ")
    print("=" * 60)

    file_info = get_file_info(file_path)
    print(f"Название файла: {file_info['name']}")
    size_kb = file_info['size'] / 1024
    print(
        f"Размер файла: {file_info['size']:,} байт "
        f"({size_kb:.2f} КБ)"
    )
    print(f"Дата последнего изменения: {file_info['modified']}")

    try:
        with Image.open(file_path) as img:
            width, height = img.size
            format_name = img.format
            mode = img.mode

            print(f"\nФормат: {format_name}")
            print(f"Разрешение: {width} x {height} пикселей")
            print(f"Цветовой режим: {mode}")

            # Доп информация
            print("\n--- Дополнительная информация ---")
            if hasattr(img, "info"):
                if "dpi" in img.info:
                    dpi = img.info["dpi"]
                    if isinstance(dpi, tuple):
                        print(f"DPI: {dpi[0]} x {dpi[1]}")
                    else:
                        print(f"DPI: {dpi}")

                if "compression" in img.info:
                    print(f"Сжатие: {img.info['compression']}")

            # Информация о цвет каналах
            if mode in ("RGB", "RGBA"):
                channels = len(mode)
                print(f"Количество каналов: {channels}")

    except (IOError, OSError, ValueError, AttributeError) as e:
        print(f"\nОшибка при анализе изображения: {e}")


def detect_file_type(file_path):
    """Определяет тип файла по расширению"""
    path = Path(file_path)
    ext = path.suffix.lower()

    audio_extensions = {
        ".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma", ".mp4"
    }
    video_extensions = {
        ".mp4",
        ".avi",
        ".mkv",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v",
        ".mpg",
        ".mpeg",
    }
    image_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".tif",
        ".webp",
        ".svg",
    }

    if ext in audio_extensions:
        # MP4 может быть и аудио, и видео - проверяем содержимое
        if ext == ".mp4":
            try:
                # Пытаемся открыть как видео
                cap = cv2.VideoCapture(file_path)
                if cap.isOpened():
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    cap.release()
                    if width > 0 and height > 0:
                        return "video"
            except (cv2.error, ValueError, AttributeError):
                pass
        return "audio"
    if ext in video_extensions:
        return "video"
    if ext in image_extensions:
        return "image"
    return "unknown"


def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print("Использование: python multimedia_analyzer.py <путь_к_файлу>")
        print("\nПримеры:")
        print("  python multimedia_analyzer.py audio.mp3")
        print("  python multimedia_analyzer.py video.mp4")
        print("  python multimedia_analyzer.py image.jpg")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Ошибка: Файл '{file_path}' не найден")
        sys.exit(1)

    file_type = detect_file_type(file_path)

    if file_type == "audio":
        analyze_audio(file_path)
    elif file_type == "video":
        analyze_video(file_path)
    elif file_type == "image":
        analyze_image(file_path)
    else:
        print("Ошибка: Неизвестный тип файла или формат не поддерживается")
        print("Поддерживаемые форматы:")
        print("  Аудио: MP3, WAV, FLAC, M4A, AAC, OGG, WMA")
        print("  Видео: MP4, AVI, MKV, MOV, WMV, FLV, WEBM, M4V, MPG, MPEG")
        print("  Изображения: JPG, JPEG, PNG, GIF, BMP, TIFF, WEBP")
        sys.exit(1)


if __name__ == "__main__":
    main()
