from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
import re

@dataclass
class ImageSize:
    url: str
    width: int
    height: int
    size: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImageSize':
        return cls(**data)

@dataclass
class Image:
    image_id: int
    type: str
    thumbnail: ImageSize
    large: ImageSize
    original: ImageSize

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Image':
        data['thumbnail'] = ImageSize.from_dict(data['thumbnail'])
        data['large'] = ImageSize.from_dict(data['large'])
        data['original'] = ImageSize.from_dict(data['original'])
        return cls(**data)

@dataclass
class Category:
    category_id: int
    title: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Category':
        return cls(**data)

@dataclass
class User:
    user_id: int
    name: str
    avatar_url: str
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(
            user_id=data['user_id'],
            name=data['name'],
            avatar_url=data.get('avatar_url', ''),
            description=data.get('description')
        )

@dataclass
class Payment:
    amount: int
    duration: str
    mode: str
    end_time: datetime
    daily_price: Dict[str, bool]
    marked_price: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Payment':
        data['end_time'] = Group._parse_datetime(data['end_time'])
        return cls(**data)

@dataclass
class Renewal:
    discounted_percentage: int
    advance_discounted_percentage: int
    grace_discounted_percentage: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Renewal':
        return cls(**data)

@dataclass
class Distribution:
    privileged_user_enabled: bool
    enabled: bool
    percentage: int
    commission_percentage: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Distribution':
        return cls(**data)

@dataclass
class MuteMode:
    enabled: bool
    repeat_days: List[int]
    begin_time: str
    end_time: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MuteMode':
        return cls(**data)

@dataclass
class QuestionFee:
    min_amount: int
    amount_options: List[int]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuestionFee':
        return cls(**data)

@dataclass
class AutoRenewal:
    enabled: bool
    yearly_package_price: int
    quarterly_package_price: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutoRenewal':
        return cls(**data)

@dataclass
class Policies:
    need_examine: bool
    allow_member_renew: bool
    payment: Payment
    renewal: Renewal
    allow_enable_distribution: bool
    distribution: Distribution
    new_members_limit_days: int
    collect_member_profiles: bool
    mute_mode: MuteMode
    enable_scoreboard: bool
    free_questions_limit_count: int
    question_fee: QuestionFee
    enable_member_number: bool
    members_visibility: str
    allow_sharing: bool
    allow_private_chat: bool
    allow_search: bool
    allow_preview: bool
    allow_join: bool
    allow_anonymous_question: bool
    silence_new_member: bool
    enable_watermark: bool
    parse_book_title: bool
    allow_copy: bool
    allow_download: bool
    enable_iap: bool
    enable_iap_join_group: bool
    enable_iap_renew_group: bool
    allow_recommendation: bool
    allow_screen_capture_recording: bool
    hide_member_description: bool
    hide_member_group_and_account: bool
    auto_renewal: AutoRenewal

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Policies':
        data['payment'] = Payment.from_dict(data['payment'])
        data['renewal'] = Renewal.from_dict(data['renewal'])
        data['distribution'] = Distribution.from_dict(data['distribution'])
        data['mute_mode'] = MuteMode.from_dict(data['mute_mode'])
        data['question_fee'] = QuestionFee.from_dict(data['question_fee'])
        data['auto_renewal'] = AutoRenewal.from_dict(data['auto_renewal'])
        return cls(**data)

@dataclass
class Privileges:
    access_group_data: str
    access_incomes_data: str
    access_weekly_reports: str
    create_topic: str
    create_comment: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Privileges':
        return cls(**data)

@dataclass
class Statistics:
    topics: Dict[str, int]
    files: Dict[str, int]
    members: Dict[str, int]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Statistics':
        return cls(**data)

@dataclass
class Membership:
    begin_time: datetime
    end_time: datetime
    need_renew: bool
    can_renew: bool
    pay_time: datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Membership':
        data['begin_time'] = Group._parse_datetime(data['begin_time'])
        data['end_time'] = Group._parse_datetime(data['end_time'])
        data['pay_time'] = Group._parse_datetime(data['pay_time'])
        return cls(**data)

@dataclass
class Validity:
    begin_time: datetime
    end_time: datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Validity':
        data['begin_time'] = Group._parse_datetime(data['begin_time'])
        data['end_time'] = Group._parse_datetime(data['end_time'])
        return cls(**data)

@dataclass
class UserSpecific:
    paid: bool
    membership: Membership
    validity: Validity
    join_time: datetime
    rewarded_owner: bool
    enable_footprint: bool
    last_active_time: datetime
    followed_owner: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSpecific':
        data['membership'] = Membership.from_dict(data['membership'])
        data['validity'] = Validity.from_dict(data['validity'])
        data['join_time'] = Group._parse_datetime(data['join_time'])
        data['last_active_time'] = Group._parse_datetime(data['last_active_time'])
        return cls(**data)

@dataclass
class Group:
    group_id: int
    number: int
    name: str
    description: str
    create_time: datetime
    update_time: datetime
    privilege_user_last_topic_create_time: datetime
    latest_topic_create_time: datetime
    alive_time: datetime
    background_url: str
    type: str
    risk_level: str
    category: Category
    owner: User
    admin_ids: Optional[List[int]]
    guest_ids: Optional[List[int]]
    partner_ids: Optional[List[int]]
    promos: List[Image]
    policies: Policies
    privileges: Privileges
    statistics: Statistics
    user_specific: UserSpecific

    @staticmethod
    def _parse_datetime(dt_str: str) -> datetime:
        """
        统一处理各种格式的日期时间字符串
        支持的格式：
        - 2023-03-15T09:59:46.346+0800
        - 2023-03-15T09:59:46+0800
        - 2023-03-15T09:59:46Z
        - 2023-03-15T09:59:46.346Z
        """
        if not dt_str:
            return None

        try:
            # 移除毫秒部分
            if '.' in dt_str:
                dt_str = dt_str.split('.')[0]
            
            # 处理时区
            if dt_str.endswith('Z'):
                dt_str = dt_str.replace('Z', '+00:00')
            elif not dt_str.endswith('+00:00'):
                # 确保时区格式为 +HH:MM
                tz_match = re.search(r'([+-]\d{4})$', dt_str)
                if tz_match:
                    tz = tz_match.group(1)
                    dt_str = dt_str.replace(tz, f"{tz[:3]}:{tz[3:]}")
            
            return datetime.fromisoformat(dt_str)
        except Exception as e:
            raise ValueError(f"Invalid datetime format: {dt_str}") from e

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Group':
        """Create a Group instance from API response data"""
        group_data = data['resp_data']['group']
        
        # 统一处理所有日期时间字段
        datetime_fields = [
            'create_time', 
            'update_time', 
            'privilege_user_last_topic_create_time',
            'latest_topic_create_time', 
            'alive_time'
        ]
        
        for field in datetime_fields:
            if field in group_data:
                try:
                    group_data[field] = cls._parse_datetime(group_data[field])
                except ValueError as e:
                    raise ValueError(f"Failed to parse {field}: {str(e)}")
        
        # Convert nested objects
        group_data['category'] = Category.from_dict(group_data['category'])
        group_data['owner'] = User.from_dict(group_data['owner'])
        group_data['promos'] = [Image.from_dict(promo) for promo in group_data['promos']]
        group_data['policies'] = Policies.from_dict(group_data['policies'])
        group_data['privileges'] = Privileges.from_dict(group_data['privileges'])
        group_data['statistics'] = Statistics.from_dict(group_data['statistics'])
        group_data['user_specific'] = UserSpecific.from_dict(group_data['user_specific'])
        
        # Set default values for optional fields
        group_data.setdefault('admin_ids', [])
        group_data.setdefault('guest_ids', [])
        group_data.setdefault('partner_ids', [])
        
        return cls(**group_data) 