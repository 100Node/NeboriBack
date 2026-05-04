import os
import asyncio
import logging

logger = logging.getLogger(__name__)

class FFmpegService:
    async def _run_command(self, cmd: list[str]) -> None:
        """Базовий метод для запуску консольних команд асинхронно"""
        # Об'єднуємо команду в рядок для логів
        cmd_str = " ".join(cmd)
        logger.info(f"Running FFmpeg: {cmd_str}")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Чекаємо завершення і читаємо потоки
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_message = stderr.decode().strip()
            logger.error(f"FFmpeg failed with code {process.returncode}: {error_message}")
            raise RuntimeError(f"FFmpeg error: {error_message}")

    async def extract_audio(self, input_path: str, output_path: str) -> str:
        """Витягує аудіо і зберігає у форматі MP3"""
        cmd = [
            "ffmpeg", 
            "-y",                   # Перезаписувати файл, якщо існує
            "-i", input_path,       # Вхідний файл
            "-vn",                  # Вимкнути відео (Video No)
            "-c:a", "libmp3lame",   # Аудіокодек MP3
            "-q:a", "2",            # Висока якість аудіо
            output_path             # Вихідний файл
        ]
        await self._run_command(cmd)
        return output_path

    async def transcode_video(self, input_path: str, output_path: str, resolution: str = "1920x1080") -> str:
        """Стискає відео до потрібної роздільної здатності"""
        cmd = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-vf", f"scale={resolution}", # Зміна розміру (напр., 1920x1080 або 1280x720)
            "-c:v", "libx264",            # Відеокодек H.264 (найпопулярніший)
            "-preset", "fast",            # Швидкість стиснення (чим швидше, тим більший файл)
            "-crf", "23",                 # Якість (Constant Rate Factor, 23 - стандарт)
            "-c:a", "aac",                # Аудіокодек AAC
            "-b:a", "128k",               # Бітрейт аудіо
            output_path
        ]
        await self._run_command(cmd)
        return output_path