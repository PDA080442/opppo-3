"""
Практическая работа 1. Вариант 12
Анализатор мультимедийных файлов

Программа обрабатывает файл с командами:
- ADD <путь_к_файлу> - добавляет мультимедийный файл в контейнер
- REM <условие> - удаляет файлы по условию
- PRINT - выводит содержимое контейнера
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional

try:
    from tinytag import TinyTag
except ImportError:
    print("Ошибка: библиотека tinytag не установлена.")
    print("venv не активировано (source venv/bin/activate)")
    print("Затем установите: pip install tinytag")
    print(f"Используемый Python: {sys.executable}")
    sys.exit(1)

try:
    import cv2
except ImportError:
    print("Ошибка: библиотека opencv-python не установлена.")
    print("venv не активировано (source venv/bin/activate)")
    print("Затем установите: pip install opencv-python")
    print(f"Используемый Python: {sys.executable}")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("Ошибка: библиотека Pillow не установлена.")
    print("venv не активировано (source venv/bin/activate)")
    print("Затем установите: pip install Pillow")
    print(f"Используемый Python: {sys.executable}")
    sys.exit(1)


class MultimediaFile:
    """Базовый класс для мультимедийных файлов"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.path = Path(file_path)
        if not self.path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        stat = self.path.stat()
        self.name = self.path.name
        self.size = stat.st_size
        self.modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        self.file_type = self._detect_type()

    def _detect_type(self) -> str:
        """Определяет тип файла"""
        ext = self.path.suffix.lower()
        audio_ext = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma"}
        video_ext = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg"}
        image_ext = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp"}
        
        if ext in audio_ext:
            return "audio"
        elif ext in video_ext:
            return "video"
        elif ext in image_ext:
            return "image"
        else:
            return "unknown"

    def __str__(self) -> str:
        return f"{self.name} ({self.file_type})"

    def __repr__(self) -> str:
        return f"MultimediaFile('{self.file_path}')"


class AudioFile(MultimediaFile):
    """Класс для аудиофайлов"""

    def __init__(self, file_path: str):
        super().__init__(file_path)
        if self.file_type != "audio":
            raise ValueError(f"Файл {file_path} не является аудиофайлом")
        
        self._load_metadata()

    def _load_metadata(self):
        """Загружает метаданные аудиофайла"""
        try:
            tag = TinyTag.get(self.file_path)
            self.bitrate = tag.bitrate if tag.bitrate else None
            self.duration = tag.duration if tag.duration else None
            self.channels = tag.channels if tag.channels else None
            self.samplerate = tag.samplerate if tag.samplerate else None
            self.title = tag.title if tag.title else None
            self.artist = tag.artist if tag.artist else None
        except Exception as e:
            self.bitrate = None
            self.duration = None
            self.channels = None
            self.samplerate = None
            self.title = None
            self.artist = None

    def __str__(self) -> str:
        duration_str = f"{int(self.duration // 60)}:{int(self.duration % 60):02d}" if self.duration else "Неизвестно"
        bitrate_str = f"{self.bitrate} kbps" if self.bitrate else "Неизвестно"
        return (
            f"Аудио: {self.name} | "
            f"Длительность: {duration_str} | "
            f"Битрейт: {bitrate_str} | "
            f"Размер: {self.size / 1024 / 1024:.2f} МБ | "
            f"Изменен: {self.modified}"
        )


class VideoFile(MultimediaFile):
    """Класс для видеофайлов"""

    def __init__(self, file_path: str):
        super().__init__(file_path)
        if self.file_type != "video":
            # Проверяем, может быть это MP4 с видео
            if self.path.suffix.lower() == ".mp4":
                try:
                    cap = cv2.VideoCapture(self.file_path)
                    if cap.isOpened():
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        cap.release()
                        if width > 0 and height > 0:
                            self.file_type = "video"
                        else:
                            raise ValueError(f"Файл {file_path} не является видеофайлом")
                    else:
                        raise ValueError(f"Файл {file_path} не является видеофайлом")
                except:
                    raise ValueError(f"Файл {file_path} не является видеофайлом")
            else:
                raise ValueError(f"Файл {file_path} не является видеофайлом")
        
        self._load_metadata()

    def _load_metadata(self):
        """Загружает метаданные видеофайла"""
        try:
            cap = cv2.VideoCapture(self.file_path)
            if not cap.isOpened():
                raise ValueError("Не удалось открыть видеофайл")
            
            self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.duration = frame_count / self.fps if self.fps > 0 else None
            self.frame_count = frame_count
            
            fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
            self.codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
            
            bitrate = cap.get(cv2.CAP_PROP_BITRATE)
            self.bitrate = bitrate / 1000 if bitrate > 0 else None
            
            cap.release()
        except Exception as e:
            self.width = None
            self.height = None
            self.fps = None
            self.duration = None
            self.frame_count = None
            self.codec = None
            self.bitrate = None

    def __str__(self) -> str:
        resolution = f"{self.width}x{self.height}" if self.width and self.height else "Неизвестно"
        fps_str = f"{self.fps:.2f} fps" if self.fps else "Неизвестно"
        duration_str = f"{int(self.duration // 60)}:{int(self.duration % 60):02d}" if self.duration else "Неизвестно"
        return (
            f"Видео: {self.name} | "
            f"Разрешение: {resolution} | "
            f"Частота кадров: {fps_str} | "
            f"Длительность: {duration_str} | "
            f"Размер: {self.size / 1024 / 1024:.2f} МБ | "
            f"Изменен: {self.modified}"
        )


class ImageFile(MultimediaFile):
    """Класс для изображений"""

    def __init__(self, file_path: str):
        super().__init__(file_path)
        if self.file_type != "image":
            raise ValueError(f"Файл {file_path} не является изображением")
        
        self._load_metadata()

    def _load_metadata(self):
        """Загружает метаданные изображения"""
        try:
            with Image.open(self.file_path) as img:
                self.width, self.height = img.size
                self.format = img.format
                self.mode = img.mode
        except Exception as e:
            self.width = None
            self.height = None
            self.format = None
            self.mode = None

    def __str__(self) -> str:
        resolution = f"{self.width}x{self.height}" if self.width and self.height else "Неизвестно"
        format_str = self.format if self.format else "Неизвестно"
        return (
            f"Изображение: {self.name} | "
            f"Разрешение: {resolution} | "
            f"Формат: {format_str} | "
            f"Размер: {self.size / 1024:.2f} КБ | "
            f"Изменен: {self.modified}"
        )


class MultimediaContainer:
    """Контейнер для хранения мультимедийных файлов"""

    def __init__(self):
        self.files: List[MultimediaFile] = []

    def add(self, file_path: str) -> bool:
        """Добавляет файл в контейнер"""
        try:
            path = Path(file_path)
            ext = path.suffix.lower()
            
            # Определяем тип файла
            audio_ext = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma"}
            video_ext = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg"}
            image_ext = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp"}
            
            if ext in audio_ext:
                file_obj = AudioFile(file_path)
            elif ext in video_ext or (ext == ".mp4" and self._is_video(file_path)):
                file_obj = VideoFile(file_path)
            elif ext in image_ext:
                file_obj = ImageFile(file_path)
            else:
                print(f"Ошибка: Неподдерживаемый формат файла: {file_path}")
                return False
            
            self.files.append(file_obj)
            print(f"Добавлен: {file_obj.name}")
            return True
        except Exception as e:
            print(f"Ошибка при добавлении файла {file_path}: {e}")
            return False

    def _is_video(self, file_path: str) -> bool:
        """Проверяет, является ли MP4 файл видео"""
        try:
            cap = cv2.VideoCapture(file_path)
            if cap.isOpened():
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()
                return width > 0 and height > 0
            return False
        except:
            return False

    def remove(self, condition: str) -> int:
        """Удаляет файлы по условию"""
        removed_count = 0
        condition_lower = condition.lower()
        
        # Парсим условие
        # Примеры: "type == audio", "size > 1000000", "name contains test"
        
        if "type" in condition_lower:
            # Условие по типу: "type == audio", "type == video", "type == image"
            match = re.search(r'type\s*==\s*(\w+)', condition_lower)
            if match:
                target_type = match.group(1)
                original_count = len(self.files)
                self.files = [f for f in self.files if f.file_type != target_type]
                removed_count = original_count - len(self.files)
                return removed_count
        
        if "size" in condition_lower:
            # Условие по размеру: "size > 1000000", "size < 5000000"
            match = re.search(r'size\s*([><=]+)\s*(\d+)', condition_lower)
            if match:
                op = match.group(1)
                size_val = int(match.group(2))
                original_count = len(self.files)
                
                if ">" in op:
                    self.files = [f for f in self.files if f.size <= size_val]
                elif "<" in op:
                    self.files = [f for f in self.files if f.size >= size_val]
                elif "==" in op or "=" in op:
                    self.files = [f for f in self.files if f.size != size_val]
                
                removed_count = original_count - len(self.files)
                return removed_count
        
        if "name" in condition_lower and "contains" in condition_lower:
            # Условие по имени: "name contains test"
            match = re.search(r'name\s+contains\s+["\']?(\w+)["\']?', condition_lower)
            if match:
                search_str = match.group(1)
                original_count = len(self.files)
                self.files = [f for f in self.files if search_str.lower() not in f.name.lower()]
                removed_count = original_count - len(self.files)
                return removed_count
        
        # Если условие не распознано, пытаемся удалить по имени файла
        if os.path.exists(condition):
            original_count = len(self.files)
            self.files = [f for f in self.files if f.file_path != condition]
            removed_count = original_count - len(self.files)
            return removed_count
        
        print(f"Ошибка: Не удалось распознать условие: {condition}")
        return 0

    def print_all(self):
        """Выводит все файлы в контейнере"""
        if not self.files:
            print("Контейнер пуст")
            return
        
        print(f"\n{'='*80}")
        print(f"Содержимое контейнера (всего файлов: {len(self.files)})")
        print(f"{'='*80}")
        
        for i, file_obj in enumerate(self.files, 1):
            print(f"{i}. {file_obj}")
        
        print(f"{'='*80}\n")


def process_commands(command_file: str):
    """Обрабатывает команды из файла"""
    container = MultimediaContainer()
    
    if not os.path.exists(command_file):
        print(f"Ошибка: Файл с командами '{command_file}' не найден")
        return
    
    with open(command_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        # Игнорируем пустые строки и комментарии
        if not line or line.startswith('#'):
            continue
        
        # Парсим команду
        parts = line.split(None, 1)
        if not parts:
            continue
        
        command = parts[0].upper()
        
        # Обрабатываем только известные команды
        if command == "ADD":
            if len(parts) < 2:
                print(f"Строка {line_num}: Ошибка - команда ADD требует аргумент")
                continue
            file_path = parts[1].strip()
            container.add(file_path)
        
        elif command == "REM":
            if len(parts) < 2:
                print(f"Строка {line_num}: Ошибка - команда REM требует аргумент")
                continue
            condition = parts[1].strip()
            removed = container.remove(condition)
            print(f"Удалено файлов: {removed}")
        
        elif command == "PRINT":
            container.print_all()
        
        # Игнорируем строки, которые не являются командами (комментарии, описания)
        elif not any(cmd in line.upper() for cmd in ["ADD", "REM", "PRINT"]):
            # Это не команда, просто пропускаем
            continue


def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print("Использование: python multimedia_analyzer.py <файл_с_командами>")
        print("\nПример файла с командами:")
        print("  ADD audio.mp3")
        print("  ADD video.mp4")
        print("  ADD image.jpg")
        print("  PRINT")
        print("  REM type == audio")
        print("  PRINT")
        sys.exit(1)
    
    command_file = sys.argv[1]
    process_commands(command_file)


if __name__ == "__main__":
    main()
