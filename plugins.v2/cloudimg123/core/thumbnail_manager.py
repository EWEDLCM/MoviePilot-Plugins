"""
缩略图管理器
负责生成、管理和缓存图片缩略图
"""

import os
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import io

from app.log import logger
from .utils import ensure_directory_exists, calculate_file_hash


class ThumbnailManager:
    """
    缩略图管理器，负责图片缩略图的生成和缓存
    """
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.cache_dir = config_path / "cache" / "thumbnails"
        self.thumbnail_size = (200, 200)  # 缩略图尺寸
        self.thumbnail_format = "WEBP"  # 使用WebP格式节省空间
        self.thumbnail_quality = 85  # 缩略图质量
        
        # 确保缓存目录存在
        self._ensure_cache_directory()
    
    def _ensure_cache_directory(self):
        """确保缓存目录存在"""
        try:
            if not self.cache_dir.exists():
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"[CloudImg123-Thumbnail] 创建缩略图缓存目录: {self.cache_dir}")
        except Exception as e:
            logger.error(f"[CloudImg123-Thumbnail] 创建缓存目录失败: {str(e)}")
    
    def _log(self, level: str, message: str):
        """安全的日志记录方法"""
        log_message = f"[CloudImg123-Thumbnail] {message}"
        if level == "info":
            logger.info(log_message)
        elif level == "error":
            logger.error(log_message)
        elif level == "warning":
            logger.warning(log_message)

    def get_thumbnail_path(self, file_id: str) -> Optional[Path]:
        """
        获取缩略图文件路径
        """
        try:
            thumbnail_filename = f"{file_id}.webp"
            thumbnail_path = self.cache_dir / thumbnail_filename
            
            # 检查文件是否存在
            if thumbnail_path.exists():
                return thumbnail_path
            else:
                self._log("warning", f"缩略图文件不存在: {thumbnail_path}")
                return None
                
        except Exception as e:
            self._log("error", f"获取缩略图路径异常: {str(e)}")
            return None

    def get_thumbnail_url_path(self, file_id: str) -> Optional[str]:
        """
        获取缩略图的URL路径（用于前端访问）
        """
        try:
            thumbnail_path = self.get_thumbnail_path(file_id)
            self._log("info", f"get_thumbnail_url_path 调用: file_id={file_id}, thumbnail_path={thumbnail_path}")
            
            if thumbnail_path and thumbnail_path.exists():
                # 返回一个特殊的标记，告诉前端这个项目有缩略图
                # 前端会在图片加载失败时尝试通过API获取缩略图
                self._log("info", f"缩略图存在，标记为可用: {file_id}")
                return "HAS_THUMBNAIL"
            else:
                self._log("warning", f"缩略图文件不存在: {thumbnail_path}")
                return None
                
        except Exception as e:
            self._log("error", f"获取缩略图URL路径异常: {str(e)}")
            return None

    async def generate_thumbnail(self, image_url: str, file_id: str) -> Optional[Path]:
        """
        生成缩略图
        """
        try:
            self._log("info", f"开始生成缩略图: {file_id}")
            
            # 检查是否已存在
            existing_thumbnail = self.get_thumbnail_path(file_id)
            if existing_thumbnail:
                self._log("info", f"缩略图已存在，跳过生成: {file_id}")
                return existing_thumbnail
            
            # 下载图片
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status != 200:
                        self._log("error", f"下载图片失败，HTTP状态码: {response.status}")
                        return None
                    
                    image_data = await response.read()
                    
                    # 生成缩略图
                    thumbnail_path = await self._create_thumbnail(image_data, file_id)
                    if thumbnail_path:
                        self._log("info", f"缩略图生成成功: {file_id}")
                        return thumbnail_path
                    else:
                        self._log("error", f"缩略图生成失败: {file_id}")
                        return None
                        
        except Exception as e:
            self._log("error", f"生成缩略图异常: {str(e)}")
            return None

    async def _create_thumbnail(self, image_data: bytes, file_id: str) -> Optional[Path]:
        """
        创建缩略图文件
        """
        try:
            # 打开图片
            img = Image.open(io.BytesIO(image_data))
            
            # 转换为RGB模式（如果需要）
            if img.mode in ('RGBA', 'P', 'LA'):
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                # 如果图片有alpha通道，将其作为mask粘贴到背景上
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            
            # 生成缩略图
            img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
            
            # 保存缩略图
            thumbnail_filename = f"{file_id}.webp"
            thumbnail_path = self.cache_dir / thumbnail_filename
            
            img.save(
                thumbnail_path, 
                format=self.thumbnail_format,
                quality=self.thumbnail_quality,
                optimize=True
            )
            
            self._log("info", f"缩略图保存成功: {thumbnail_filename}")
            return thumbnail_path
            
        except Exception as e:
            self._log("error", f"创建缩略图文件异常: {str(e)}")
            return None

    def delete_thumbnail(self, file_id: str) -> bool:
        """
        删除缩略图
        """
        try:
            thumbnail_path = self.get_thumbnail_path(file_id)
            if thumbnail_path and thumbnail_path.exists():
                thumbnail_path.unlink()
                self._log("info", f"缩略图删除成功: {file_id}")
                return True
            else:
                self._log("warning", f"缩略图文件不存在: {file_id}")
                return False
                
        except Exception as e:
            self._log("error", f"删除缩略图异常: {str(e)}")
            return False

    def cleanup_all_thumbnails(self) -> bool:
        """
        清理所有缩略图
        """
        try:
            if self.cache_dir.exists():
                for thumbnail_file in self.cache_dir.glob("*.webp"):
                    thumbnail_file.unlink()
                
                self._log("info", "所有缩略图清理完成")
                return True
            else:
                self._log("warning", "缩略图缓存目录不存在")
                return False
                
        except Exception as e:
            self._log("error", f"清理所有缩略图异常: {str(e)}")
            return False

    def get_cache_info(self) -> dict:
        """
        获取缓存信息
        """
        try:
            if not self.cache_dir.exists():
                return {
                    "total_count": 0,
                    "total_size": 0,
                    "cache_dir": str(self.cache_dir),
                    "exists": False
                }
            
            thumbnail_files = list(self.cache_dir.glob("*.webp"))
            total_size = sum(f.stat().st_size for f in thumbnail_files)
            
            return {
                "total_count": len(thumbnail_files),
                "total_size": total_size,
                "cache_dir": str(self.cache_dir),
                "exists": True
            }
            
        except Exception as e:
            self._log("error", f"获取缓存信息异常: {str(e)}")
            return {
                "total_count": 0,
                "total_size": 0,
                "cache_dir": str(self.cache_dir),
                "error": str(e)
            }

    def cleanup_orphaned_thumbnails(self, active_file_ids: list) -> int:
        """
        清理孤立的缩略图（没有对应历史记录的缩略图）
        """
        try:
            if not self.cache_dir.exists():
                return 0
            
            cleaned_count = 0
            for thumbnail_file in self.cache_dir.glob("*.webp"):
                file_id = thumbnail_file.stem
                if file_id not in active_file_ids:
                    thumbnail_file.unlink()
                    cleaned_count += 1
                    self._log("info", f"清理孤立缩略图: {file_id}")
            
            if cleaned_count > 0:
                self._log("info", f"清理完成，共删除 {cleaned_count} 个孤立缩略图")
            
            return cleaned_count
            
        except Exception as e:
            self._log("error", f"清理孤立缩略图异常: {str(e)}")
            return 0