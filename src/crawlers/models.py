"""
Data models for 知识星球 content
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from src.utils.logger import setup_logger

logger = setup_logger(__name__)



@dataclass
class EmojiLike:
    emoji_key: str
    likes_count: int
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            emoji_key=data.get('emoji_key', ''),
            likes_count=data.get('likes_count', 0)
        )


@dataclass
class LikesDetail:
    emojis: List[EmojiLike] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict):
        emojis_data = data.get('emojis', [])
        return cls(
            emojis=[EmojiLike.from_dict(emoji) for emoji in emojis_data]
        )


@dataclass
class User:
    user_id: int
    name: str
    avatar_url: str
    description: Optional[str] = None
    location: Optional[str] = None
    number: Optional[int] = None
    ai_comment_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            user_id=int(data.get('user_id', 0)),
            name=data.get('name', ''),
            avatar_url=data.get('avatar_url', ''),
            description=data.get('description'),
            location=data.get('location'),
            number=data.get('number'),
            ai_comment_url=data.get('ai_comment_url')
        )


@dataclass
class Group:
    group_id: int
    name: str
    type: str
    background_url: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            group_id=int(data.get('group_id', 0)),
            name=data.get('name', ''),
            type=data.get('type', ''),
            background_url=data.get('background_url', '')
        )


@dataclass
class File:
    file_id: int
    name: str
    hash: str
    size: int
    download_count: int
    create_time: datetime

    @classmethod
    def from_dict(cls, data: dict):
        create_time_str = data.get('create_time', '')
        try:
            create_time = datetime.strptime(create_time_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        except ValueError:
            try:
                create_time = datetime.strptime(create_time_str, '%Y-%m-%dT%H:%M:%S%z')
            except ValueError:
                create_time = datetime.now()
        
        return cls(
            file_id=int(data.get('file_id', 0)),
            name=data.get('name', ''),
            hash=data.get('hash', ''),
            size=data.get('size', 0),
            download_count=data.get('download_count', 0),
            create_time=create_time
        )


@dataclass
class Like:
    create_time: datetime
    owner: User

    @classmethod
    def from_dict(cls, data: dict):
        create_time_str = data.get('create_time', '')
        try:
            create_time = datetime.strptime(create_time_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        except ValueError:
            try:
                create_time = datetime.strptime(create_time_str, '%Y-%m-%dT%H:%M:%S%z')
            except ValueError:
                create_time = datetime.now()
        return cls(
            create_time=create_time,
            owner=User.from_dict(data.get('owner', {}))
        )


@dataclass
class UserSpecific:
    liked: bool
    liked_emojis: List[str]
    subscribed: bool

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            liked=data.get('liked', False),
            liked_emojis=data.get('liked_emojis', []),
            subscribed=data.get('subscribed', False)
        )


@dataclass
class ImageSize:
    url: str
    width: int
    height: int
    size: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            url=data.get('url', ''),
            width=data.get('width', 0),
            height=data.get('height', 0),
            size=data.get('size')
        )

@dataclass
class Image:
    image_id: int
    type: str
    thumbnail: ImageSize
    large: ImageSize
    original: ImageSize

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            image_id=int(data.get('image_id', 0)),
            type=data.get('type', ''),
            thumbnail=ImageSize.from_dict(data.get('thumbnail', {})),
            large=ImageSize.from_dict(data.get('large', {})),
            original=ImageSize.from_dict(data.get('original', {}))
        )

@dataclass
class Talk:
    owner: User
    text: str
    images: List[Image] = field(default_factory=list)
    files: List[File] = field(default_factory=list)
    title: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        images = [Image.from_dict(img) for img in data.get('images', [])]
        files = [File.from_dict(f) for f in data.get('files', [])]
        return cls(
            owner=User.from_dict(data.get('owner', {})),
            text=data.get('text', ''),
            images=images,
            files=files,
            title=data.get('title')
        )


@dataclass
class Topic:
    topic_id: int
    group: Group
    type: str
    talk: Talk
    latest_likes: List[Like]
    create_time: datetime
    likes_count: int = 0
    tourist_likes_count: int = 0
    likes_detail: Optional[LikesDetail] = None
    rewards_count: int = 0
    comments_count: int = 0
    reading_count: int = 0
    readers_count: int = 0
    digested: bool = False
    sticky: bool = False
    user_specific: Optional[UserSpecific] = None
    title: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        latest_likes = [Like.from_dict(like) for like in data.get('latest_likes', [])]
        create_time_str = data.get('create_time', '')
        try:
            create_time = pd.to_datetime(create_time_str)
        except ValueError as e:
            logger.error(f"create time parse error:{e}")
            create_time = datetime.now()

        return cls(
            topic_id=int(data.get('topic_id', 0)),
            group=Group.from_dict(data.get('group', {})),
            type=data.get('type', ''),
            talk=Talk.from_dict(data.get('talk', {})),
            latest_likes=latest_likes,
            create_time=create_time,
            likes_count=data.get('likes_count', 0),
            tourist_likes_count=data.get('tourist_likes_count', 0),
            likes_detail=LikesDetail.from_dict(data.get('likes_detail', {})) if data.get('likes_detail') else None,
            rewards_count=data.get('rewards_count', 0),
            comments_count=data.get('comments_count', 0),
            reading_count=data.get('reading_count', 0),
            readers_count=data.get('readers_count', 0),
            digested=data.get('digested', False),
            sticky=data.get('sticky', False),
            user_specific=UserSpecific.from_dict(data.get('user_specific', {})) if data.get('user_specific') else None,
            title=data.get('title')
        )
    def get_timestamp(self) -> Optional[datetime]:
        """Get the creation time as a datetime object"""
        if isinstance(self.create_time, datetime):
            return self.create_time
        return None

@dataclass
class SimpleTopic:
    topic_id: int
    title: str
    create_time: datetime
    likes_count: int
    owner: User

    @classmethod
    def from_dict(cls, data: dict):
        create_time_str = data.get('create_time', '')
        try:
            create_time = datetime.strptime(create_time_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        except ValueError as e:
            logger.error(f"create_time parse is error: {e}")
            create_time = datetime.now()

        return cls(
            topic_id=int(data.get('topic_id', 0)),
            title=data.get('title', ''),
            likes_count=data.get('likes_count', 0),
            owner=User.from_dict(data.get('owner', {})),
            create_time=create_time
        )