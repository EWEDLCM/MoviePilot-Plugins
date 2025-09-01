"""
CFW设备在线汇报插件
版本: 1.0.3
作者: EWEDL
功能:
- 定期向Cloudflare Worker或服务器发送心跳请求
- 可配置Worker URL、设备名称和设备token
- 可配置心跳发送间隔(cron表达式)
- 支持详细日志记录模式
"""
import requests
import json
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import os 

from app.core.config import settings
from app.plugins import _PluginBase
from typing import Any, List, Dict, Tuple, Optional
from app.log import logger

# 定义默认值常量
DEFAULT_CRON = "*/2 * * * *"  # 每2分钟执行一次


class Cfworkerheartbeat(_PluginBase):
    # 插件名称
    plugin_name = "CFW设备在线汇报"
    # 插件描述
    plugin_desc = "定期向Cloudflare Worker或服务器发送心跳请求，汇报设备在线状态"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/EWEDLCM/MoviePilot-Plugins/main/icons/cloudflare.png"
    # 插件版本
    plugin_version = "1.0.3"
    # 插件作者
    plugin_author = "EWEDL"
    # 作者主页
    author_url = "https://github.com/EWEDLCM"
    # 插件配置项ID前缀
    plugin_config_prefix = "cfworkerheartbeat_"
    # 加载顺序
    plugin_order = 1
    # 可使用的用户级别
    auth_level = 2

    # 私有属性
    _enabled = False
    _onlyonce = False
    _worker_url = ""
    _device_name = ""
    _device_token = ""
    _cron = DEFAULT_CRON
    _verbose_logging = False
    _use_proxy_host_cfw = False # 新增：是否使用 PROXY_HOST 作为代理

    def init_plugin(self, config: dict = None):
        logger.info("============= CFW设备在线汇报插件初始化 =============")
        
        if config:
            self._enabled = config.get("enabled", False)
            self._worker_url = config.get("worker_url", "")
            self._device_name = config.get("device_name", "")
            self._device_token = config.get("device_token", "")
            self._cron = config.get("cron", DEFAULT_CRON)
            self._verbose_logging = config.get("verbose_logging", False)
            self._onlyonce = config.get("onlyonce", False)
            self._use_proxy_host_cfw = config.get("use_proxy_host_cfw", False) # 新增
            
            logger.info(f"配置: enabled={self._enabled}, cron={self._cron}, verbose_logging={self._verbose_logging}, use_proxy_host_cfw={self._use_proxy_host_cfw}")
            
            # 检查配置有效性
            if not self._worker_url:
                logger.error("Worker URL未配置")
                self._enabled = False
            elif "https://<你的Worker名>" in self._worker_url:
                logger.error("请先填写插件配置中的 WORKER_URL")
                self._enabled = False
                
            if not self._device_name:
                logger.error("设备名称未配置")
                self._enabled = False
                
            if not self._device_token:
                logger.error("设备Token未配置")
                self._enabled = False

            # 如果启用了代理并尝试获取PROXY_HOST
            if self._use_proxy_host_cfw:
                proxy_host_val = self.get_proxy_host()
                if not proxy_host_val:
                    logger.warning("已启用PROXY_HOST代理，但未获取到PROXY_HOST设置，将自动关闭代理开关并继续运行。")
                    self._use_proxy_host_cfw = False
                else:
                    logger.info(f"已启用PROXY_HOST代理，将使用：{proxy_host_val}")

            if self._onlyonce:
                logger.info("执行一次性心跳发送")
                self.send_heartbeat()
                self._onlyonce = False

            # 保存配置更新
            self.update_config({
                "onlyonce": False,
                "enabled": self._enabled,
                "worker_url": self._worker_url,
                "device_name": self._device_name,
                "device_token": self._device_token,
                "cron": self._cron,
                "verbose_logging": self._verbose_logging,
                "use_proxy_host_cfw": self._use_proxy_host_cfw
            })

    def get_proxy_host(self):
        """获取 PROXY_HOST 环境变量"""
        proxy_host = os.environ.get('PROXY_HOST')
        if proxy_host:
            if not proxy_host.startswith('http://') and not proxy_host.startswith('https://'):
                proxy_host = f"http://{proxy_host}"
            logger.info(f"从环境变量 PROXY_HOST 获取到代理: {proxy_host}")
            return proxy_host

        try:
            if hasattr(settings, 'PROXY_HOST') and settings.PROXY_HOST:
                proxy_host = settings.PROXY_HOST
                if not proxy_host.startswith('http://') and not proxy_host.startswith('https://'):
                    proxy_host = f"http://{proxy_host}"
                logger.info(f"从 settings.PROXY_HOST 获取到代理: {proxy_host}")
                return proxy_host
        except Exception as e:
            logger.debug(f"尝试从 settings 获取 PROXY_HOST 失败: {str(e)}")
        
        logger.info("未找到 PROXY_HOST 设置")
        return None

    def send_heartbeat(self):
        """向Cloudflare Worker发送心跳请求"""
        if not self._enabled:
            return
            
        if self._verbose_logging:
            logger.info("正在发送心跳...")
        
        heartbeat_endpoint = self._worker_url.strip('/') + "/heartbeat"
        payload = {
            "devicename": self._device_name,
            "token": self._device_token
        }
        headers = {
            "Content-Type": "application/json"
        }

        proxies = None
        if self._use_proxy_host_cfw:
            proxy_host_val = self.get_proxy_host()
            if proxy_host_val:
                proxies = {"http": proxy_host_val, "https": proxy_host_val}
                logger.info(f"使用 PROXY_HOST 代理进行心跳请求: {proxy_host_val}")
            else:
                logger.warning("已启用PROXY_HOST代理，但未获取到PROXY_HOST设置，心跳请求将不使用代理。")

        try:
            response = requests.post(heartbeat_endpoint, headers=headers, json=payload, proxies=proxies, timeout=10)

            if response.status_code == 200:
                if self._verbose_logging:
                    logger.info(f"心跳发送成功, 服务器响应: {response.text}")
                # 非详细模式下不记录成功日志
            else:
                logger.error(f"心跳发送失败! 状态码: {response.status_code}, 错误信息: {response.text}")

        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败! 错误详情: {e}")

    def get_state(self) -> bool:
        return self._enabled

    def get_service(self) -> List[Dict[str, Any]]:
        """注册插件服务"""
        if self._enabled and self._cron:
            try:
                if str(self._cron).strip().count(" ") == 4:
                    return [{
                        "id": "cfworkerheartbeat",
                        "name": "CFW设备在线汇报服务",
                        "trigger": CronTrigger.from_crontab(self._cron, timezone=settings.TZ),
                        "func": self.send_heartbeat,
                        "kwargs": {}
                    }]
                else:
                    logger.error(f"CFW设备在线汇报的Cron表达式 '{self._cron}' 格式不正确，服务启动失败。")
            except Exception as e:
                logger.error(f"CFW设备在线汇报注册定时任务失败：{e}", exc_info=True)
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """获取表单配置"""
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
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件',
                                            'hint': '开启或关闭插件',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'verbose_logging',
                                            'label': '详细日志记录',
                                            'hint': '开启时显示详细响应结果',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'onlyonce',
                                            'label': '立即运行一次',
                                            'hint': '保存后立即执行一次',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'use_proxy_host_cfw',
                                            'label': '使用PROXY_HOST代理',
                                            'hint': '复用环境变量PROXY_HOST代理',
                                            'persistent-hint': True
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
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'worker_url',
                                            'label': 'Worker URL',
                                            'placeholder': 'https://your-worker.workers.dev',
                                            'hint': 'Cloudflare Worker或服务器的完整URL',
                                            'persistent-hint': True
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
                                            'model': 'device_name',
                                            'label': '设备名称',
                                            'placeholder': '设备名称',
                                            'hint': '用于标识设备的名称',
                                            'persistent-hint': True
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
                                            'model': 'device_token',
                                            'label': '设备Token',
                                            'placeholder': '设备Token',
                                            'hint': '设备的认证令牌',
                                            'persistent-hint': True
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
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'cron',
                                            'label': '执行周期',
                                            'placeholder': DEFAULT_CRON,
                                            'hint': '五位Cron表达式，默认每2分钟一次',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enabled": self._enabled,
            "worker_url": self._worker_url,
            "device_name": self._device_name,
            "device_token": self._device_token,
            "cron": self._cron,
            "verbose_logging": self._verbose_logging,
            "onlyonce": False,
            "use_proxy_host_cfw": self._use_proxy_host_cfw # 新增
        }

    def get_page(self) -> List[dict]:
        """获取插件页面"""
        return [
            {
                'component': 'VRow',
                'content': [
                    {
                        'component': 'VCol',
                        'props': {
                            'cols': 12
                        },
                        'content': [
                            {
                                'component': 'VCard',
                                'props': {
                                    'title': 'CFW设备在线汇报',
                                    'subtitle': '定期向Cloudflare Worker或服务器发送心跳请求，保持设备在线状态'
                                },
                                'content': [
                                    {
                                        'component': 'VCardText',
                                        'content': [
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'text-subtitle-1 font-weight-bold'
                                                },
                                                'text': '当前状态:'
                                            },
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'text-body-1 mt-2'
                                                },
                                                'text': '运行中' if self.get_state() else '未运行'
                                            },
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'text-subtitle-1 font-weight-bold mt-4'
                                                },
                                                'text': '配置信息:'
                                            },
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'text-body-1 mt-2'
                                                },
                                                'text': f'Worker URL: {self._worker_url}'
                                            },
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'text-body-1'
                                                },
                                                'text': f'设备名称: {self._device_name}'
                                            },
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'text-body-1'
                                                },
                                                'text': f'执行周期: {self._cron}'
                                            },
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'text-subtitle-1 font-weight-bold mt-4'
                                                },
                                                'text': '使用说明:'
                                            },
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'text-body-1 mt-2'
                                                },
                                                'text': '详见飞牛论坛帖子详情：'
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]

    def stop_service(self):
        """停止插件服务"""
        # 由于我们使用框架的调度机制，这里不需要额外操作
        logger.info("CFW设备在线汇报服务已停止")
        return True

    def get_command(self) -> List[Dict[str, Any]]:
        """注册命令"""
        return [{
            "cmd": "/cfheartbeat",
            "event": self.send_heartbeat,
            "desc": "手动执行Cloudflare Worker心跳发送"
        }]

    def get_api(self) -> List[Dict[str, Any]]:
        """注册API"""
        return []