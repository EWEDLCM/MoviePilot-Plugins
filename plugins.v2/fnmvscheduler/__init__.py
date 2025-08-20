import time
import os
import threading
from typing import Any, List, Dict, Tuple, Optional
from pathlib import Path
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.base import JobLookupError

from app.core.config import settings
from app.core.event import eventmanager, Event
from app.helper.mediaserver import MediaServerHelper
from app.plugins import _PluginBase
from app.schemas import ServiceInfo, MediaServerLibrary, MediaServerConf, TransferInfo
from app.core.context import MediaInfo
from app.schemas.types import EventType
from app.schemas.file import FileItem
from app.log import logger

# 导入 fnapi
import app.modules.trimemedia.api as fnapi
from app.utils.url import UrlUtils


class fnmvscheduler(_PluginBase):
    # 插件名称
    plugin_name = "飞牛影视调度器"
    # 插件描述
    plugin_desc = "根据平台整理通告，按设置的模式智能触发飞牛影视媒体库扫描。"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/EWEDLCM/MoviePilot-Plugins/main/icons/fnmv.png"
    # 插件版本
    plugin_version = "1.5.0" 
    # 插件作者
    plugin_author = "EWEDL"
    # 作者主页
    author_url = "https://github.com/EWEDLCM/MoviePilot-Plugins"
    # 插件配置项ID前缀
    plugin_config_prefix = "fnmvscheduler_"
    # 加载顺序
    plugin_order = 100
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enabled = False
    _run_once = False
    _cloud_drive_mode = False
    _check_tasks_once = False
    _selected_mediaservers: List[str] = []
    _mediaserver_helper: Optional[MediaServerHelper] = None
    _scan_lock = threading.Lock()
    _task_scheduler: Optional[BackgroundScheduler] = None

    def __init__(self):
        super().__init__()
        logger.debug("【飞牛影视调度器】Fnmvscheduler 类 __init__ 方法被调用。")

    def init_plugin(self, config: dict = None):
        logger.debug("【飞牛影视调度器】init_plugin 方法被调用。")
        self.stop_service()  # Ensure a clean state on re-initialization
        if config:
            self._enabled = config.get("enabled", False)
            self._run_once = config.get("run_once", False)
            self._cloud_drive_mode = config.get("cloud_drive_mode", False)
            self._check_tasks_once = config.get("check_tasks_once", False)
            self._selected_mediaservers = config.get("selected_mediaservers", [])

        try:
            self._mediaserver_helper = MediaServerHelper()
        except Exception as e:
            logger.error(f"【飞牛影视调度器】MediaServerHelper 初始化失败: {e}", exc_info=True)
            self._enabled = False
            return

        try:
            if not self._task_scheduler or not self._task_scheduler.running:
                self._task_scheduler = BackgroundScheduler(timezone=settings.TZ)
                self._task_scheduler.start()
                logger.info("【飞牛影视调度器】任务调度器已启动。")
        except Exception as e:
            logger.error(f"【飞牛影视调度器】任务调度器启动失败: {e}", exc_info=True)
            self._enabled = False
            return

        if self._enabled and self._run_once:
            logger.info("【飞牛影视调度器】检测到 '运行一次' 选项已勾选...")
            run_once_scheduler = BackgroundScheduler(timezone=settings.TZ)
            run_once_scheduler.add_job(
                func=self._execute_and_reset,
                trigger=DateTrigger(run_date=datetime.now() + timedelta(seconds=3)),
                name="Log Media Libraries Once"
            )
            try:
                run_once_scheduler.start()
            except Exception as e:
                logger.error(f"【飞牛影视调度器】'运行一次' 调度器启动失败: {e}", exc_info=True)

        if self._enabled and self._check_tasks_once:
            logger.info("【飞牛影视调度器】检测到 '扫描任务检测' 选项已勾选，准备执行一次性任务检查...")
            try:
                self._task_scheduler.add_job(
                    func=self._execute_check_and_reset,
                    name="Check Running Tasks Once"
                )
            except Exception as e:
                logger.error(f"【飞牛影视调度器】添加 '扫描任务检测' 任务失败: {e}", exc_info=True)

    def _execute_check_and_reset(self):
        """
        执行一次性的“扫描任务检测”并自动关闭开关。
        """
        try:
            logger.info("【飞牛影视调度器】开始检查所有已配置飞牛服务器的正在运行任务...")
            all_configs = self._mediaserver_helper.get_configs()
            
            checked_any = False
            for config in all_configs.values():
                if config.type != 'trimemedia':
                    continue
                
                checked_any = True
                logger.info(f"--- 正在检查服务器: {config.name} ---")
                host = config.config.get("host")
                username = config.config.get("username")
                password = config.config.get("password")
                api_key = "16CCEB3D-AB42-077D-36A1-F355324E4237"
                
                api, base_url = self._create_feiniu_api(host, api_key)
                token = api.login(username, password) if api else None
                
                if token:
                    tasks = self._get_running_tasks(api, base_url, token)
                    logger.info(f"【飞牛影视调度器】服务器 '{config.name}' 的运行中任务GUID列表: {tasks if tasks else '当前无任务'}")
                    api.close()
                else:
                    logger.warning(f"【飞牛影视调度器】无法登录服务器 '{config.name}'，跳过检查。")
                    if api: api.close()
            
            if not checked_any:
                logger.warning("【飞牛影视调度器】未找到任何已配置的飞牛(trimemedia)媒体服务器以进行检查。")

        except Exception as e:
            logger.error(f"【飞牛影视调度器】执行扫描任务检测时发生错误: {e}")
        finally:
            logger.info("【飞牛影视调度器】'扫描任务检测' 任务完成，选项已自动重置为 False。")
            self._check_tasks_once = False
            self.update_config({
                "enabled": self._enabled,
                "run_once": self._run_once,
                "cloud_drive_mode": self._cloud_drive_mode,
                "selected_mediaservers": self._selected_mediaservers,
                "check_tasks_once": False
            })

    def _execute_and_reset(self):
        """
        执行记录逻辑并重置 '运行一次' 标志
        """
        try:
            self._log_media_libraries()
        except Exception as e:
            logger.error(f"【飞牛影视调度器】执行记录时发生错误: {e}")
        finally:
            self._run_once = False
            self.update_config({
                "enabled": self._enabled,
                "run_once": self._run_once,
                "cloud_drive_mode": self._cloud_drive_mode,
                "check_tasks_once": self._check_tasks_once,
                "selected_mediaservers": self._selected_mediaservers
            })
            logger.info("【飞牛影视调度器】'运行一次' 选项已重置为 False。")

    def _create_feiniu_api(self, host: str, api_key: str) -> Tuple[Optional[fnapi.Api], Optional[str]]:
        """
        创建一个飞牛API实例，并返回API对象和其有效的base_url
        """
        standard_host = UrlUtils.standardize_base_url(host).rstrip("/")
        
        host_with_v = f"{standard_host}/v"
        api = fnapi.Api(host_with_v, api_key)
        try:
            if api.sys_version():
                return api, host_with_v
        except Exception:
            pass
        
        api = fnapi.Api(standard_host, api_key)
        try:
            if api.sys_version():
                return api, standard_host
        except Exception:
            pass
            
        return None, None
    
    def _is_cloud_path(self, path_str: str) -> bool:
        """判断路径是否为网盘路径（以/vol0开头）"""
        if not path_str: return False
        normalized_path = os.path.normpath(path_str)
        return normalized_path.startswith(f"{os.sep}vol0")

    def _get_running_tasks(self, api: fnapi.Api, base_url: str, token: str) -> List[str]:
        """调用 /task/running 接口并返回正在运行的媒体库GUID列表"""
        try:
            task_url = f"{base_url.rstrip('/')}/api/v1/task/running"
            
            headers = {
                "Authorization": token,
                "Accept": "application/json"
            }
            logger.debug(f"【飞牛影视调度器】正在请求运行中的任务列表，URL: {task_url}")
            
            response = api._session.get(task_url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and data.get("code") == 0 and "data" in data:
                tasks = data.get("data", [])
                running_guids = list(set(task.get("guid") for task in tasks if task.get("guid")))
                logger.debug(f"【飞牛影视调度器】当前正在运行的扫描任务GUID: {running_guids if running_guids else '无'}")
                return running_guids
            else:
                logger.warning(f"【飞牛影视调度器】获取任务列表时API返回错误: {data}")
                return []
        except Exception as e:
            logger.error(f"【飞牛影视调度器】获取正在运行的任务列表时发生网络或解析错误: {e}")
        return []

    @eventmanager.register(EventType.TransferComplete)
    def handle_transfer_complete(self, event: Event):
        if not self._enabled: return
        if not self._scan_lock.acquire(blocking=False):
            logger.debug("【飞牛影视调度器】事件处理中，跳过重复触发。")
            return
        try:
            transfer_info: Optional[TransferInfo] = event.event_data.get("transferinfo")
            target_diritem: Optional[FileItem] = getattr(transfer_info, 'target_diritem', None)
            if not (target_diritem and target_diritem.path): return
            
            logger.info(f"【飞牛影视调度器】接收到转移完成事件，目标目录: {target_diritem.path}")
            
            if not isinstance(target_diritem.path, (str, Path)): return
            
            normalized_target_path = os.path.normpath(str(target_diritem.path))
            path_for_dirname = normalized_target_path
            if not path_for_dirname.endswith(os.sep): path_for_dirname += os.sep
            series_parent_path = os.path.dirname(path_for_dirname)
            category_path = os.path.dirname(series_parent_path)
            if not category_path.endswith(os.sep): category_path += os.sep

            _mediaserver_helper = self._mediaserver_helper
            all_services = _mediaserver_helper.get_services()
            all_configs = _mediaserver_helper.get_configs()
            if not all_services: return

            for name, service_info in all_services.items():
                if str(service_info.type) == 'trimemedia':
                    libraries = service_info.instance.get_librarys()
                    for lib in libraries:
                        lib_path_str = lib.path[0] if isinstance(lib.path, list) and lib.path else str(lib.path)
                        if not lib_path_str: continue
                        normalized_lib_path = os.path.normpath(lib_path_str)
                        if not normalized_lib_path.endswith(os.sep): normalized_lib_path += os.sep
                        if category_path == normalized_lib_path:
                            logger.info(f"【飞牛影视调度器】匹配成功！媒体库: '{lib.name}'，服务器: '{name}'")
                            feiniu_config = all_configs.get(name)
                            if self._cloud_drive_mode and self._is_cloud_path(lib_path_str):
                                self._handle_cloud_scan_request(lib, feiniu_config)
                            elif not self._cloud_drive_mode and not self._is_cloud_path(lib_path_str):
                                self._handle_local_scan_request(lib, feiniu_config)
                            return
        finally:
            self._scan_lock.release()

    def _handle_local_scan_request(self, lib: MediaServerLibrary, feiniu_config: MediaServerConf):
        """处理本地模式下的扫描请求，立即执行。"""
        logger.info(f"【飞牛影视调度器-本地模式】媒体库 '{lib.name}' 收到扫描请求，立即执行。")
        job_id = f"immediate_scan_{lib.id}_{datetime.now().timestamp()}"
        self._task_scheduler.add_job(self._execute_scan, args=[lib, feiniu_config], id=job_id, name=f"Immediate Scan for {lib.name}")
    
    def _handle_cloud_scan_request(self, lib: MediaServerLibrary, feiniu_config: MediaServerConf):
        """
        处理网盘模式下的扫描请求，启动或重置5分钟防抖计时器。
        如果存在后续任务（重试或静默等待），则取消它们，重新开始流程。
        """
        retry_job_id = f"retry_check_{lib.id}"
        final_scan_job_id = f"final_scan_{lib.id}"

        # 检查并取消后续任务，实现逻辑中断
        try:
            if self._task_scheduler.get_job(retry_job_id):
                self._task_scheduler.remove_job(retry_job_id)
                logger.info(f"【飞牛影视调度器-网盘模式】媒体库 '{lib.name}' 收到新事件，中断了正在进行的3分钟重试检查。")
        except JobLookupError:
            pass
        
        try:
            if self._task_scheduler.get_job(final_scan_job_id):
                self._task_scheduler.remove_job(final_scan_job_id)
                logger.info(f"【飞牛影视调度器-网盘模式】媒体库 '{lib.name}' 收到新事件，中断了正在进行的10分钟静默等待。")
        except JobLookupError:
            pass

        # 设置或重置5分钟防抖计时器
        debounce_job_id = f"debounce_scan_{lib.id}"
        run_time = datetime.now() + timedelta(minutes=5)
        
        if self._task_scheduler.get_job(debounce_job_id):
            self._task_scheduler.reschedule_job(debounce_job_id, trigger='date', run_date=run_time)
            logger.info(f"【飞牛影视调度器-网盘模式】检测到媒体库 '{lib.name}' 的新请求，重置5分钟防抖计时器。")
        else:
            logger.info(f"【飞牛影视调度器-网盘模式】媒体库 '{lib.name}' 收到扫描请求，启动5分钟防抖等待。")
            self._task_scheduler.add_job(
                self._after_debounce_check, 'date', run_date=run_time, 
                args=[lib, feiniu_config], 
                id=debounce_job_id, name=f"Debounce Check for {lib.name}", 
                replace_existing=True
            )

    def _after_debounce_check(self, lib: MediaServerLibrary, feiniu_config: MediaServerConf):
        """5分钟防抖结束后，检查任务状态并决定下一步操作。"""
        logger.info(f"【飞牛影视调度器-网盘模式】媒体库 '{lib.name}' 的5分钟防抖期结束，开始检查当前扫描状态...")
        
        host = feiniu_config.config.get("host")
        username = feiniu_config.config.get("username")
        password = feiniu_config.config.get("password")
        api_key = "16CCEB3D-AB42-077D-36A1-F355324E4237"
        
        api, base_url = self._create_feiniu_api(host, api_key)
        token = api.login(username, password) if api else None
        
        if not token:
            logger.error(f"【飞牛影视调度器】无法登录飞牛服务器 '{feiniu_config.name}'，扫描任务中止。")
            if api: api.close()
            return

        is_scanning = False
        try:
            running_tasks = self._get_running_tasks(api, base_url, token)
            if lib.id in running_tasks:
                is_scanning = True
        finally:
            api.close()

        if is_scanning:
            logger.info(f"【飞牛影视调度器-网盘模式】检测到媒体库 '{lib.name}' 正在扫描中。启动3分钟后的重试检查。")
            retry_job_id = f"retry_check_{lib.id}"
            self._task_scheduler.add_job(
                self._retry_check_loop, 'date', run_date=datetime.now() + timedelta(minutes=3), 
                args=[lib, feiniu_config], 
                id=retry_job_id, name=f"Retry Check for {lib.name}", 
                replace_existing=True
            )
        else:
            logger.info(f"【飞牛影视调度器-网盘模式】确认媒体库 '{lib.name}' 当前无扫描任务，立即执行扫描。")
            self._execute_scan(lib, feiniu_config)

    def _retry_check_loop(self, lib: MediaServerLibrary, feiniu_config: MediaServerConf):
        """
        循环检查任务状态，如果任务仍在运行，则安排下一次检查；如果任务已停止，则进入10分钟静默期。
        """
        logger.info(f"【飞牛影视调度器-网盘模式】正在对媒体库 '{lib.name}' 进行3分钟后的重试检查...")
        
        host = feiniu_config.config.get("host")
        username = feiniu_config.config.get("username")
        password = feiniu_config.config.get("password")
        api_key = "16CCEB3D-AB42-077D-36A1-F355324E4237"
        
        api, base_url = self._create_feiniu_api(host, api_key)
        token = api.login(username, password) if api else None
        
        if not token:
            logger.error(f"【飞牛影视调度器】无法登录飞牛服务器 '{feiniu_config.name}'，重试检查中止。")
            if api: api.close()
            return
            
        is_scanning = False
        try:
            if lib.id in self._get_running_tasks(api, base_url, token):
                is_scanning = True
        finally:
            api.close()

        if is_scanning:
            logger.info(f"【飞牛影视调度器-网盘模式】媒体库 '{lib.name}' 仍在扫描中。将在3分钟后再次检查。")
            retry_job_id = f"retry_check_{lib.id}"
            self._task_scheduler.add_job(
                self._retry_check_loop, 'date', run_date=datetime.now() + timedelta(minutes=3), 
                args=[lib, feiniu_config], 
                id=retry_job_id, name=f"Retry Check for {lib.name}", 
                replace_existing=True
            )
        else:
            logger.info(f"【飞牛影视调度器-网盘模式】确认媒体库 '{lib.name}' 的扫描任务已结束。开始10分钟的静默等待期。")
            final_scan_job_id = f"final_scan_{lib.id}"
            self._task_scheduler.add_job(
                self._execute_scan, 'date', run_date=datetime.now() + timedelta(minutes=10), 
                args=[lib, feiniu_config], 
                id=final_scan_job_id, name=f"Final Scan for {lib.name}", 
                replace_existing=True
            )

    def _execute_scan(self, lib: MediaServerLibrary, feiniu_config: MediaServerConf):
        """最终执行扫描的函数。"""
        logger.info(f"【飞牛影视调度器】开始对媒体库 '{lib.name}' (ID: {lib.id}) 发起扫描请求...")
        host = feiniu_config.config.get("host")
        username = feiniu_config.config.get("username")
        password = feiniu_config.config.get("password")
        api_key = "16CCEB3D-AB42-077D-36A1-F355324E4237"
        
        api, _ = self._create_feiniu_api(host, api_key)

        if not api or not api.login(username, password):
            logger.error(f"【飞牛影视调度器】执行扫描前登录飞牛服务器 '{feiniu_config.name}' 失败。")
            if api: api.close()
            return
        
        try:
            mdb_to_scan = fnapi.MediaDb(guid=lib.id, category=fnapi.Category.MOVIE, name=lib.name)
            success = api.mdb_scan(mdb_to_scan)
            logger.info(f"【飞牛影视调度器】媒体库 '{lib.name}' 扫描请求最终执行结果：{'成功' if success else '失败'}。")
        except Exception as e:
            logger.error(f"【飞牛影视调度器】执行扫描时发生意外错误: {e}")
        finally:
            api.close()
            
    def _log_media_libraries(self):
        """
        获取并记录媒体库信息 (此为 "运行一次" 功能的完整实现)
        """
        logger.info("【飞牛影视调度器】开始获取媒体库信息...")
        _mediaserver_helper = self._mediaserver_helper
        if not _mediaserver_helper:
            logger.error("【飞牛影视调度器】MediaServerHelper 未初始化。无法获取媒体库信息。")
            return
        
        all_services: Optional[Dict[str, ServiceInfo]] = _mediaserver_helper.get_services()

        if not all_services:
            logger.warning("【飞牛影视调度器】未找到任何配置的媒体服务器。")
            return

        logged_any = False
        for name, service_info in all_services.items():
            if self._selected_mediaservers and name not in self._selected_mediaservers:
                continue

            logger.info(f"【飞牛影视调度器】正在处理媒体服务器: {name} (类型: {str(service_info.type)})")
            
            if service_info.instance.is_inactive():
                logger.warning(f"【飞牛影视调度器】媒体服务器 {name} 未连接或不活跃，跳过。")
                continue

            try:
                libraries: List[MediaServerLibrary] = service_info.instance.get_librarys()
                if not libraries:
                    logger.info(f"【飞牛影视调度器】媒体服务器 {name} 未发现任何媒体库。")
                    continue

                for lib in libraries:
                    logged_any = True
                    logger.info(f"【飞牛影视调度器】媒体服务器: {name}")
                    logger.info(f"  - 库ID: {lib.id}")
                    logger.info(f"  - 库类型: {str(lib.type)}") 
                    logger.info(f"  - 库名称: {lib.name}")
                    logger.info(f"  - 路径: {lib.path}")
                    logger.info("-" * 20)
            except Exception as e:
                logger.error(f"【飞牛影视调度器】获取媒体服务器 {name} 的媒体库信息时发生错误: {e}")

        if not logged_any:
            logger.info("【飞牛影视调度器】没有媒体库信息被记录到日志中。")
        logger.info("【飞牛影视调度器】媒体库信息记录完成。")

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        _mediaserver_helper = MediaServerHelper()
        all_services_configs = _mediaserver_helper.get_configs()
        select_items = [{"title": config.name, "value": config.name} for config in all_services_configs.values()]

        form_config = [
            {
                "component": "VCard",
                "props": {"variant": "outlined", "class": "mb-3"},
                "content": [
                    {
                        "component": "VCardTitle",
                        "props": {"class": "d-flex align-center"},
                        "content": [
                            {"component": "VIcon", "props": {"icon": "mdi-cog", "color": "primary", "class": "mr-2"}},
                            {"component": "span", "text": "基本设置"},
                        ],
                    },
                    {"component": "VDivider"},
                    {
                        "component": "VCardText",
                        "content": [
                            {
                                "component": "VRow",
                                "content": [
                                    {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VSwitch", "props": {"model": "enabled", "label": "启用插件"}}]},
                                    {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VSwitch", "props": {"model": "cloud_drive_mode", "label": "网盘模式", "color": "primary"}}]},
                                    {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VSwitch", "props": {"model": "run_once", "label": "媒体库获取检测"}}]},
                                    {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VSwitch", "props": {"model": "check_tasks_once", "label": "扫描任务检测", "color": "orange"}}]},
                                ],
                            },
                            {"component": "VSelect", "props": {"multiple": True, "chips": True, "clearable": True, "model": "selected_mediaservers", "label": "选择媒体服务器（留空则处理所有）", "items": select_items}},
                        ],
                    },
                ],
            },
        ]
        
        default_values = {
            "enabled": False,
            "run_once": False,
            "cloud_drive_mode": False,
            "check_tasks_once": False,
            "selected_mediaservers": [],
        }

        return form_config, default_values

    def get_page(self) -> List[dict]:
        pass

    def stop_service(self):
        """退出插件时停止所有调度器"""
        if self._task_scheduler and self._task_scheduler.running:
            self._task_scheduler.shutdown(wait=False)
            self._task_scheduler = None
            logger.info("【飞牛影视调度器】任务调度器已停止。")
        
        try:
            from app.core.event import eventmanager
            eventmanager.remove_event_listener(EventType.TransferComplete, self.handle_transfer_complete)
        except Exception as e:
            logger.debug(f"【飞牛影视调度器】注销事件监听器时出错（可能已被注销）: {e}")

