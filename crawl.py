#!/usr/bin/env python3
"""
知识星球内容抓取工具
支持实时 Telegram 通知
"""
import os
import time
from datetime import datetime

from config import validate_config
from src.crawlers.zsxq_crawler import ZsxqCrawler
from src.formatters.message_formatter import TelegramFormatter
from src.notifiers.telegram_notifier import TelegramNotifier
from state_manager import StateManager


def main():
    # Validate environment variables
    try:
        validate_config()
    except ValueError as e:
        print(f"配置错误：{str(e)}")
        return

    # Initialize components
    crawler = ZsxqCrawler()
    notifier = TelegramNotifier()
    last_topic_id = StateManager.get_state()

    try:
        # Start crawling
        print("开始抓取知识星球内容...")
        while True:
            topics, new_last_topic_id = crawler.crawl(last_topic_id=last_topic_id)
            
            if topics:
                success_count = 0
                reversed_topics = list(reversed(topics))  # 从老到新发送
                for topic in reversed_topics:
                    try:
                        # Format and send each topic
                        message = TelegramFormatter.format_topic(topic)
                        notifier.send_message_sync(message, parse_mode='HTML')
                        success_count += 1
                        print(f"已发送主题：{topic.title or f'ID:{topic.topic_id}'}")
                        time.sleep(1)  # 避免发送太快
                    except Exception as e:
                        print(f"发送消息失败：{str(e)}")
                        continue
                
                # Save the last topic id after successful sending
                if new_last_topic_id and success_count > 0:
                    StateManager.save_state(new_last_topic_id)
                    print(f"已成功转发 {success_count} 条更新内容")
                    last_topic_id = new_last_topic_id
            else:
                print("未获取到任何新内容")
                break  # 如果没有新内容就退出循环
                
            time.sleep(2)  # 稍作延迟，避免请求太快
            
    except Exception as e:
        error_msg = f"抓取过程发生错误：{str(e)}"
        print(error_msg)
        try:
            notifier.send_message_sync(f"⚠️ {error_msg}")
        except:
            pass

if __name__ == '__main__':
    main()