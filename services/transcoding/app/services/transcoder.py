import os
import asyncio
import logging

logger = logging.getLogger(__name__)

class FFmpegService:
    async def _run_command(self, cmd: list[str]) -> None:
        cmd_str = " ".join(cmd)
        logger.info(f"Running FFmpeg: {cmd_str}")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise RuntimeError(f"FFmpeg error: {stderr.decode().strip()}")
                
        except asyncio.CancelledError:
            logger.warning(f"Task canceled! Sending SIGTERM to FFmpeg (PID: {process.pid})")
            process.terminate()
            await process.wait()
            raise

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
        """Стискає відео до потрібної роздільної здатності (MP4)"""
        cmd = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-vf", f"scale={resolution}", # Зміна розміру (напр., 1920x1080 або 1280x720)
            "-c:v", "libx264",            # Відеокодек H.264
            "-preset", "fast",            # Швидкість стиснення
            "-crf", "23",                 # Якість
            "-c:a", "aac",                # Аудіокодек AAC
            "-b:a", "128k",               # Бітрейт аудіо
            output_path
        ]
        await self._run_command(cmd)
        return output_path

    async def transcode_to_hls(self, input_path: str, output_dir: str, resolution: str = "1920x1080") -> str:
        """
        Конвертує відео у формат HLS (створює плейлист .m3u8 та сегменти .ts)
        """
        # Обов'язково створюємо директорію для чанків, інакше FFmpeg впаде
        os.makedirs(output_dir, exist_ok=True)
        
        # Визначаємо шляхи для плейлиста та патерн для шматочків відео
        playlist_path = os.path.join(output_dir, "index.m3u8")
        segment_pattern = os.path.join(output_dir, "segment_%03d.ts")

        cmd = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-vf", f"scale={resolution}", # Масштабуємо (напр. 1280x720)
            "-c:v", "libx264",            # Відеокодек H.264
            "-preset", "fast",            # Швидкий пресет для оптимізації процесора
            "-crf", "23",                 # Оптимальний баланс розмір/якість
            "-c:a", "aac",                # Аудіо AAC (стандарт для HLS)
            "-b:a", "128k",               # Бітрейт аудіо
            "-f", "hls",                  # Формат - HTTP Live Streaming
            "-hls_time", "10",            # Довжина одного чанка (10 секунд)
            "-hls_playlist_type", "vod",  # Тип плейлиста VOD (Video On Demand)
            "-hls_segment_filename", segment_pattern,
            playlist_path                 # Шлях до головного файлу плейлиста
        ]
        
        await self._run_command(cmd)
        
        # Повертаємо шлях саме до плейлиста, бо це головний файл для HLS
        return playlist_path
    
    