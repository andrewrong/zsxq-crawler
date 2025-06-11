import os
import json
from typing import Optional, Dict, List
from datetime import datetime
import requests
from src.models.group import Group
from src.utils.logger import setup_logger
from config import GROUP_CONFIG_MANAGER

logger = setup_logger(__name__)

class GroupManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GroupManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.cookie = os.getenv('ZSXQ_COOKIE')
            self.base_url = 'https://api.zsxq.com/v2'
            self._groups: Dict[int, Group] = {}
            self._session = requests.Session()
            self._session.headers.update({
                'Cookie': "zsxq_access_token=" + self.cookie,
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
            })
            self._initialized = True
            self.initialize_groups()

    def initialize_groups(self) -> bool:
        """Initialize groups from configuration"""
        try:
            logger.info("Initializing groups from configuration...")
            success = True
            
            # Get all configured group IDs
            group_ids = GROUP_CONFIG_MANAGER.get_group_configs()
            if not group_ids:
                logger.warning("No groups configured")
                return False
            
            # Load group info for each configured group
            for group_id in group_ids:
                group = self.get_group_info(group_id)
                if group:
                    logger.info(f"Successfully loaded group: {group.name} (ID: {group_id})")
                else:
                    logger.error(f"Failed to load group ID: {group_id}")
                    success = False
            
            if success:
                logger.info(f"Successfully initialized {len(self._groups)} groups")
            else:
                logger.warning("Some groups failed to initialize")
            
            return success
                
        except Exception as e:
            logger.error(f"Error initializing groups: {str(e)}")
            return False

    def get_group_info(self, group_id: int) -> Optional[Group]:
        """Get group information from API"""
        try:
            url = f"{self.base_url}/groups/{group_id}"
            response = self._session.get(url)
            
            if response.status_code != 200:
                logger.error(f"Failed to get group info for ID {group_id}: {response.status_code}")
                return None
            
            data = response.json()
            if not data.get('succeeded'):
                logger.error(f"API error for group ID {group_id}: {data.get('resp_data', {}).get('error')}")
                return None
            
            group = Group.from_dict(data)
            self._groups[group_id] = group
            return group
                
        except Exception as e:
            logger.error(f"Error getting group info for ID {group_id}: {str(e)}")
            return None

    def get_group(self, group_id: int) -> Optional[Group]:
        """Get group from cache"""
        return self._groups.get(group_id)

    def get_group_name(self, group_id: int) -> str:
        """Get group name from cache, fallback to ID if not found"""
        group = self.get_group(group_id)
        return group.name if group else str(group_id)

    def get_all_groups(self) -> List[Group]:
        """Get all cached groups"""
        return list(self._groups.values())

    def clear_cache(self):
        """Clear group cache"""
        self._groups.clear()

    def close(self):
        """Close requests session"""
        if self._session:
            self._session.close()
            self._session = None
            self._initialized = False
            GroupManager._instance = None

    def save_group_to_file(self, group_id: int, filepath: str):
        """Save group info to file"""
        group = self.get_group(group_id)
        if not group:
            logger.error(f"Group {self.get_group_name(group_id)} not found in cache")
            return
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(group.__dict__, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"Saved group {group.name} info to {filepath}")
        except Exception as e:
            logger.error(f"Error saving group {self.get_group_name(group_id)} info to file: {str(e)}")

    def load_group_from_file(self, filepath: str) -> Optional[Group]:
        """Load group info from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                group = Group(**data)
                self._groups[group.group_id] = group
                logger.info(f"Loaded group {group.name} from file {filepath}")
                return group
        except Exception as e:
            logger.error(f"Error loading group info from file {filepath}: {str(e)}")
            return None 