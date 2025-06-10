#!/usr/bin/env python3
"""
知识星球内容抓取工具
支持实时 Telegram 通知
"""
import os
import time
from datetime import datetime

from config import validate_config, IS_CRAWL_HOME
from src.crawlers.zsxq_crawler import ZsxqCrawler
from src.formatters.message_formatter import TelegramFormatter
from src.notifiers.telegram_notifier import TelegramNotifier
from state_manager import CrawlType, StateManager


def process_topics(crawler, notifier, topics, crawl_type):
    """处理主题列表：格式化并发送到 Telegram"""
    success_count = 0
    last_topic_id = None
    
    # 从老到新处理主题
    reversed_topics = list(reversed(topics))
    for topic in reversed_topics:
        try:
            # 格式化并发送
            message = TelegramFormatter.format_topic(topic, crawl_type)
            notifier.send_message_sync(
                text=message,
                images=topic.talk.images if topic.talk else None,
                files=topic.talk.files if topic.talk else None,
                parse_mode='HTML'
            )
            success_count += 1
            print(f"已发送主题：{topic.title or f'ID:{topic.topic_id}'}")
            
            # 记录最后处理的主题 ID
            if not last_topic_id or topic.topic_id > last_topic_id:
                last_topic_id = topic.topic_id
                
            time.sleep(2)  # 避免发送太快
            
        except Exception as e:
            print(f"处理主题失败 [ID:{topic.topic_id}]: {e}")
            continue
            
    return success_count, last_topic_id


def main():
    # 验证环境变量配置
    try:
        validate_config()
    except ValueError as e:
        print(f"配置错误：{str(e)}")
        return

    # 初始化组件
    crawler = ZsxqCrawler()
    notifier = TelegramNotifier()
    
    try:
        print("开始抓取知识星球内容...")
        
        # 处理首页内容
        home_state = StateManager.get_state(CrawlType.HOME)
        last_home_id = home_state.get('last_topic_id') if home_state else None
        success_count = 0

        if IS_CRAWL_HOME:
            topics, new_last_topic_id = crawler.crawl_home_topics(last_topic_id=last_home_id)
            if topics:
                success_count, last_topic_id = process_topics(crawler, notifier, topics, CrawlType.HOME.value)
            else:
                print(f"{CrawlType.HOME} 未获取到任何新内容")
            if success_count > 0:
                StateManager.save_state(CrawlType.HOME, {
                    'last_topic_id': last_topic_id,
                    'update_time': datetime.now().isoformat()
                })
                print(f"已成功转发 {success_count} 条首页更新")
        
        # 处理精华内容
        digest_state = StateManager.get_state(CrawlType.DIGEST)
        last_digest_id = digest_state.get('last_topic_id') if digest_state else None
        
        digest_topics, new_last_digest_id = crawler.get_digest_topics(last_topic_id=last_digest_id)
        if digest_topics:
            success_count, last_topic_id = process_topics(crawler, notifier, digest_topics, CrawlType.DIGEST.value)
            if success_count > 0:
                StateManager.save_state(CrawlType.DIGEST, {
                    'last_topic_id': last_topic_id,
                    'update_time': datetime.now().isoformat()
                })
                print(f"已成功转发 {success_count} 条精华内容")
        else:
            print(f"{CrawlType.DIGEST} 未获取到任何新内容")
            
    except Exception as e:
        error_msg = f"抓取过程发生错误：{str(e)}"
        print(error_msg)
        try:
            notifier.send_message_sync(text=f"⚠️ {error_msg}")
        except:
            pass


if __name__ == '__main__':
    main()