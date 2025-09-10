import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from app.log import logger
from .api_client import CloudAPI123
from .history_manager import HistoryManager, UploadRecord


class UploadManager:
    """
    上传管理器
    """
    
    def __init__(self, api_client: CloudAPI123, history_manager: HistoryManager):
        self.api_client = api_client
        self.history_manager = history_manager
        
        # 支持的图片格式
        self.supported_formats = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', 
            '.tiff', '.tif', '.ico', '.svg'
        }

    def _log(self, level: str, message: str):
        """
        安全的日志记录方法
        """
        log_message = f"[CloudImg123-Upload] {message}"
        if level == "info":
            logger.info(log_message)
        elif level == "error":
            logger.error(log_message)
        elif level == "warning":
            logger.warning(log_message)

    def _is_image_file(self, file_path: str) -> bool:
        """
        检查文件是否为支持的图片格式
        """
        try:
            file_ext = Path(file_path).suffix.lower()
            return file_ext in self.supported_formats
        except Exception as e:
            logger.error(f"[CloudImg123-Upload] 检查文件格式异常: {str(e)}")
            return False

    def _validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        验证文件是否可以上传
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {"valid": False, "message": "文件不存在"}

            # 检查是否为文件
            if not os.path.isfile(file_path):
                return {"valid": False, "message": "不是有效的文件"}

            # 检查文件大小（最大100MB）
            file_size = os.path.getsize(file_path)
            max_size = 100 * 1024 * 1024  # 100MB
            if file_size > max_size:
                return {"valid": False, "message": f"文件过大，最大支持 {max_size // (1024*1024)}MB"}

            # 检查文件格式
            if not self._is_image_file(file_path):
                return {"valid": False, "message": "不支持的文件格式，仅支持图片文件"}

            # 检查文件是否可读
            try:
                with open(file_path, 'rb') as f:
                    f.read(1)
            except Exception:
                return {"valid": False, "message": "文件无法读取"}

            return {"valid": True, "size": file_size}

        except Exception as e:
            logger.error(f"[CloudImg123-Upload] 文件验证异常: {str(e)}")
            return {"valid": False, "message": f"文件验证异常: {str(e)}"}

    def _generate_formats(self, download_url: str, filename: str) -> Dict[str, str]:
        """
        生成各种格式的链接
        """
        try:
            # 获取不带扩展名的文件名作为alt文本
            alt_text = Path(filename).stem
            
            formats = {
                "url": download_url,
                "html": f'<img src="{download_url}" alt="{alt_text}" title="{filename}">',
                "markdown": f'![{alt_text}]({download_url} "{filename}")',
                "bbcode": f'[img]{download_url}[/img]'
            }
            
            logger.info(f"[CloudImg123-Upload] 生成链接格式完成: {filename}")
            return formats
            
        except Exception as e:
            logger.error(f"[CloudImg123-Upload] 生成链接格式异常: {str(e)}")
            return {
                "url": download_url,
                "html": f'<img src="{download_url}" alt="{filename}">',
                "markdown": f'![{filename}]({download_url})',
                "bbcode": f'[img]{download_url}[/img]'
            }

    async def upload_image(self, file_path: str, filename: str = None, file_hash: str = None) -> Dict[str, Any]:
        """
        增强的上传方法，支持哈希检测
        """
        try:
            logger.info(f"[CloudImg123-Upload] 开始处理上传请求: {file_path}")
            
            # 检查重复上传（基于哈希值）
            if file_hash:
                duplicate_record = self.history_manager.get_record_by_hash(file_hash)
                if duplicate_record:
                    logger.info(f"[CloudImg123-Upload] 检测到重复文件，返回历史记录: {filename}")
                    
                    # 将重复记录移至最前面
                    self.history_manager.move_record_to_front(duplicate_record.id)
                    
                    return {
                        "success": True,
                        "message": "文件已存在，返回历史记录",
                        "is_duplicate": True,
                        "data": duplicate_record.to_dict()
                    }
            
            # 验证文件
            validation = self._validate_file(file_path)
            if not validation["valid"]:
                logger.error(f"[CloudImg123-Upload] 文件验证失败: {validation['message']}")
                return {"success": False, "message": validation["message"]}

            # 确定文件名
            if not filename:
                filename = os.path.basename(file_path)
            
            logger.info(f"[CloudImg123-Upload] 开始上传文件: {filename}，大小: {validation['size']} bytes")

            # 调用API上传
            upload_result = await self.api_client.upload_file(file_path, filename)
            
            if not upload_result.get("success"):
                logger.error(f"[CloudImg123-Upload] API上传失败: {upload_result.get('message')}")
                return upload_result

            # 提取上传结果
            file_id = upload_result.get("file_id")
            download_url = upload_result.get("download_url")
            user_self_url = upload_result.get("user_self_url")
            file_size = upload_result.get("size", validation["size"])
            upload_time_str = upload_result.get("upload_time")

            if not download_url:
                logger.error(f"[CloudImg123-Upload] 上传成功但未获取到下载链接")
                return {"success": False, "message": "上传成功但未获取到下载链接"}

            # 生成各种格式链接
            formats = self._generate_formats(download_url, filename)

            # 创建上传记录（包含哈希值）
            record = UploadRecord(
                filename=filename,
                file_id=file_id,
                download_url=download_url,
                user_self_url=user_self_url,
                file_size=file_size,
                upload_time=upload_time_str or datetime.now().isoformat(),
                formats=formats,
                file_hash=file_hash  # 保存哈希值
            )

            # 保存到历史记录（使用新的增强方法）
            save_success = self.history_manager.add_or_update_record(record, check_duplicate=True)
            if not save_success:
                logger.warning(f"[CloudImg123-Upload] 上传成功但保存历史记录失败: {filename}")

            logger.info(f"[CloudImg123-Upload] 文件上传完成: {filename}")
            
            # 返回完整结果
            result = {
                "success": True,
                "message": "上传成功",
                "is_duplicate": False,
                "data": {
                    "id": record.id,
                    "filename": filename,
                    "file_id": file_id,
                    "file_hash": file_hash,
                    "download_url": download_url,
                    "user_self_url": user_self_url,
                    "file_size": file_size,
                    "upload_time": record.upload_time,
                    "formats": formats
                }
            }
            
            return result

        except Exception as e:
            logger.error(f"[CloudImg123-Upload] 上传图片异常: {str(e)}")
            return {"success": False, "message": f"上传异常: {str(e)}"}

    async def upload_multiple_images(self, file_paths: list, callback=None) -> Dict[str, Any]:
        """
        批量上传多个图片
        """
        try:
            results = []
            success_count = 0
            
            logger.info(f"[CloudImg123-Upload] 开始批量上传，文件数量: {len(file_paths)}")
            
            for i, file_path in enumerate(file_paths):
                try:
                    result = await self.upload_image(file_path)
                    results.append(result)
                    
                    if result.get("success"):
                        success_count += 1
                    
                    # 调用回调函数报告进度
                    if callback:
                        progress = (i + 1) / len(file_paths) * 100
                        callback(progress, result)
                        
                except Exception as e:
                    error_result = {"success": False, "message": f"上传异常: {str(e)}", "file_path": file_path}
                    results.append(error_result)
                    logger.error(f"[CloudImg123-Upload] 批量上传中单个文件失败: {file_path}, {str(e)}")

            logger.info(f"[CloudImg123-Upload] 批量上传完成，成功: {success_count}/{len(file_paths)}")
            
            return {
                "success": True,
                "message": f"批量上传完成，成功 {success_count}/{len(file_paths)} 个文件",
                "data": {
                    "total": len(file_paths),
                    "success_count": success_count,
                    "results": results
                }
            }

        except Exception as e:
            logger.error(f"[CloudImg123-Upload] 批量上传异常: {str(e)}")
            return {"success": False, "message": f"批量上传异常: {str(e)}"}

    def get_supported_formats(self) -> list:
        """
        获取支持的文件格式列表
        """
        return list(self.supported_formats)

    def test_upload_capability(self) -> Dict[str, Any]:
        """
        测试上传能力
        """
        try:
            # 测试API连接
            if not self.api_client.test_connection():
                return {"success": False, "message": "API连接测试失败"}

            # 检查历史管理器
            if not self.history_manager:
                return {"success": False, "message": "历史管理器未初始化"}

            # 测试数据目录写权限
            test_file = self.history_manager.data_path / "test_write.tmp"
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                test_file.unlink()  # 删除测试文件
            except Exception:
                return {"success": False, "message": "数据目录无写权限"}

            return {"success": True, "message": "上传功能正常"}

        except Exception as e:
            logger.error(f"[CloudImg123-Upload] 测试上传能力异常: {str(e)}")
            return {"success": False, "message": f"测试异常: {str(e)}"}