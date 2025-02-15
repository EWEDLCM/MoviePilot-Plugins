from typing import Any, List, Dict, Tuple
from app.plugins import _PluginBase
from app.schemas.types import NotificationType
from app.log import logger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

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
    plugin_author = "YourName"
    # 作者主页
    author_url = "https://github.com/YourGitHub"
    # 插件配置项ID前缀
    plugin_config_prefix = "shoutbox_plugin_"
    # 加载顺序
    plugin_order = 30
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enabled = False
    _site_url = ""
    _message = ""
    _cron = ""
    _scheduler: BackgroundScheduler = None

    def init_plugin(self, config: dict = None):
        try:
            if config:
                self._enabled = config.get("enabled")
                self._site_url = config.get("site_url")
                self._message = config.get("message")
                self._cron = config.get("cron")

                logger.info("插件初始化配置: %s", config)

                if self._enabled and self._cron:
                    self._scheduler = BackgroundScheduler()
                    self._scheduler.add_job(self.send_message, CronTrigger.from_crontab(self._cron))
                    self._scheduler.start()
                    logger.info("插件已启动，执行周期: %s", self._cron)
                else:
                    logger.warning("插件未启用或未设置执行周期")
        except Exception as e:
            logger.error("插件初始化失败: %s", str(e))

    def get_state(self) -> bool:
        return self._enabled

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
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
                                            'label': '启用插件',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
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
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'site_url',
                                            'label': '站点URL',
                                            'placeholder': '输入要喊话的站点URL',
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
                    },
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
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'cron',
                                            'label': '执行周期',
                                            'placeholder': '输入Cron表达式',
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
            "message": "",
            "cron": ""
        }

    def send_message(self):
        """发送消息到指定站点"""
        if not self.get_state():
            logger.warning("插件未启用")
            return

        if not self._site_url or not self._message:
            logger.warning("站点URL或消息内容未设置")
            return

        # 这里实现发送消息的逻辑
        logger.info(f"向 {self._site_url} 发送消息: {self._message}")
        # 发送请求的代码可以在这里实现

    def stop_service(self):
        """退出插件"""
        if self._scheduler:
            self._scheduler.shutdown() 
