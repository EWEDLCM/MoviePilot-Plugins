from typing import Any, List, Dict, Tuple
from app.plugins import _PluginBase
from app.log import logger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from datetime import datetime, timedelta

class ShoutBoxPlugin(_PluginBase):
    # 插件名称
    plugin_name = "喊话功能"
    # 插件描述
    plugin_desc = "在指定站点进行喊话"
    # 插件图标
    plugin_icon = "shoutbox.png"
    # 插件版本
    plugin_version = "1.0"
    # 插件作者
    plugin_author = "EWEDL"
    # 作者主页
    author_url = "https://github.com/EWEDL"
    # 插件配置项ID前缀
    plugin_config_prefix = "shoutbox_plugin_"
    # 加载顺序
    plugin_order = 30
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enabled = False
    _site_url = ""
    _cookie = ""
    _message = ""
    _scheduler: BackgroundScheduler = None

    def init_plugin(self, config: dict = None):
        """
        插件初始化
        """
        if config:
            self._enabled = config.get("enabled")
            self._site_url = config.get("site_url")
            self._cookie = config.get("cookie")
            self._message = config.get("message")

            # 停止现有任务
            self.stop_service()

            if self._enabled:
                logger.info(f"站点喊话服务启动，站点：{self._site_url}")
                self._scheduler = BackgroundScheduler()
                self._scheduler.add_job(self.send_message, 
                                      CronTrigger.from_crontab('0 * * * *'),
                                      name="站点喊话",
                                      next_run_time=datetime.now(tz=pytz.UTC) + timedelta(seconds=3))
                self._scheduler.start()

    def get_state(self) -> bool:
        return self._enabled

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面
        """
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件'
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'site_url',
                                            'label': '站点URL',
                                            'placeholder': '输入要喊话的站点URL'
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'cookie',
                                            'label': 'Cookie',
                                            'placeholder': '输入站点的Cookie'
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextarea',
                                        'props': {
                                            'model': 'message',
                                            'label': '喊话内容',
                                            'placeholder': '输入要发送的消息',
                                            'rows': 4
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enabled": False,
            "site_url": "",
            "cookie": "",
            "message": ""
        }

    def send_message(self):
        """发送消息到指定站点"""
        if not self.get_state():
            return
        if not self._site_url or not self._message:
            return
        logger.info(f"向 {self._site_url} 发送消息: {self._message}")

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_page(self) -> List[dict]:
        pass

    def get_command(self) -> List[Dict[str, Any]]:
        pass

    def stop_service(self):
        """退出插件"""
        if self._scheduler:
            self._scheduler.shutdown()
            self._scheduler = None 
