"""
Telegram notification handler for the 知识星球 crawler.
"""
import asyncio
import mimetypes
from pathlib import Path

from telegram import Bot, InputMediaDocument, InputMediaPhoto
from telegram.error import TelegramError

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

from ..utils.file_downloader import FileDownloader


class TelegramNotifier:
    def __init__(self):
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
            self.chat_id = TELEGRAM_CHAT_ID
        else:
            self.bot = None
            self.chat_id = None
        self._loop = None

    @property
    def loop(self):
        """Get or create event loop"""
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        return self._loop

    async def send_message_with_media(self, text, thread_id=None, images=None, files=None, parse_mode='HTML'):
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
            
        try:
            # If there are images or files, download them first
            media_group = []
            
            # Handle images
            if images:
                for img in images:
                    img_path = FileDownloader.download_file(img.original.url)
                    if img_path:
                        media_group.append(InputMediaPhoto(
                            media=Path(img_path).open('rb'),
                            caption=text if len(media_group) == 0 else None,
                            parse_mode=parse_mode
                        ))
                        
            # Handle files
            if files:
                for file in files:
                    if not hasattr(file, 'url'):
                        continue
                    file_path = FileDownloader.download_file(file.url, file.name)
                    if file_path:
                        media_group.append(InputMediaDocument(
                            media=Path(file_path).open('rb'),
                            caption=text if len(media_group) == 0 else None,
                            parse_mode=parse_mode,
                            filename=file.name
                        ))
            
            # Send media group if there are any media files
            if media_group:
                await self.bot.send_media_group(
                    chat_id=self.chat_id,
                    media=media_group,
                    message_thread_id=thread_id
                )
            else:
                # Send text-only message
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                    parse_mode=parse_mode,
                    message_thread_id=thread_id
                )
                
        except TelegramError as e:
            print(f"Failed to send Telegram message: {e}")
        except Exception as e:
            print(f"Unexpected error while sending Telegram message: {e}")

    def send_message_sync(self, text, thread_id=None, images=None, files=None, parse_mode='HTML'):
        """
        Send message with media files to Telegram synchronously
        
        Args:
            text (str): Message text to send
            thread_id (str): Thread ID for the message
            images (list): List of images
            files (list): List of files
            parse_mode (str): Message parse mode ('HTML' or 'Markdown')
        """
        if not self.bot or not self.chat_id:
            return
            
        self.loop.run_until_complete(
            self.send_message_with_media(text, thread_id, images, files, parse_mode)
        )
