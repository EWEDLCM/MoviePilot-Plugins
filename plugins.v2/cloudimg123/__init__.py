from typing import Any, List, Dict, Tuple, Optional
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from app.core.config import settings
from app.core.event import eventmanager, Event
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import EventType
from starlette.requests import Request
from starlette.responses import FileResponse, StreamingResponse
from fastapi import UploadFile, Form

from .core.api_client import CloudAPI123
from .core.upload_manager import UploadManager
from .core.history_manager import HistoryManager


class CloudImg123(_PluginBase):
    # 插件名称
    plugin_name = "123云盘图床"
    # 插件描述
    plugin_desc = "123云盘图床插件，支持图片上传和多格式链接生成"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/EWEDLCM/MoviePilot-Plugins/main/icons/cloudimg123.png"
    # 插件版本
    plugin_version = "1.3.0"
    # 插件作者
    plugin_author = "EWEDL"
    # 作者主页
    author_url = "https://github.com/EWEDLCM"
    # 插件配置项ID前缀
    plugin_config_prefix = "cloudimg123_"
    # 加载顺序
    plugin_order = 2
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enabled = False
    _client_id = ""
    _client_secret = ""
    _history_limit = 50
    _debug = False
    
    # 核心组件
    _api = None
    _upload_manager = None
    _history_manager = None
    
    # 数据目录
    _config_path = None

    def init_plugin(self, config: dict = None):
        """
        初始化插件
        """
        try:
            # 处理配置
            if config:
                self._enabled = config.get("enabled", False)
                self._client_id = config.get("client_id", "")
                self._client_secret = config.get("client_secret", "")
                self._history_limit = config.get("history_limit", 50)
                self._debug = config.get("debug", False)

            # 设置配置目录（使用/config/plugins/cloudimg123）
            if hasattr(settings, 'CONFIG_PATH'):
                # 使用MoviePilot的配置目录
                self._config_path = Path(settings.CONFIG_PATH) / "plugins" / "cloudimg123"
            else:
                # 回退到插件目录下的config文件夹
                self._config_path = Path(__file__).parent / "config"
            
            if not self._config_path.exists():
                self._config_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"[CloudImg123] 创建配置目录: {self._config_path}")

            # 初始化核心组件（配置处理完成后）
            if self._enabled and self._client_id and self._client_secret:
                try:
                    # 初始化API客户端
                    self._api = CloudAPI123(
                        client_id=self._client_id,
                        client_secret=self._client_secret,
                        config_path=self._config_path,
                        debug=self._debug
                    )
                    
                    # 初始化历史管理器
                    self._history_manager = HistoryManager(
                        config_path=self._config_path,
                        limit=0 if self._history_limit >= 200 else self._history_limit
                    )
                    
                    # 初始化上传管理器
                    self._upload_manager = UploadManager(
                        api_client=self._api,
                        history_manager=self._history_manager
                    )
                    
                    logger.info(f"[CloudImg123] 插件初始化成功")
                except Exception as e:
                    logger.error(f"[CloudImg123] 核心组件初始化失败: {str(e)}")
                    self._api = None
                    self._upload_manager = None
                    self._history_manager = None
            else:
                if self._enabled:
                    logger.warning(f"[CloudImg123] 插件已启用但配置不完整，请检查Client ID和Client Secret")
                else:
                    logger.info(f"[CloudImg123] 插件未启用")
                    
        except Exception as e:
            logger.error(f"[CloudImg123] 插件初始化异常: {str(e)}")

    def get_state(self) -> bool:
        """
        获取插件状态
        """
        state = self._enabled and self._api is not None
        logger.info(f"[CloudImg123] 插件状态: enabled={self._enabled}, api_ready={self._api is not None}, state={state}")
        return state

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        """
        定义远程命令
        """
        return [{
            "cmd": "/cloudimg123_upload",
            "event": EventType.PluginAction,
            "desc": "上传图片到123云盘",
            "category": "图床",
            "data": {
                "action": "upload_image"
            }
        }]

    def get_api(self) -> List[Dict[str, Any]]:
        """
        获取插件API
        """
        return [
            {
                "path": "/upload",
                "endpoint": self.upload_image,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "上传图片",
                "description": "上传图片到123云盘并返回各种格式链接",
            },
            {
                "path": "/history",
                "endpoint": self.get_history,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取上传历史",
                "description": "获取用户上传历史记录",
            },
            {
                "path": "/statistics",
                "endpoint": self.get_statistics,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取统计信息",
                "description": "获取上传统计信息",
            },
            {
                "path": "/status",
                "endpoint": self.get_status,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取系统状态",
                "description": "获取插件系统状态",
            },
            {
                "path": "/chart",
                "endpoint": self.get_chart_data,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取图表数据",
                "description": "获取上传趋势图表数据",
            },
            {
                "path": "/history/<record_id>",
                "endpoint": self.delete_history,
                "methods": ["DELETE"],
                "auth": "bear",
                "summary": "删除历史记录",
                "description": "删除指定的历史记录",
            },
                        {
                "path": "/delete",
                "endpoint": self.delete_multiple_records,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "批量删除记录",
                "description": "接收JSON格式的文件ID列表，批量删除对应的历史记录",
            },
            {
                "path": "/test_connection",
                "endpoint": self.test_connection,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "测试API连接",
                "description": "测试123云盘API连接和凭据有效性",
            },
            {
                "path": "/token_info",
                "endpoint": self.get_token_info,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取Token信息",
                "description": "获取当前Token的详细信息和状态",
            },
            {
                "path": "/thumbnail/generate_all",
                "endpoint": self.generate_all_thumbnails,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "生成所有缩略图",
                "description": "为所有历史记录生成缩略图",
            },
            {
                "path": "/thumbnail/generate",
                "endpoint": self.generate_thumbnail,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "生成单个缩略图",
                "description": "为指定文件生成缩略图",
            },
            {
                "path": "/thumbnail/{file_path:path}",
                "endpoint": self.serve_thumbnail,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "提供缩略图文件服务",
                "description": "提供缩略图文件的API访问",
            }
        ]

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        插件配置页面 - 使用Vue联邦模块，返回默认配置
        """
        # 使用Vue联邦模块，返回空表单和默认配置
        return [], {
            "enabled": False,
            "client_id": "",
            "client_secret": "",
            "history_limit": 50,
            "debug": False
        } 

    def get_page(self) -> List[dict]:
        """
        插件详情页面，使用Vue模式时返回None
        """
        logger.info(f"[CloudImg123] 调用get_page方法，返回None以使用Vue模式")
        return None

    def get_render_mode(self) -> Tuple[str, str]:
        """
        获取插件渲染模式
        使用Vue模式和本地联邦模块
        """
        return "vue", "dist/assets"

    async def upload_image(self, file: UploadFile, file_hash: str = Form(None)) -> dict:
        """
        上传图片API接口 - 处理HTTP请求（带缓存管理和重复检测）
        """
        try:
            logger.info(f"[CloudImg123] 收到上传请求")
            
            if not self._upload_manager:
                logger.error(f"[CloudImg123] 上传管理器未初始化")
                return {"success": False, "message": "插件未正确初始化"}

            # Use file.filename directly
            filename = file.filename
            if not filename: # Check if filename is available
                logger.error(f"[CloudImg123] 文件名缺失")
                return {"success": False, "message": "文件名缺失"}

            logger.info(f"[CloudImg123] 开始处理上传文件: {filename}, 文件哈希: {file_hash}")
            
            # Save temporary file from UploadFile
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as temp_file:
                # Read content from UploadFile asynchronously
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Call upload manager with temp file path, filename, and file hash
                result = await self._upload_manager.upload_image(temp_file_path, filename, file_hash)
                
                if result.get("success"):
                    logger.info(f"[CloudImg123] 文件上传成功: {result.get('filename')}")
                else:
                    logger.error(f"[CloudImg123] 文件上传失败: {result.get('message')}")
                    
                return result
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"[CloudImg123] 清理临时文件失败: {temp_file_path}, {str(e)}")
            
        except Exception as e:
            logger.error(f"[CloudImg123] 上传图片异常: {str(e)}")
            return {"success": False, "message": f"上传异常: {str(e)}"}

    def get_history(self, limit: int = None, with_thumbnails: bool = True) -> dict:
        """
        获取上传历史API接口
        """
        try:
            if not self._history_manager:
                logger.error(f"[CloudImg123] 历史管理器未初始化")
                return {"success": False, "message": "插件未正确初始化"}

            history_limit = limit or self._history_limit
            
            # 根据参数决定是否返回缩略图信息
            if with_thumbnails:
                history = self._history_manager.get_history_with_thumbnails(limit=history_limit)
            else:
                history = self._history_manager.get_history(limit=history_limit)
            
            logger.info(f"[CloudImg123] 获取历史记录，数量: {len(history)}, 缩略图: {with_thumbnails}")
            return {"success": True, "data": history}
            
        except Exception as e:
            logger.error(f"[CloudImg123] 获取历史记录异常: {str(e)}")
            return {"success": False, "message": f"获取历史异常: {str(e)}"}

    def delete_history(self, record_id: str) -> dict:
        """
        删除历史记录API接口（带缓存管理）
        """
        try:
            if not self._history_manager:
                logger.error(f"[CloudImg123] 历史管理器未初始化")
                return {"success": False, "message": "插件未正确初始化"}

            result = self._history_manager.delete_record(record_id)
            
            if result:
                logger.info(f"[CloudImg123] 删除历史记录成功: {record_id}")
            else:
                logger.warning(f"[CloudImg123] 删除历史记录失败: {record_id}")
                
            return {"success": result, "message": "删除成功" if result else "删除失败"}
            
        except Exception as e:
            logger.error(f"[CloudImg123] 删除历史记录异常: {str(e)}")
            return {"success": False, "message": f"删除异常: {str(e)}"}

    @eventmanager.register(EventType.PluginAction)
    def on_plugin_action(self, event: Event):
        """
        监听插件动作事件
        """
        if not event:
            return
        event_data = event.event_data or {}
        if event_data.get("action") != "upload_image":
            return

        # 这里可以处理远程命令触发的上传操作
        logger.info(f"[CloudImg123] 收到上传图片命令")

    def stop_service(self):
        """
        退出插件
        """
        try:
            logger.info(f"[CloudImg123] 插件正在停止")
            # 清理资源
            self._api = None
            self._upload_manager = None
            self._history_manager = None
        except Exception as e:
            logger.error(f"[CloudImg123] 插件停止异常: {str(e)}")

    def get_statistics(self) -> dict:
        """
        获取统计信息 API接口
        """
        try:
            if not self._history_manager:
                logger.error(f"[CloudImg123] 历史管理器未初始化")
                return {
                    "success": True,
                    "data": {
                        "totalUploads": 0,
                        "totalSize": 0,
                        "todayUploads": 0,
                        "averageSize": 0
                    }
                }

            stats = self._history_manager.get_statistics()
            
            # 计算今日上传数量
            today_uploads = 0
            history = self._history_manager.get_history(limit=100)  # 获取最近100条记录
            today = datetime.now().date()
            
            for record in history:
                try:
                    # 处理不同的时间格式
                    upload_time_str = record['upload_time']
                    
                    # 如果时间字符串包含时区信息（Z或+/-），需要特殊处理
                    if 'Z' in upload_time_str:
                        upload_time_str = upload_time_str.replace('Z', '+00:00')
                    
                    # 尝试解析ISO格式时间，处理包含微秒的情况
                    upload_date = datetime.fromisoformat(upload_time_str).date()
                    if upload_date == today:
                        today_uploads += 1
                except (ValueError, TypeError) as e:
                    logger.warning(f"[CloudImg123] 解析时间失败: {record['upload_time']}, 错误: {str(e)}")
                    continue
            
            # 计算平均大小
            average_size = stats['total_size'] // stats['total_count'] if stats['total_count'] > 0 else 0
            
            result = {
                "totalUploads": int(stats['total_count']) if stats['total_count'] else 0,
                "totalSize": int(stats['total_size']) if stats['total_size'] else 0,
                "todayUploads": int(today_uploads),
                "averageSize": int(average_size)
            }
            
            logger.info(f"[CloudImg123] 获取统计信息成功: {result}")
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"[CloudImg123] 获取统计信息异常: {str(e)}")
            return {
                "success": True,
                "data": {
                    "totalUploads": 0,
                    "totalSize": 0,
                    "todayUploads": 0,
                    "averageSize": 0
                }
            }

    def get_status(self) -> dict:
        """
        获取系统状态 API接口
        """
        try:
            api_status = False
            token_status = False
            storage_status = True  # 默认存储正常
            
            # 检查API状态
            if self._api:
                try:
                    # 简单的连接测试
                    api_status = True
                except:
                    api_status = False
            
            # 检查Token状态
            if self._api and hasattr(self._api, 'token_manager'):
                try:
                    token_info = self._api.token_manager.get_token_info()
                    token_status = token_info.get('is_valid', False)
                except:
                    token_status = False
            
            # 检查存储状态
            try:
                if self._config_path and self._config_path.exists():
                    # 测试写权限
                    test_file = self._config_path / "test_write.tmp"
                    with open(test_file, 'w') as f:
                        f.write("test")
                    test_file.unlink()
                    storage_status = True
                else:
                    storage_status = False
            except:
                storage_status = False
            
            result = {
                "api": api_status,
                "token": token_status,
                "storage": storage_status
            }
            
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"[CloudImg123] 获取系统状态异常: {str(e)}")
            return {"success": False, "message": f"获取状态异常: {str(e)}"}

    def get_chart_data(self, days: int = 7) -> dict:
        """
        获取图表数据 API接口
        """
        try:
            if not self._history_manager:
                logger.error(f"[CloudImg123] 历史管理器未初始化")
                return {"success": False, "message": "插件未正确初始化"}

            # 获取历史记录
            history = self._history_manager.get_history(limit=500)  # 获取足够的记录
            
            # 生成指定天数的数据
            chart_data = []
            today = datetime.now().date()
            
            for i in range(days):
                target_date = today - timedelta(days=days - 1 - i)
                uploads_count = 0
                
                for record in history:
                    try:
                        upload_date = datetime.fromisoformat(record.upload_time.replace('Z', '+00:00')).date()
                        if upload_date == target_date:
                            uploads_count += 1
                    except:
                        continue
                
                chart_data.append({
                    "date": target_date.strftime('%Y-%m-%d'),
                    "uploads": uploads_count
                })
            
            result = {"chart": chart_data}
            
            logger.info(f"[CloudImg123] 获取图表数据成功，天数: {days}")
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"[CloudImg123] 获取图表数据异常: {str(e)}")
            return {"success": False, "message": f"获取图表异常: {str(e)}"}

    
    async def delete_multiple_records(self, request: Request) -> dict:
        """
        批量删除记录 API接口（POST方法）
        接收JSON格式的文件ID列表进行删除
        """
        try:
            if not self._history_manager:
                logger.error(f"[CloudImg123] 历史管理器未初始化")
                return {"success": False, "message": "插件未正确初始化"}

            # 直接解析JSON请求体获取文件列表
            try:
                data = await request.json()
                logger.info(f"[CloudImg123] 收到删除请求，数据: {data}")
                
                # 获取文件ID列表
                file_ids = data.get('file_ids', [])
                
                if not file_ids:
                    logger.error(f"[CloudImg123] 请求中缺少file_ids参数")
                    return {"success": False, "message": "没有指定要删除的记录"}
                
                # 确保file_ids是列表
                if isinstance(file_ids, str):
                    try:
                        file_ids = json.loads(file_ids)
                    except json.JSONDecodeError:
                        file_ids = [file_ids]
                
                logger.info(f"[CloudImg123] 准备删除文件列表: {file_ids} (共{len(file_ids)}个)")
                
            except Exception as e:
                logger.error(f"[CloudImg123] 解析请求JSON失败: {str(e)}")
                return {"success": False, "message": "请求格式错误"}
            
            # 执行批量删除
            deleted_count = 0
            failed_items = []
            
            for file_id in file_ids:
                try:
                    logger.info(f"[CloudImg123] 正在删除文件: {file_id}")
                    
                    # 通过file_id查找记录
                    record = self._history_manager.get_record_by_file_id(file_id)
                    if record:
                        logger.info(f"[CloudImg123] 找到记录: {record.filename} (ID: {record.id})")
                        
                        # 删除记录
                        if self._history_manager.delete_record(record.id):
                            deleted_count += 1
                            logger.info(f"[CloudImg123] 删除成功: {record.filename}")
                        else:
                            logger.error(f"[CloudImg123] 删除失败: {record.filename}")
                            failed_items.append(file_id)
                    else:
                        logger.warning(f"[CloudImg123] 未找到文件记录: {file_id}")
                        failed_items.append(file_id)
                        
                except Exception as e:
                    logger.error(f"[CloudImg123] 删除文件异常 {file_id}: {str(e)}")
                    failed_items.append(file_id)
            
            # 返回详细结果
            result = {
                "success": True,
                "message": f"删除完成，成功: {deleted_count}/{len(file_ids)}",
                "data": {
                    "total": len(file_ids),
                    "deleted": deleted_count,
                    "failed": len(failed_items),
                    "failed_items": failed_items
                }
            }
            
            logger.info(f"[CloudImg123] 批量删除完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"[CloudImg123] 批量删除异常: {str(e)}")
            return {"success": False, "message": f"删除异常: {str(e)}"}

    def test_connection(self, request: Request) -> dict:
        """
        测试API连接 API接口
        """
        try:
            logger.info(f"[CloudImg123] 收到测试连接请求")
            
            # 从请求中获取测试参数
            data = request.get_json() if hasattr(request, 'get_json') else {}
            client_id = data.get('client_id') or self._client_id
            client_secret = data.get('client_secret') or self._client_secret
            
            if not client_id or not client_secret:
                return {
                    "success": False, 
                    "message": "缺少Client ID或Client Secret",
                    "data": {
                        "api_status": False,
                        "token_obtained": False
                    }
                }
            
            # 创建临时API客户端进行连接测试
            from .core.api_client import CloudAPI123
            test_client = CloudAPI123(
                client_id=client_id,
                client_secret=client_secret,
                config_path=self._config_path,
                debug=self._debug
            )
            
            # 测试连接
            connection_success = test_client.test_connection()
            
            result_data = {
                "api_status": connection_success,
                "token_obtained": connection_success
            }
            
            if connection_success:
                logger.info(f"[CloudImg123] API连接测试成功")
                return {
                    "success": True,
                    "message": "连接测试成功",
                    "data": result_data
                }
            else:
                logger.warning(f"[CloudImg123] API连接测试失败")
                return {
                    "success": False,
                    "message": "连接测试失败，请检查Client ID和Client Secret",
                    "data": result_data
                }
                
        except Exception as e:
            logger.error(f"[CloudImg123] 测试连接异常: {str(e)}")
            return {
                "success": False, 
                "message": f"测试连接异常: {str(e)}",
                "data": {
                    "api_status": False,
                    "token_obtained": False
                }
            }

    def get_token_info(self) -> dict:
        """
        获取Token信息 API接口
        """
        try:
            if not self._api:
                logger.warning(f"[CloudImg123] API客户端未初始化")
                return {
                    "success": True,
                    "data": {
                        "has_token": False,
                        "is_valid": False,
                        "should_refresh": True,
                        "message": "API客户端未初始化"
                    }
                }
            
            token_info = self._api.get_token_info()
            logger.info(f"[CloudImg123] 获取Token信息成功")
            
            return {
                "success": True,
                "data": token_info
            }
            
        except Exception as e:
            logger.error(f"[CloudImg123] 获取Token信息异常: {str(e)}")
            return {
                "success": False,
                "message": f"获取Token信息异常: {str(e)}",
                "data": {
                    "has_token": False,
                    "is_valid": False,
                    "should_refresh": True,
                    "error": str(e)
                }
            }

    async def generate_thumbnail(self, request: Request) -> dict:
        """
        为指定文件生成缩略图 API接口（带缓存管理）
        """
        try:
            if not self._history_manager:
                logger.error(f"[CloudImg123] 历史管理器未初始化")
                return {"success": False, "message": "插件未正确初始化"}

            # 从请求体中获取file_id
            body = await request.json()
            file_id = body.get("file_id")
            
            if not file_id:
                return {"success": False, "message": "缺少file_id参数"}

            # 获取记录信息 - 使用file_id查找记录
            record = self._history_manager.get_record_by_file_id(file_id)
            if not record:
                logger.error(f"[CloudImg123] 未找到文件记录，file_id: {file_id}")
                return {"success": False, "message": f"未找到文件记录: {file_id}"}

            logger.info(f"[CloudImg123] 找到记录: {record.filename}, 开始生成缩略图")

            # 生成缩略图
            success = await self._history_manager.generate_thumbnail_for_record(
                file_id, record.download_url
            )
            
            if success:
                logger.info(f"[CloudImg123] 生成缩略图成功: {file_id}")
                return {"success": True, "message": "缩略图生成成功"}
            else:
                logger.warning(f"[CloudImg123] 生成缩略图失败: {file_id}")
                return {"success": False, "message": "缩略图生成失败"}
            
        except Exception as e:
            logger.error(f"[CloudImg123] 生成缩略图异常: {str(e)}")
            return {"success": False, "message": f"生成缩略图异常: {str(e)}"}

    async def generate_all_thumbnails(self) -> dict:
        """
        为所有历史记录生成缩略图 API接口（带缓存管理）
        """
        try:
            if not self._history_manager:
                logger.error(f"[CloudImg123] 历史管理器未初始化")
                return {"success": False, "message": "插件未正确初始化"}

            logger.info(f"[CloudImg123] 开始批量生成缩略图")
            result = await self._history_manager.generate_all_thumbnails()
            
            # 如果有生成缩略图，记录日志
            if result.get("generated", 0) > 0:
                logger.info(f"[CloudImg123] 生成了 {result.get('generated', 0)} 个缩略图")
            
            return result
            
        except Exception as e:
            logger.error(f"[CloudImg123] 批量生成缩略图异常: {str(e)}")
            return {
                "success": False,
                "message": f"批量生成缩略图异常: {str(e)}",
                "total": 0,
                "generated": 0,
                "failed": 0
            }

    def get_thumbnail_cache_info(self) -> dict:
        """
        获取缩略图缓存信息 API接口
        """
        try:
            if not self._history_manager:
                logger.error(f"[CloudImg123] 历史管理器未初始化")
                return {"success": False, "message": "插件未正确初始化"}

            cache_info = self._history_manager.get_thumbnail_cache_info()
            logger.info(f"[CloudImg123] 获取缩略图缓存信息成功")
            
            return {"success": True, "data": cache_info}
            
        except Exception as e:
            logger.error(f"[CloudImg123] 获取缩略图缓存信息异常: {str(e)}")
            return {"success": False, "message": f"获取缓存信息异常: {str(e)}"}

    def serve_thumbnail(self, file_path: str) -> dict:
        """
        提供缩略图文件服务
        """
        try:
            if not self._history_manager:
                logger.error(f"[CloudImg123] 历史管理器未初始化")
                return {"success": False, "message": "插件未正确初始化"}

            # 构建完整的缩略图文件路径
            config_path = self._config_path
            thumbnail_path = config_path / "cache" / "thumbnails" / file_path
            
            logger.info(f"[CloudImg123] 请求缩略图: {file_path}")
            logger.info(f"[CloudImg123] 构建路径: {thumbnail_path}")
            logger.info(f"[CloudImg123] 配置路径: {config_path}")
            
            # 检查文件是否存在
            if not thumbnail_path.exists():
                logger.warning(f"[CloudImg123] 缩略图文件不存在: {thumbnail_path}")
                # 检查cache目录是否存在
                cache_dir = self._config_path / "cache" / "thumbnails"
                if not cache_dir.exists():
                    logger.warning(f"[CloudImg123] 缩略图缓存目录不存在: {cache_dir}")
                else:
                    # 列出目录内容
                    try:
                        files = list(cache_dir.glob("*.webp"))
                        logger.info(f"[CloudImg123] 缓存目录中的文件: {[f.name for f in files[:5]]}")
                    except Exception as list_e:
                        logger.error(f"[CloudImg123] 列出缓存目录失败: {list_e}")
                return {"success": False, "message": "缩略图文件不存在"}
            
            # 检查文件大小
            file_size = thumbnail_path.stat().st_size
            logger.info(f"[CloudImg123] 缩略图文件大小: {file_size} bytes")
            
            if file_size == 0:
                logger.error(f"[CloudImg123] 缩略图文件为空: {thumbnail_path}")
                return {"success": False, "message": "缩略图文件为空"}
            
            # 检查文件是否在允许的目录内（安全检查）
            try:
                thumbnail_path.resolve().relative_to(self._config_path.resolve())
            except ValueError:
                logger.error(f"[CloudImg123] 非法的文件路径访问: {thumbnail_path}")
                return {"success": False, "message": "非法的文件路径访问"}
            
            logger.info(f"[CloudImg123] 提供缩略图文件: {thumbnail_path}")
            
            # 尝试直接读取文件内容
            try:
                with open(thumbnail_path, 'rb') as f:
                    file_content = f.read(1024)  # 读取前1KB验证文件
                    logger.info(f"[CloudImg123] 文件前1024字节: {len(file_content)} bytes")
                    if len(file_content) == 0:
                        logger.error(f"[CloudImg123] 文件读取为空")
            except Exception as read_error:
                logger.error(f"[CloudImg123] 读取文件失败: {read_error}")
            
            # 读取文件内容并返回base64编码
            try:
                with open(thumbnail_path, 'rb') as f:
                    file_content = f.read()
                    
                import base64
                base64_content = base64.b64encode(file_content).decode('utf-8')
                
                logger.info(f"[CloudImg123] 缩略图读取成功，大小: {len(file_content)} bytes")
                
                return {
                    "success": True,
                    "message": "缩略图获取成功",
                    "data": {
                        "content": base64_content,
                        "mime_type": "image/webp",
                        "size": len(file_content)
                    }
                }
                
            except Exception as read_error:
                logger.error(f"[CloudImg123] 读取缩略图文件失败: {read_error}")
                return {"success": False, "message": f"读取文件失败: {str(read_error)}"}
            
        except Exception as e:
            logger.error(f"[CloudImg123] 提供缩略图文件异常: {str(e)}")
            return {"success": False, "message": f"服务器错误: {str(e)}"}
