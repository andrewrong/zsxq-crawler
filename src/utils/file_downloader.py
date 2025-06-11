"""
文件下载工具
"""
import os
import requests
import tempfile
from pathlib import Path
from config import TEMP_DIR
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class FileDownloader:
    @staticmethod
    def download_file(url: str, filename: str = None) -> str:
        """
        Download a file from URL and save it to temporary directory
        
        Args:
            url (str): URL of the file to download
            filename (str, optional): Name to save the file as. If not provided, will use the last part of URL
            
        Returns:
            str: Path to the downloaded file, or None if download failed
        """
        try:
            # Get filename from URL if not provided
            if not filename:
                filename = url.split('/')[-1]
                
            # Create full path
            file_path = TEMP_DIR / filename
            
            # Download file
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Save file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            logger.info(f"Successfully downloaded file: {filename}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to download file {url}: {e}")
            return None
    
    @staticmethod
    def delete_filename(filename: str):
        file_path = TEMP_DIR / filename
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Successfully deleted file: {filename}")
        else:
            logger.warning(f"File not found: {filename}")

    @staticmethod
    def cleanup_temp_files():
        """清理临时下载的文件"""
        temp_dir = TEMP_DIR
        if temp_dir.exists():
            for file in temp_dir.iterdir():
                try:
                    file.unlink()
                except Exception as e:
                    print(f"临时文件删除失败 {file}: {e}")
