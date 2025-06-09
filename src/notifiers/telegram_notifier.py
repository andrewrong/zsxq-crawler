"""
Telegram notification handler for the 知识星球 crawler.
"""
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

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

    async def send_message(self, text, parse_mode='HTML'):
        """
        Asynchronously send a message via Telegram.
        
        Args:
            text (str): The message to send
            parse_mode (str): Message parse mode ('HTML' or 'Markdown')
        """
        if not self.bot or not self.chat_id:
            return
            
        try:
            await self.bot.send_message(
                chat_id=self.chat_id, 
                text=text, 
                parse_mode=parse_mode,
                disable_web_page_preview=True  # 避免预览可能导致的延迟
            )
        except TelegramError as e:
            print(f"Failed to send Telegram message: {e}")
            raise

    def send_message_sync(self, text, parse_mode='HTML'):
        """
        Synchronously send a message via Telegram.
        
        Args:
            text (str): The message to send
            parse_mode (str): Message parse mode ('HTML' or 'Markdown')
        """
        if not self.bot or not self.chat_id:
            return
            
        try:
            # 使用实例的事件循环
            loop = self.loop
            loop.run_until_complete(self.send_message(text, parse_mode))
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
            raise
