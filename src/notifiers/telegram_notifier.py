"""
Telegram notification handler for the 知识星球 crawler.
"""
import asyncio
import mimetypes
from pathlib import Path
import os
from typing import Optional, List

from telegram import Bot, InputMediaDocument, InputMediaPhoto
from telegram.error import TelegramError
from telegram.constants import ParseMode

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

from ..utils.file_downloader import FileDownloader
from src.utils.logger import setup_logger
import aiohttp

logger = setup_logger(__name__)


class TelegramNotifier:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        if not self.bot_token or not self.chat_id:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")
        self.bot = Bot(token=self.bot_token, timeout=60)
        self._loop = None

    def _get_loop(self):
        """Get or create event loop"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop

    async def _send_message(self, text: str, thread_id: Optional[int] = None, parse_mode: str = 'HTML') -> bool:
        """Send a message to Telegram"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if thread_id:
            data["message_thread_id"] = thread_id
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        logger.info("Successfully sent Telegram message")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send Telegram message: {error_text}")
                        return False
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
            
    async def _send_media(self, media_type: str, media_data: dict, thread_id: Optional[int] = None) -> bool:
        """Send media (photo/document) to Telegram"""
        url = f"https://api.telegram.org/bot{self.bot_token}/send{media_type.capitalize()}"
        data = {
            "chat_id": self.chat_id,
            media_type: media_data["file_id"],
            "caption": media_data.get("caption", ""),
            "parse_mode": "HTML"
        }
        if thread_id:
            data["message_thread_id"] = thread_id
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        logger.info(f"Successfully sent {media_type}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send {media_type}: {error_text}")
                        return False
        except Exception as e:
            logger.error(f"Failed to send {media_type}: {e}")
            return False
            
    async def _send_message_with_media(self, text, thread_id=None, images=None, files=None, parse_mode='HTML'):
        """
        Send message with media files to Telegram
        
        Args:
            text (str): Message text to send
            thread_id (str): Thread ID for the message
            images (list): List of images
            files (list): List of files
            parse_mode (str): Message parse mode ('HTML' or 'Markdown')
        """
        if not self.bot or not self.chat_id:
            return
        
        if len(text) > 4096 :
            logger.warning(f"Text length is greater than 4096 characters, truncating to 4096 characters")
            text = text[:4000] + "...(more)"
            
        try:
            # # If there are images or files, download them first
            # media_group = []
            
            # # Handle images
            # if images:
            #     for i, img in enumerate(images):
            #         img_path = FileDownloader.download_file(img.large.url)
            #         if img_path:
            #             media_group.append(InputMediaPhoto(
            #                 media=Path(img_path).open('rb'),
            #                 caption=text if i == 0 and not files else None,
            #                 parse_mode=parse_mode
            #             ))
                    
            # # Handle files
            # if files:
            #     for i, file in enumerate(files):
            #         if not hasattr(file, 'url'):
            #             continue
            #         file_path = FileDownloader.download_file(file.url, file.name)
            #         if file_path:
            #             media_group.append(InputMediaDocument(
            #                 media=Path(file_path).open('rb'),
            #                 caption=text if i == 0 and not images else None,
            #                 parse_mode=parse_mode,
            #                 filename=file.name
            #             ))
            
            # # Send media group if there are any media files
            # if media_group:
            #     await self.bot.send_media_group(
            #         chat_id=self.chat_id,
            #         media=media_group,
            #         message_thread_id=thread_id
            #     )
            # else:
                # Send text-only message
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                    parse_mode=parse_mode,
                    message_thread_id=thread_id,
                )
                
        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}, text:{len(text)}, images:{len(images)}, files:{len(files)}")
        except Exception as e:
            logger.error(f"Unexpected error while sending Telegram message: {e}")
        finally:
            FileDownloader.cleanup_temp_files()
            
    def send_message_with_media(self, text, thread_id=None, images=None, files=None, parse_mode='HTML'):
        """Synchronous wrapper for send_message_with_media"""
        loop = self._get_loop()
        return loop.run_until_complete(
            self._send_message_with_media(text, thread_id, images, files, parse_mode)
        )
        
    def send_message_sync(self, text: str, thread_id: Optional[str] = None, images: Optional[List[str]] = None, files: Optional[List[str]] = None, parse_mode: str = ParseMode.HTML) -> bool:
        """Synchronous method to send message"""
        try:
            loop = self._get_loop()
            return loop.run_until_complete(
                self.bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                    parse_mode=parse_mode,
                    message_thread_id=thread_id
                )
            )
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
