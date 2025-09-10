import os
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path

from app.log import logger


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小为人类可读格式
    """
    try:
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    except Exception:
        return f"{size_bytes} B"


def validate_image_file(file_path: str) -> Dict[str, Any]:
    """
    验证图片文件
    """
    try:
        # 支持的图片格式
        supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif', '.ico', '.svg'}
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return {"valid": False, "message": "文件不存在"}
        
        # 检查是否为文件
        if not os.path.isfile(file_path):
            return {"valid": False, "message": "不是有效的文件"}
        
        # 检查文件扩展名
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in supported_formats:
            return {"valid": False, "message": f"不支持的文件格式: {file_ext}"}
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        max_size = 100 * 1024 * 1024  # 100MB
        if file_size > max_size:
            return {"valid": False, "message": f"文件过大，最大支持100MB"}
        
        if file_size == 0:
            return {"valid": False, "message": "文件为空"}
        
        return {
            "valid": True,
            "size": file_size,
            "size_formatted": format_file_size(file_size),
            "extension": file_ext
        }
        
    except Exception as e:
        return {"valid": False, "message": f"文件验证异常: {str(e)}"}


def calculate_file_hash(file_path: str, algorithm: str = "md5") -> Optional[str]:
    """
    计算文件哈希值
    """
    try:
        if algorithm.lower() == "md5":
            hash_obj = hashlib.md5()
        elif algorithm.lower() == "sha256":
            hash_obj = hashlib.sha256()
        else:
            return None
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
        
    except Exception as e:
        logger.error(f"[CloudImg123-Utils] 计算文件哈希异常: {str(e)}")
        return None


def ensure_directory_exists(directory_path: Path, create_if_missing: bool = True) -> bool:
    """
    确保目录存在
    """
    try:
        if directory_path.exists():
            return directory_path.is_dir()
        
        if create_if_missing:
            directory_path.mkdir(parents=True, exist_ok=True)
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"[CloudImg123-Utils] 目录操作异常: {str(e)}")
        return False


def safe_filename(filename: str) -> str:
    """
    生成安全的文件名，移除不安全字符
    """
    try:
        # 定义不安全字符
        unsafe_chars = '<>:"/\\|?*'
        
        # 移除不安全字符
        safe_name = filename
        for char in unsafe_chars:
            safe_name = safe_name.replace(char, '_')
        
        # 移除开头和结尾的点和空格
        safe_name = safe_name.strip('. ')
        
        # 确保文件名不为空
        if not safe_name:
            safe_name = "unnamed_file"
        
        # 限制文件名长度
        if len(safe_name) > 200:
            name_part = Path(safe_name).stem[:190]
            ext_part = Path(safe_name).suffix
            safe_name = name_part + ext_part
        
        return safe_name
        
    except Exception as e:
        logger.error(f"[CloudImg123-Utils] 生成安全文件名异常: {str(e)}")
        return "unnamed_file"


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    获取文件的详细信息
    """
    try:
        if not os.path.exists(file_path):
            return {"exists": False}
        
        stat_info = os.stat(file_path)
        file_size = stat_info.st_size
        
        return {
            "exists": True,
            "path": file_path,
            "filename": os.path.basename(file_path),
            "size": file_size,
            "size_formatted": format_file_size(file_size),
            "extension": Path(file_path).suffix.lower(),
            "stem": Path(file_path).stem,
            "modified_time": stat_info.st_mtime,
            "is_file": os.path.isfile(file_path),
            "is_readable": os.access(file_path, os.R_OK),
        }
        
    except Exception as e:
        logger.error(f"[CloudImg123-Utils] 获取文件信息异常: {str(e)}")
        return {"exists": False, "error": str(e)}


def generate_thumbnail_name(original_filename: str, suffix: str = "_thumb") -> str:
    """
    生成缩略图文件名
    """
    try:
        path_obj = Path(original_filename)
        name_part = path_obj.stem
        ext_part = path_obj.suffix
        
        return f"{name_part}{suffix}{ext_part}"
        
    except Exception:
        return f"thumb_{original_filename}"


def parse_upload_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    解析上传响应数据
    """
    try:
        if not isinstance(response_data, dict):
            return {"success": False, "message": "无效的响应数据"}
        
        success = response_data.get("success", False)
        message = response_data.get("message", "")
        
        result = {
            "success": success,
            "message": message
        }
        
        if success and "data" in response_data:
            data = response_data["data"]
            result.update({
                "file_id": data.get("file_id"),
                "filename": data.get("filename"),
                "download_url": data.get("download_url"),
                "file_size": data.get("file_size"),
                "formats": data.get("formats", {})
            })
        
        return result
        
    except Exception as e:
        logger.error(f"[CloudImg123-Utils] 解析响应数据异常: {str(e)}")
        return {"success": False, "message": f"解析响应异常: {str(e)}"}


def create_error_response(message: str, code: int = None) -> Dict[str, Any]:
    """
    创建标准错误响应
    """
    response = {
        "success": False,
        "message": message
    }
    
    if code is not None:
        response["code"] = code
    
    return response


def create_success_response(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
    """
    创建标准成功响应
    """
    response = {
        "success": True,
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    return response