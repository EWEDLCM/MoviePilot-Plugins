import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.log import logger


class UploadRecord:
    """
    上传记录数据类
    """
    
    def __init__(self, record_id: str = None, filename: str = "", file_id: str = "",
                 download_url: str = "", user_self_url: str = "", file_size: int = 0,
                 upload_time: str = None, formats: Dict[str, str] = None, 
                 file_hash: str = None):
        self.id = record_id or str(uuid.uuid4())
        self.filename = filename
        self.file_id = file_id
        self.download_url = download_url
        self.user_self_url = user_self_url or download_url
        self.file_size = file_size
        self.upload_time = upload_time or datetime.now().isoformat()
        self.formats = formats or {}
        self.file_hash = file_hash  # 新增：文件哈希值

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式，兼容前端期望的字段名
        """
        return {
            "id": self.id,
            "filename": self.filename,
            "original_name": self.filename,  # 前端期望的字段名
            "file_id": self.file_id,
            "file_hash": self.file_hash,  # 新增字段
            "download_url": self.download_url,
            "thumbnail_url": self.download_url,  # 123云盘没有缩略图，使用原图
            "user_self_url": self.user_self_url,
            "file_size": self.file_size,
            "upload_time": self.upload_time,
            "formats": self.formats
        }
    
    def to_dict_with_thumbnail(self, thumbnail_manager) -> Dict[str, Any]:
        """
        转换为字典格式，包含缩略图路径
        """
        # 获取缩略图URL路径
        thumbnail_url_path = thumbnail_manager.get_thumbnail_url_path(self.file_id)
        
        return {
            "id": self.id,
            "filename": self.filename,
            "original_name": self.filename,
            "file_id": self.file_id,
            "file_hash": self.file_hash,  # 新增字段
            "download_url": self.download_url,
            "thumbnail_url": thumbnail_url_path or self.download_url,  # 优先使用本地缩略图
            "user_self_url": self.user_self_url,
            "file_size": self.file_size,
            "upload_time": self.upload_time,
            "formats": self.formats,
            "has_local_thumbnail": bool(thumbnail_url_path)  # 标记是否有本地缩略图
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UploadRecord':
        """
        从字典创建记录对象
        """
        return cls(
            record_id=data.get("id"),
            filename=data.get("filename", ""),
            file_id=data.get("file_id", ""),
            download_url=data.get("download_url", ""),
            user_self_url=data.get("user_self_url", ""),
            file_size=data.get("file_size", 0),
            upload_time=data.get("upload_time"),
            formats=data.get("formats", {}),
            file_hash=data.get("file_hash")  # 新增字段
        )


class HistoryManager:
    """
    历史记录管理器，使用config/plugins/cloudimg123目录存储
    """
    
    def __init__(self, config_path: Path, limit: int = 50):
        self.config_path = config_path
        self.limit = limit
        self.history_file = config_path / "upload_history.json"
        
        # 导入缩略图管理器
        from .thumbnail_manager import ThumbnailManager
        self.thumbnail_manager = ThumbnailManager(config_path)
        
        # 确保配置目录存在
        if not self.config_path.exists():
            self.config_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"[CloudImg123-History] 创建历史数据目录: {self.config_path}")

    def _log(self, level: str, message: str):
        """
        安全的日志记录方法
        """
        log_message = f"[CloudImg123-History] {message}"
        if level == "info":
            logger.info(log_message)
        elif level == "error":
            logger.error(log_message)
        elif level == "warning":
            logger.warning(log_message)

    def _load_history(self) -> List[Dict[str, Any]]:
        """
        从文件加载历史记录
        """
        try:
            if not self.history_file.exists():
                return []
            
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
                
        except Exception as e:
            logger.error(f"[CloudImg123-History] 加载历史记录失败: {str(e)}")
            return []

    def _save_history(self, history: List[Dict[str, Any]]) -> bool:
        """
        保存历史记录到文件
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            return True
            
        except Exception as e:
            logger.error(f"[CloudImg123-History] 保存历史记录失败: {str(e)}")
            return False

    def add_record(self, record: UploadRecord) -> bool:
        """
        添加上传记录
        """
        try:
            history = self._load_history()
            
            # 添加新记录到开头
            history.insert(0, record.to_dict())
            
            # 限制历史记录数量（limit为0表示无限）
            if self.limit > 0 and len(history) > self.limit:
                history = history[:self.limit]
                logger.info(f"[CloudImg123-History] 历史记录超出限制，保留最新 {self.limit} 条")
            
            # 保存到文件
            success = self._save_history(history)
            if success:
                logger.info(f"[CloudImg123-History] 添加历史记录成功: {record.filename}")
            else:
                logger.error(f"[CloudImg123-History] 添加历史记录失败: {record.filename}")
                
            return success
            
        except Exception as e:
            logger.error(f"[CloudImg123-History] 添加历史记录异常: {str(e)}")
            return False

    def get_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取历史记录列表
        """
        try:
            history = self._load_history()
            
            # 应用查询限制（limit为0表示无限）
            query_limit = limit or self.limit
            if query_limit > 0 and len(history) > query_limit:
                history = history[:query_limit]
            
            logger.info(f"[CloudImg123-History] 获取历史记录 {len(history)} 条")
            return history
            
        except Exception as e:
            logger.error(f"[CloudImg123-History] 获取历史记录异常: {str(e)}")
            return []
    
    def get_history_with_thumbnails(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取历史记录列表，包含缩略图信息
        """
        try:
            history = self._load_history()
            
            # 应用查询限制（limit为0表示无限）
            query_limit = limit or self.limit
            if query_limit > 0 and len(history) > query_limit:
                history = history[:query_limit]
            
            # 转换为记录对象并添加缩略图信息
            result = []
            for record_data in history:
                record = UploadRecord.from_dict(record_data)
                result.append(record.to_dict_with_thumbnail(self.thumbnail_manager))
            
            logger.info(f"[CloudImg123-History] 获取历史记录（含缩略图）{len(result)} 条")
            return result
            
        except Exception as e:
            logger.error(f"[CloudImg123-History] 获取历史记录（含缩略图）异常: {str(e)}")
            return []

    def get_record(self, record_id: str) -> Optional[UploadRecord]:
        """
        根据ID获取单条记录
        """
        try:
            history = self._load_history()
            
            for record_data in history:
                if record_data.get("id") == record_id:
                    return UploadRecord.from_dict(record_data)
            
            return None
            
        except Exception as e:
            logger.error(f"[CloudImg123-History] 获取记录异常: {str(e)}")
            return None

    def get_record_by_file_id(self, file_id: str) -> Optional[UploadRecord]:
        """
        根据file_id获取单条记录
        """
        try:
            history = self._load_history()
            
            for record_data in history:
                if record_data.get("file_id") == file_id:
                    return UploadRecord.from_dict(record_data)
            
            return None
            
        except Exception as e:
            logger.error(f"[CloudImg123-History] 根据file_id获取记录异常: {str(e)}")
            return None

    def delete_record(self, record_id: str) -> bool:
        """
        删除指定记录
        """
        try:
            history = self._load_history()
            
            # 找到要删除的记录
            record_to_delete = None
            for record in history:
                if record.get("id") == record_id:
                    record_to_delete = record
                    break
            
            if not record_to_delete:
                logger.warning(f"[CloudImg123-History] 未找到要删除的记录: {record_id}")
                return False
            
            # 删除记录
            history = [record for record in history if record.get("id") != record_id]
            
            # 保存历史记录
            success = self._save_history(history)
            if success:
                # 同步删除缩略图
                file_id = record_to_delete.get("file_id")
                if file_id:
                    self.thumbnail_manager.delete_thumbnail(file_id)
                
                logger.info(f"[CloudImg123-History] 删除历史记录成功: {record_id}")
            else:
                logger.error(f"[CloudImg123-History] 删除历史记录保存失败: {record_id}")
            
            return success
                
        except Exception as e:
            logger.error(f"[CloudImg123-History] 删除历史记录异常: {str(e)}")
            return False

    def clear_history(self) -> bool:
        """
        清空所有历史记录
        """
        try:
            success = self._save_history([])
            if success:
                # 同步清空所有缩略图
                self.thumbnail_manager.cleanup_all_thumbnails()
                logger.info(f"[CloudImg123-History] 清空历史记录成功")
            else:
                logger.error(f"[CloudImg123-History] 清空历史记录失败")
            return success
            
        except Exception as e:
            logger.error(f"[CloudImg123-History] 清空历史记录异常: {str(e)}")
            return False

    def update_limit(self, new_limit: int):
        """
        更新历史记录数量限制
        """
        try:
            old_limit = self.limit
            self.limit = new_limit
            
            # 如果新限制更小，需要清理多余记录
            if new_limit < old_limit:
                history = self._load_history()
                if len(history) > new_limit:
                    # 获取被删除记录的file_id
                    removed_records = history[new_limit:]
                    removed_file_ids = [record.get("file_id") for record in removed_records if record.get("file_id")]
                    
                    # 截断历史记录
                    history = history[:new_limit]
                    success = self._save_history(history)
                    
                    if success:
                        # 清理对应的缩略图
                        for file_id in removed_file_ids:
                            self.thumbnail_manager.delete_thumbnail(file_id)
                        
                        logger.info(f"[CloudImg123-History] 历史记录限制从 {old_limit} 更新为 {new_limit}，清理了多余记录")
                    else:
                        logger.error(f"[CloudImg123-History] 更新历史记录限制失败")
            else:
                logger.info(f"[CloudImg123-History] 历史记录限制从 {old_limit} 更新为 {new_limit}")
                
        except Exception as e:
            logger.error(f"[CloudImg123-History] 更新历史记录限制异常: {str(e)}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取历史记录统计信息
        """
        try:
            history = self._load_history()
            
            if not history:
                return {
                    "total_count": 0,
                    "total_size": 0,
                    "latest_upload": None
                }
            
            total_size = sum(record.get("file_size", 0) for record in history)
            latest_upload = history[0].get("upload_time") if history else None
            
            return {
                "total_count": len(history),
                "total_size": total_size,
                "latest_upload": latest_upload
            }
            
        except Exception as e:
            logger.error(f"[CloudImg123-History] 获取统计信息异常: {str(e)}")
            return {
                "total_count": 0,
                "total_size": 0,
                "latest_upload": None
            }
    
    async def generate_thumbnail_for_record(self, file_id: str, image_url: str) -> bool:
        """
        为指定记录生成缩略图
        """
        try:
            success = await self.thumbnail_manager.generate_thumbnail(image_url, file_id)
            if success:
                logger.info(f"[CloudImg123-History] 为记录 {file_id} 生成缩略图成功")
                return True
            else:
                logger.warning(f"[CloudImg123-History] 为记录 {file_id} 生成缩略图失败")
                return False
        except Exception as e:
            logger.error(f"[CloudImg123-History] 生成缩略图异常 {file_id}: {str(e)}")
            return False
    
    async def generate_all_thumbnails(self) -> Dict[str, Any]:
        """
        为所有历史记录生成缩略图
        """
        try:
            history = self._load_history()
            if not history:
                return {
                    "success": True,
                    "total": 0,
                    "generated": 0,
                    "failed": 0,
                    "message": "没有历史记录需要处理"
                }
            
            total = len(history)
            generated = 0
            failed = 0
            
            logger.info(f"[CloudImg123-History] 开始为 {total} 条记录生成缩略图")
            
            for record_data in history:
                file_id = record_data.get("file_id")
                download_url = record_data.get("download_url")
                
                if file_id and download_url:
                    success = await self.generate_thumbnail_for_record(file_id, download_url)
                    if success:
                        generated += 1
                    else:
                        failed += 1
                else:
                    failed += 1
            
            result = {
                "success": True,
                "total": total,
                "generated": generated,
                "failed": failed,
                "message": f"完成缩略图生成：成功 {generated} 个，失败 {failed} 个"
            }
            
            logger.info(f"[CloudImg123-History] {result['message']}")
            return result
            
        except Exception as e:
            logger.error(f"[CloudImg123-History] 批量生成缩略图异常: {str(e)}")
            return {
                "success": False,
                "total": 0,
                "generated": 0,
                "failed": 0,
                "message": f"批量生成缩略图失败: {str(e)}"
            }
    
    def get_thumbnail_cache_info(self) -> Dict[str, Any]:
        """
        获取缩略图缓存信息
        """
        try:
            return self.thumbnail_manager.get_cache_info()
        except Exception as e:
            logger.error(f"[CloudImg123-History] 获取缩略图缓存信息失败: {str(e)}")
            return {
                "total_count": 0,
                "total_size": 0,
                "cache_dir": str(self.thumbnail_manager.cache_dir),
                "error": str(e)
            }

    def get_record_by_hash(self, file_hash: str) -> Optional[UploadRecord]:
        """
        根据文件哈希获取记录
        """
        try:
            history = self._load_history()
            
            for record_data in history:
                if record_data.get("file_hash") == file_hash:
                    return UploadRecord.from_dict(record_data)
            
            return None
            
        except Exception as e:
            logger.error(f"[CloudImg123-History] 根据哈希获取记录异常: {str(e)}")
            return None

    def move_record_to_front(self, record_id: str) -> bool:
        """
        将指定记录移至历史记录最前面
        """
        try:
            history = self._load_history()
            
            # 找到要移动的记录
            record_to_move = None
            for i, record in enumerate(history):
                if record.get("id") == record_id:
                    record_to_move = history.pop(i)
                    break
            
            if not record_to_move:
                logger.warning(f"[CloudImg123-History] 未找到要移动的记录: {record_id}")
                return False
            
            # 将记录移至最前面
            history.insert(0, record_to_move)
            
            # 保存历史记录
            success = self._save_history(history)
            if success:
                logger.info(f"[CloudImg123-History] 记录移至最前面成功: {record_id}")
            else:
                logger.error(f"[CloudImg123-History] 记录移动保存失败: {record_id}")
            
            return success
                
        except Exception as e:
            logger.error(f"[CloudImg123-History] 移动记录异常: {str(e)}")
            return False

    def add_or_update_record(self, record: UploadRecord, check_duplicate: bool = True) -> bool:
        """
        添加或更新记录，支持重复检测和置顶处理
        """
        try:
            history = self._load_history()
            
            # 检查重复（基于哈希值）
            if check_duplicate and record.file_hash:
                existing_record = None
                existing_index = -1
                
                for i, record_data in enumerate(history):
                    if record_data.get("file_hash") == record.file_hash:
                        existing_record = record_data
                        existing_index = i
                        break
                
                # 如果存在重复，先删除旧记录
                if existing_record:
                    history.pop(existing_index)
                    logger.info(f"[CloudImg123-History] 发现重复记录，将替换: {record.filename}")
            
            # 添加新记录到开头
            history.insert(0, record.to_dict())
            
            # 限制历史记录数量
            if self.limit > 0 and len(history) > self.limit:
                history = history[:self.limit]
                logger.info(f"[CloudImg123-History] 历史记录超出限制，保留最新 {self.limit} 条")
            
            # 保存到文件
            success = self._save_history(history)
            if success:
                logger.info(f"[CloudImg123-History] 添加/更新历史记录成功: {record.filename}")
            else:
                logger.error(f"[CloudImg123-History] 添加/更新历史记录失败: {record.filename}")
                
            return success
            
        except Exception as e:
            logger.error(f"[CloudImg123-History] 添加/更新历史记录异常: {str(e)}")
            return False