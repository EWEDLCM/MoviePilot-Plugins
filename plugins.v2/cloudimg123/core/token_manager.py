import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from app.core.config import settings
from app.log import logger


class TokenManager:
    """
    Token管理器，负责token的持久化存储和有效期管理
    """
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.token_file = config_path / "token_data.json"
        
        # Token有效期：30天
        self.token_validity_days = 30
        # 提前更新时间：提前1天更新token
        self.refresh_buffer_days = 1
        
        # 确保配置目录存在
        if not self.config_path.exists():
            self.config_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"[CloudImg123-Token] 创建配置目录: {self.config_path}")

    def _log(self, level: str, message: str):
        """
        安全的日志记录方法
        """
        log_message = f"[CloudImg123-Token] {message}"
        if level == "info":
            logger.info(log_message)
        elif level == "error":
            logger.error(log_message)
        elif level == "warning":
            logger.warning(log_message)

    def _load_token_data(self) -> Dict[str, Any]:
        """
        从文件加载token数据
        """
        try:
            if not self.token_file.exists():
                return {}
            
            with open(self.token_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
                
        except Exception as e:
            logger.error(f"[CloudImg123-Token] 加载token数据失败: {str(e)}")
            return {}

    def _save_token_data(self, token_data: Dict[str, Any]) -> bool:
        """
        保存token数据到文件
        """
        try:
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(token_data, f, ensure_ascii=False, indent=2)
            return True
            
        except Exception as e:
            logger.error(f"[CloudImg123-Token] 保存token数据失败: {str(e)}")
            return False

    def get_stored_token(self) -> Optional[str]:
        """
        获取存储的有效token
        """
        try:
            token_data = self._load_token_data()
            
            if not token_data:
                logger.info(f"[CloudImg123-Token] 未找到存储的token数据")
                return None
            
            access_token = token_data.get("access_token")
            created_time = token_data.get("created_time")
            
            if not access_token or not created_time:
                logger.warning(f"[CloudImg123-Token] token数据不完整")
                return None
            
            # 检查token是否过期
            created_timestamp = float(created_time)
            current_timestamp = time.time()
            
            # 计算token年龄（天数）
            token_age_days = (current_timestamp - created_timestamp) / (24 * 3600)
            
            # 检查是否需要刷新（提前1天刷新）
            refresh_threshold_days = self.token_validity_days - self.refresh_buffer_days
            
            if token_age_days >= self.token_validity_days:
                logger.warning(f"[CloudImg123-Token] token已过期，年龄: {token_age_days:.1f}天")
                return None
            elif token_age_days >= refresh_threshold_days:
                logger.info(f"[CloudImg123-Token] token即将过期，年龄: {token_age_days:.1f}天，建议刷新")
                # 仍然返回token，但会在日志中提示需要刷新
                return access_token
            else:
                logger.info(f"[CloudImg123-Token] 使用有效的存储token，年龄: {token_age_days:.1f}天")
                return access_token
                
        except Exception as e:
            logger.error(f"[CloudImg123-Token] 获取存储token异常: {str(e)}")
            return None

    def save_token(self, access_token: str, expires_in: int = None) -> bool:
        """
        保存新的token到存储
        
        :param access_token: 访问令牌
        :param expires_in: 过期时间（秒），如果不提供则使用30天
        """
        try:
            current_time = time.time()
            
            # 计算过期时间戳
            if expires_in:
                expires_at = current_time + expires_in
            else:
                # 默认30天
                expires_at = current_time + (self.token_validity_days * 24 * 3600)
            
            token_data = {
                "access_token": access_token,
                "created_time": current_time,
                "expires_at": expires_at,
                "created_date": datetime.fromtimestamp(current_time).isoformat(),
                "expires_date": datetime.fromtimestamp(expires_at).isoformat(),
                "validity_days": self.token_validity_days
            }
            
            success = self._save_token_data(token_data)
            
            if success:
                logger.info(f"[CloudImg123-Token] token保存成功，有效期至: {token_data['expires_date']}")
            else:
                logger.error(f"[CloudImg123-Token] token保存失败")
                
            return success
            
        except Exception as e:
            logger.error(f"[CloudImg123-Token] 保存token异常: {str(e)}")
            return False

    def is_token_valid(self) -> bool:
        """
        检查当前存储的token是否有效
        """
        try:
            token_data = self._load_token_data()
            
            if not token_data:
                return False
            
            created_time = token_data.get("created_time")
            if not created_time:
                return False
            
            current_timestamp = time.time()
            created_timestamp = float(created_time)
            
            # 计算token年龄
            token_age_days = (current_timestamp - created_timestamp) / (24 * 3600)
            
            return token_age_days < self.token_validity_days
            
        except Exception as e:
            logger.error(f"[CloudImg123-Token] 检查token有效性异常: {str(e)}")
            return False

    def should_refresh_token(self) -> bool:
        """
        检查是否应该刷新token（即将过期）
        """
        try:
            token_data = self._load_token_data()
            
            if not token_data:
                return True  # 没有token，需要获取新的
            
            created_time = token_data.get("created_time")
            if not created_time:
                return True
            
            current_timestamp = time.time()
            created_timestamp = float(created_time)
            
            # 计算token年龄
            token_age_days = (current_timestamp - created_timestamp) / (24 * 3600)
            
            # 如果超过29天，建议刷新
            refresh_threshold_days = self.token_validity_days - self.refresh_buffer_days
            
            return token_age_days >= refresh_threshold_days
            
        except Exception as e:
            logger.error(f"[CloudImg123-Token] 检查token刷新需求异常: {str(e)}")
            return True

    def clear_token(self) -> bool:
        """
        清除存储的token
        """
        try:
            if self.token_file.exists():
                self.token_file.unlink()
                logger.info(f"[CloudImg123-Token] token数据已清除")
                return True
            else:
                logger.info(f"[CloudImg123-Token] 无token数据需要清除")
                return True
                
        except Exception as e:
            logger.error(f"[CloudImg123-Token] 清除token数据异常: {str(e)}")
            return False

    def get_token_info(self) -> Dict[str, Any]:
        """
        获取token的详细信息
        """
        try:
            token_data = self._load_token_data()
            
            if not token_data:
                return {
                    "has_token": False,
                    "is_valid": False,
                    "should_refresh": True
                }
            
            created_time = token_data.get("created_time")
            if not created_time:
                return {
                    "has_token": False,
                    "is_valid": False,
                    "should_refresh": True
                }
            
            current_timestamp = time.time()
            created_timestamp = float(created_time)
            
            # 计算token年龄
            token_age_days = (current_timestamp - created_timestamp) / (24 * 3600)
            remaining_days = self.token_validity_days - token_age_days
            
            is_valid = token_age_days < self.token_validity_days
            should_refresh = token_age_days >= (self.token_validity_days - self.refresh_buffer_days)
            
            return {
                "has_token": True,
                "is_valid": is_valid,
                "should_refresh": should_refresh,
                "token": token_data.get("access_token"),
                "age_days": round(token_age_days, 1),
                "remaining_days": round(remaining_days, 1),
                "created_date": token_data.get("created_date"),
                "expires_date": token_data.get("expires_date")
            }
            
        except Exception as e:
            logger.error(f"[CloudImg123-Token] 获取token信息异常: {str(e)}")
            return {
                "has_token": False,
                "is_valid": False,
                "should_refresh": True,
                "error": str(e)
            }

    def set_manual_token(self, access_token: str) -> bool:
        """
        手动设置token（用于测试或直接输入已有token）
        """
        try:
            # 保存手动设置的token，标记为手动设置
            current_time = time.time()
            expires_at = current_time + (self.token_validity_days * 24 * 3600)
            
            token_data = {
                "access_token": access_token,
                "created_time": current_time,
                "expires_at": expires_at,
                "created_date": datetime.fromtimestamp(current_time).isoformat(),
                "expires_date": datetime.fromtimestamp(expires_at).isoformat(),
                "validity_days": self.token_validity_days,
                "manual_set": True  # 标记为手动设置
            }
            
            success = self._save_token_data(token_data)
            
            if success:
                logger.info(f"[CloudImg123-Token] 手动token设置成功，有效期至: {token_data['expires_date']}")
            else:
                logger.error(f"[CloudImg123-Token] 手动token设置失败")
                
            return success
            
        except Exception as e:
            logger.error(f"[CloudImg123-Token] 手动设置token异常: {str(e)}")
            return False