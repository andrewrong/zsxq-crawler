"""
文件下载工具
"""
import os
import tempfile
from pathlib import Path
from typing import Optional

import requests


class FileDownloader:
    @staticmethod
    def download_file(url: str, filename: Optional[str] = None) -> Optional[str]:
        """
        从 URL 下载文件并返回本地路径
        
        Args:
            url: 要下载的文件 URL
            filename: 可选的文件名
            
        Returns:
            str: 下载的文件路径，如果下载失败则返回 None
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # 创建临时目录（如果不存在）
            temp_dir = Path(tempfile.gettempdir()) / "zsxq_downloads"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # 使用提供的文件名或从 URL 提取
            if not filename:
                filename = os.path.basename(url.split('?')[0])
            temp_path = temp_dir / filename
            
            # 获取文件总大小（如果可用）
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            # 分块下载文件并显示进度
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\rDownloading {filename}: {progress:.1f}%", end="")
                
            if total_size > 0:
                print()  # 打印换行
            return str(temp_path)
            
        except Exception as e:
            print(f"文件下载失败 {url}: {e}")
            return None

    @staticmethod
    def cleanup_temp_files():
        """清理临时下载的文件"""
        temp_dir = Path(tempfile.gettempdir()) / "zsxq_downloads"
        if temp_dir.exists():
            for file in temp_dir.iterdir():
                try:
                    file.unlink()
                except Exception as e:
                    print(f"临时文件删除失败 {file}: {e}")
