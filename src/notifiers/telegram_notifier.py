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

    async def send_message_with_media(self, text, images=None, files=None, parse_mode='HTML'):
        """
        发送带有媒体文件的消息到 Telegram
        
        Args:
            text (str): 要发送的消息文本
            images (list): 图片列表
            files (list): 文件列表
            parse_mode (str): 消息解析模式 ('HTML' 或 'Markdown')
        """
        if not self.bot or not self.chat_id:
            return
            
        try:
            # 如果有图片或文件，先下载
            media_group = []
            
            # 处理图片
            if images:
                for img in images:
                    img_path = FileDownloader.download_file(img.original.url)
                    if img_path:
                        media_group.append(InputMediaPhoto(
                            media=Path(img_path).open('rb'),
                            caption=text if len(media_group) == 0 else None,
                            parse_mode=parse_mode
                        ))
                        
            # 处理文件
            if files:
                for file in files:
                    file_path = FileDownloader.download_file(file.url, file.name)
                    if file_path:
                        media_group.append(InputMediaDocument(
                            media=Path(file_path).open('rb'),
                            caption=text if len(media_group) == 0 else None,
                            parse_mode=parse_mode,
                            filename=file.name
                        ))
            
            # 发送媒体组或普通消息
            if media_group:
                await self.bot.send_media_group(
                    chat_id=self.chat_id,
                    media=media_group
                )
                # 如果文件太多，可能 caption 放不下，就单独发送消息
                if len(media_group) > 1:
                    await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=text,
                        parse_mode=parse_mode,
                        disable_web_page_preview=False  # 允许预览
                    )
            else:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                    parse_mode=parse_mode,
                    disable_web_page_preview=False  # 允许预览
                )
                
        except Exception as e:
            print(f"发送消息失败：{e}")
            # 如果发送失败，尝试只发送文本
            try:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=f"{text}\n\n⚠️ 媒体文件发送失败：{str(e)}",
                    parse_mode=parse_mode,
                    disable_web_page_preview=False
                )
            except:
                raise
        finally:
            # 清理临时文件
            FileDownloader.cleanup_temp_files()

    def send_message_sync(self, text, images=None, files=None, parse_mode='HTML'):
        """
        同步方式发送带有媒体文件的消息到 Telegram
        
        Args:
            text (str): 要发送的消息文本
            images (list): 图片列表
            files (list): 文件列表
            parse_mode (str): 消息解析模式 ('HTML' 或 'Markdown')
        """
        if not self.bot or not self.chat_id:
            return
            
        self.loop.run_until_complete(
            self.send_message_with_media(text, images, files, parse_mode)
        )
