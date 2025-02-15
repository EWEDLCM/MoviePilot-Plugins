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
    plugin_desc = "在多个指定站点进行定时喊话"
    # 插件图标
    plugin_icon = "shoutbox.png"
    # 插件版本
    plugin_version = "1.2"
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
    _sites = []
    _scheduler: BackgroundScheduler = None

    def init_plugin(self, config: dict = None):
        """
        插件初始化
        """
        # 停止现有任务
        self.stop_service()

        if config:
            self._enabled = config.get("enabled", False)
            self._sites = config.get("sites", [])

        if self._enabled and self._sites:
            try:
                # 初始化调度器
                self._scheduler = BackgroundScheduler(timezone=pytz.UTC)
                self._scheduler.add_job(
                    func=self.send_messages_to_all_sites,
                    trigger=CronTrigger.from_crontab('0 * * * *'),  # 每小时执行一次
                    name="定时喊话任务"
                )
                # 立即运行一次测试
                self._scheduler.add_job(
                    func=self.send_messages_to_all_sites,
                    trigger='date',
                    run_date=datetime.now(pytz.UTC) + timedelta(seconds=3),
                    name="测试喊话任务"
                )
                self._scheduler.start()
                logger.info("喊话服务启动成功")
            except Exception as e:
                logger.error(f"定时任务启动失败: {e}")
                self.stop_service()

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
                                'props': {'cols': 12, 'md': 6},
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
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VArray',
                                        'props': {
                                            'model': 'sites',
                                            'label': '站点配置',
                                            'item_default': {
                                                'site_url': '',
                                                'cookie': '',
                                                'message': ''
                                            },
                                            'items': [
                                                {
                                                    'component': 'VRow',
                                                    'content': [
                                                        {
                                                            'component': 'VCol',
                                                            'props': {'cols': 12, 'md': 4},
                                                            'content': [
                                                                {
                                                                    'component': 'VTextField',
                                                                    'props': {
                                                                        'model': 'item.site_url',
                                                                        'label': '站点URL',
                                                                        'placeholder': 'https://example.com'
                                                                    }
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            'component': 'VCol',
                                                            'props': {'cols': 12, 'md': 4},
                                                            'content': [
                                                                {
                                                                    'component': 'VTextField',
                                                                    'props': {
                                                                        'model': 'item.cookie',
                                                                        'label': 'Cookie',
                                                                        'placeholder': '输入站点Cookie'
                                                                    }
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            'component': 'VCol',
                                                            'props': {'cols': 12, 'md': 4},
                                                            'content': [
                                                                {
                                                                    'component': 'VTextField',
                                                                    'props': {
                                                                        'model': 'item.message',
                                                                        'label': '喊话内容',
                                                                        'placeholder': '输入喊话消息'
                                                                    }
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
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
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'info',
                                            'variant': 'tonal',
                                            'text': '每小时整点自动执行喊话，请确保Cookie有效性'
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
            "sites": []
        }

    def send_messages_to_all_sites(self):
        """
        向所有配置的站点发送消息
        """
        if not self._enabled or not self._sites:
            logger.info("插件未启用或无站点配置，跳过喊话")
            return

        for site in self._sites:
            try:
                site_url = site.get('site_url')
                cookie = site.get('cookie')
                message = site.get('message')

                if not all([site_url, cookie, message]):
                    logger.warning(f"站点配置不完整，跳过: {site}")
                    continue

                logger.info(f"正在向 {site_url} 发送喊话: {message}")
                # 示例：使用requests发送POST请求
                # import requests
                # headers = {'Cookie': cookie}
                # data = {'message': message}
                # response = requests.post(f"{site_url}/shoutbox", headers=headers, data=data)
                # if response.status_code == 200:
                #     logger.success(f"喊话成功: {site_url}")
                # else:
                #     logger.error(f"喊话失败: {response.text}")
            except Exception as e:
                logger.error(f"向 {site.get('site_url')} 喊话失败: {str(e)}")

    def stop_service(self):
        """
        停止服务
        """
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
                self._scheduler = None
                logger.info("喊话服务已停止")
        except Exception as e:
            logger.error(f"停止服务失败: {e}")

    # 以下方法保持空实现即可
    def get_api(self) -> List[Dict[str, Any]]: pass
    def get_page(self) -> List[dict]: pass
    def get_command(self) -> List[Dict[str, Any]]: pass
