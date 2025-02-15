from typing import Any, List, Dict, Tuple
from app.plugins import _PluginBase
from app.log import logger
from app.core.config import settings
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
    plugin_version = "1.0.1"
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
        try:
            if config:
                self._enabled = config.get("enabled")
                self._site_url = config.get("site_url")
                self._cookie = config.get("cookie")
                self._message = config.get("message")

                logger.info("插件初始化配置: %s", config)

                # 停止现有任务
                self.stop_service()

                if self._enabled:
                    logger.info("插件已启用，站点URL: %s", self._site_url)
                    # 创建定时任务，使用项目自己的时区设置
                    self._scheduler = BackgroundScheduler(timezone=settings.TZ)
                    self._scheduler.add_job(self.send_message, 
                                          CronTrigger.from_crontab('0 * * * *'),  # 每小时执行一次
                                          name="站点喊话")
                    # 启动任务
                    if self._scheduler.get_jobs():
                        self._scheduler.start()
                        logger.info("站点喊话服务启动")
                else:
                    logger.warning("插件未启用")
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
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'cookie',
                                            'label': 'Cookie',
                                            'placeholder': '输入站点的Cookie',
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
            logger.warning("插件未启用")
            return

        if not self._site_url or not self._message:
            logger.warning("站点URL或消息内容未设置")
            return

        # 这里实现发送消息的逻辑
        logger.info(f"向 {self._site_url} 发送消息: {self._message}，使用Cookie: {self._cookie}")
        # 发送请求的代码可以在这里实现

    def stop_service(self):
        """
        退出插件
        """
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
                self._scheduler = None
                logger.info("站点喊话服务已停止")
        except Exception as e:
            logger.error("退出插件失败: %s", str(e)) 
