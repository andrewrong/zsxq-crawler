"""
Format messages for Telegram HTML mode
"""
import re
import warnings
from datetime import datetime
from html import escape
from typing import List
from urllib.parse import unquote

from bs4 import MarkupResemblesLocatorWarning

# 忽略 Beautiful Soup 的 URL 警告
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

from bs4 import BeautifulSoup, Tag

from ..crawlers.models import Topic


def get_attr_safe(tag: Tag, attr: str) -> str:
    """安全地获取标签属性"""
    if hasattr(tag, 'attrs'):
        value = tag.attrs.get(attr, '')
        if isinstance(value, (list, tuple)):
            return str(value[0]) if value else ''
        return str(value)
    return ''

def handle_link(text: str) -> str:
    """处理文本中的链接、@提及和话题标签"""
    if not text:
        return text
        
    soup = BeautifulSoup(text, "html.parser")

    # 处理@提及
    mentions = soup.find_all('e', attrs={'type': 'mention'})
    for mention in mentions:
        if isinstance(mention, Tag):
            mention_name = get_attr_safe(mention, 'title')
            mention.replace_with(soup.new_string(f"@{mention_name}"))

    # 处理话题标签
    hashtags = soup.find_all('e', attrs={'type': 'hashtag'})
    for tag in hashtags:
        if isinstance(tag, Tag):
            tag_name = unquote(get_attr_safe(tag, 'title'))
            tag.replace_with(soup.new_string(f"#{tag_name}"))

    # 处理网页链接
    links = soup.find_all('e', attrs={'type': 'web'})
    for link in links:
        if isinstance(link, Tag):
            title = unquote(get_attr_safe(link, 'title'))
            href = unquote(get_attr_safe(link, 'href'))
            new_a_tag = soup.new_tag('a', href=href)
            new_a_tag.string = title
            link.replace_with(new_a_tag)

    # 处理文本加粗
    bold_texts = soup.find_all('e', attrs={'type': 'text_bold'})
    for bold in bold_texts:
        if isinstance(bold, Tag):
            title = unquote(get_attr_safe(bold, 'title'))
            new_tag = soup.new_tag('b')
            new_tag.string = title
            bold.replace_with(new_tag)

    text = str(soup)
    # 清理任何剩余的 <e> 标签
    text = re.sub(r'<e[^>]*?>', '', text)
    text = re.sub(r'</e>', '', text)
    return text.strip()

class TelegramFormatter:
    @staticmethod
    def escape_html(text: str) -> str:
        """Escape special characters for Telegram HTML mode"""
        if not text:
            return ""
            
        # Process special tags first (before HTML escaping)
        text = handle_link(text)
        return text  # handle_link already includes HTML escaping

    @staticmethod
    def format_topic(topic: Topic) -> str:
        """Format a topic for Telegram message"""
        message_parts = []
        
        # Extract and format hashtags first
        text = topic.talk.text
        soup = BeautifulSoup(text, "html.parser")
        hashtags = soup.find_all('e', attrs={'type': 'hashtag'})
        if hashtags:
            tags = ["#知识星球", "#"+topic.group.name.replace(' ', '_')]
            for tag in hashtags:
                if isinstance(tag, Tag):
                    tag_name = unquote(get_attr_safe(tag, 'title'))
                    tag_name = tag_name.strip("#")
                    tags.append(f"#{tag_name.replace(' ', '_')}")
            if tags:
                message_parts.append(" ".join(tags) + "\n")
        
        # Format title
        if topic.title:
            message_parts.append(f"<b>{TelegramFormatter.escape_html(topic.title)}</b>\n")
        
        # Format main text
        text = TelegramFormatter.escape_html(topic.talk.text)
        message_parts.append(text)
        
        # Format author and metadata section
        meta_parts = []
        # Author info
        meta_parts.append(f"📝 作者：{TelegramFormatter.escape_html(topic.talk.owner.name)}")
        if topic.talk.owner.location:
            meta_parts.append(f"📍 {TelegramFormatter.escape_html(topic.talk.owner.location)}")
            
        # Stats
        # Add media counts in metadata
        if topic.talk.images:
            meta_parts.append(f"🖼 {len(topic.talk.images)}张图片")
            
        if topic.likes_count > 0:
            emoji_info = []
            if topic.likes_detail and topic.likes_detail.emojis:
                for emoji in topic.likes_detail.emojis:
                    emoji_info.append(f"{emoji.emoji_key}×{emoji.likes_count}")
                meta_parts.append("❤️ " + " ".join(emoji_info))
            else:
                meta_parts.append(f"❤️ {topic.likes_count}")
        if topic.comments_count > 0:
            meta_parts.append(f"💬 {topic.comments_count}")
            
        # Add metadata section
        message_parts.append("\n\n" + " | ".join(meta_parts))
        
        # Add image links if any
        if topic.talk.images:
            image_links = []
            for img in topic.talk.images:
                image_links.append(f"<a href='{img.original.url}'>查看原图</a>")
            message_parts.append("\n\n" + " | ".join(image_links))
        
        # Add timestamp in local time format
        if isinstance(topic.create_time, datetime):
            timestamp = topic.create_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp = str(topic.create_time)
        message_parts.append(f"\n\n⏰ {timestamp}")
        
        return "\n".join(filter(None, message_parts))