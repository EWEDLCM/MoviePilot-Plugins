"""
代理地址测试插件
版本: 1.1.1
作者: EWEDL
功能:
- 获取容器内的系统代理设置
- 测试网络连通性
- 支持复用容器系统代理
- 支持检测 PROXY_HOST 环境变量
- 实时测试连接并生成日志
"""
import os
import time
import requests
from datetime import datetime, timedelta
import pytz
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.plugins import _PluginBase
from typing import Any, List, Dict, Tuple, Optional
from app.log import logger
from app.utils.http import RequestUtils

# 定义默认值常量
DEFAULT_TEST_URL = "https://www.google.com"
DEFAULT_CRON = "0 */4 * * *"  # 每4小时执行一次
DEFAULT_HISTORY_DAYS = 7


class proxytest(_PluginBase):
    # 插件名称
    plugin_name = "代理地址测试"
    # 插件描述
    plugin_desc = "测试容器内的HTTP代理设置，并尝试使用代理连接外网"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/EWEDLCM/MoviePilot-Plugins/main/icons/proxytest.png"
    # 插件版本
    plugin_version = "1.1.1"  # 更新版本号
    # 插件作者
    plugin_author = "EWEDL"
    # 作者主页
    author_url = "https://github.com/EWEDLCM"
    # 插件配置项ID前缀
    plugin_config_prefix = "proxytest_"
    # 加载顺序
    plugin_order = 1
    # 可使用的用户级别
    auth_level = 2

    # 私有属性
    _enabled = False
    _onlyonce = False
    _use_proxy = False
    _use_proxy_host = False  # 新增：是否使用 PROXY_HOST
    _use_requests = True     # 新增：是否用requests测试
    _use_requestutils = False # 新增：是否用RequestUtils测试
    _test_url = DEFAULT_TEST_URL
    _cron = DEFAULT_CRON
    _history_days = DEFAULT_HISTORY_DAYS
    # 定时器
    _scheduler: Optional[BackgroundScheduler] = None

    def init_plugin(self, config: dict = None):
        # 停止现有任务
        self.stop_service()

        logger.info("============= 代理地址测试插件初始化 =============")
        try:
            if config:
                self._enabled = config.get("enabled", False)
                self._test_url = config.get("test_url", DEFAULT_TEST_URL)
                self._use_proxy = config.get("use_proxy", False)
                self._use_proxy_host = config.get("use_proxy_host", False)  # 新增：读取配置
                self._onlyonce = config.get("onlyonce", False)
                self._cron = config.get("cron", DEFAULT_CRON)
                self._history_days = int(config.get("history_days", DEFAULT_HISTORY_DAYS))
                self._use_requests = config.get("use_requests", True)  # 新增
                self._use_requestutils = config.get("use_requestutils", False)  # 新增
                logger.info(f"配置: enabled={self._enabled}, use_proxy={self._use_proxy}, use_proxy_host={self._use_proxy_host}, use_requests={self._use_requests}, use_requestutils={self._use_requestutils}, cron={self._cron}, history_days={self._history_days}")
                logger.info(f"测试网址: {self._test_url}")
            
            if self._onlyonce:
                logger.info("执行一次性代理测试")
                self._scheduler = BackgroundScheduler(timezone=settings.TZ)
                self._scheduler.add_job(func=self.test_proxy, trigger='date',
                                    run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=3),
                                    name="代理地址测试")
                self._onlyonce = False
                self.update_config({
                    "onlyonce": False,
                    "enabled": self._enabled,
                    "test_url": self._test_url,
                    "use_proxy": self._use_proxy,
                    "use_proxy_host": self._use_proxy_host,  # 新增：保存配置
                    "cron": self._cron,
                    "history_days": self._history_days,
                    "use_requests": self._use_requests,
                    "use_requestutils": self._use_requestutils
                })

                # 启动任务
                if self._scheduler.get_jobs():
                    self._scheduler.print_jobs()
                    self._scheduler.start()
            elif self._enabled and self._cron:
                # 启动定时任务
                self._scheduler = BackgroundScheduler(timezone=settings.TZ)
                self._scheduler.add_job(func=self.test_proxy,
                                     trigger=CronTrigger.from_crontab(self._cron),
                                     name="代理地址测试")
                logger.info(f"已启动定时任务，cron: {self._cron}")
                
                # 启动任务
                if self._scheduler.get_jobs():
                    self._scheduler.print_jobs()
                    self._scheduler.start()

        except Exception as e:
            logger.error(f"代理地址测试插件初始化错误: {str(e)}", exc_info=True)

    def get_proxy_from_env(self):
        """从环境变量获取代理设置"""
        proxy_env = None
        # 按优先级检查环境变量
        for env_var in ['https_proxy', 'HTTPS_PROXY', 'http_proxy', 'HTTP_PROXY']:
            proxy_env = os.environ.get(env_var)
            if proxy_env:
                logger.info(f"从环境变量 {env_var} 获取到代理: {proxy_env}")
                return proxy_env
        
        logger.info("未在环境变量中找到代理设置")
        return None
        
    def get_proxy_host(self):
        """获取 PROXY_HOST 环境变量"""
        proxy_host = os.environ.get('PROXY_HOST')
        if proxy_host:
            # 确保代理地址格式正确（添加 http:// 前缀如果没有的话）
            if not proxy_host.startswith('http://') and not proxy_host.startswith('https://'):
                proxy_host = f"http://{proxy_host}"
            logger.info(f"从环境变量 PROXY_HOST 获取到代理: {proxy_host}")
            return proxy_host
        
        # 尝试从 settings 中获取 PROXY_HOST
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

    def test_proxy(self):
        """测试代理连接"""
        logger.info("============= 开始代理地址测试 =============")
        start_time = datetime.now()
        url = self._test_url if self._test_url else DEFAULT_TEST_URL
        logger.info(f"测试目标网址: {url}")
        proxies = None
        proxy_source = "未使用代理"
        if self._use_proxy_host:
            proxy_env = self.get_proxy_host()
            if proxy_env:
                proxies = {"http": proxy_env, "https": proxy_env}
                logger.info(f"使用 PROXY_HOST 代理: {proxy_env}")
                proxy_source = "PROXY_HOST"
            else:
                logger.warning("PROXY_HOST 代理选项已启用，但未找到 PROXY_HOST 设置")
                proxy_source = "PROXY_HOST (未找到)"
        elif self._use_proxy:
            proxy_env = self.get_proxy_from_env()
            if proxy_env:
                proxies = {"http": proxy_env, "https": proxy_env}
                logger.info(f"使用环境变量代理: {proxy_env}")
                proxy_source = "环境变量"
            else:
                logger.warning("复用代理选项已启用，但环境变量中未找到代理设置")
                proxy_source = "环境变量 (未找到)"
        # 记录代理模式
        if self._use_proxy_host:
            proxy_mode = "PROXY_HOST"
        elif self._use_proxy:
            proxy_mode = "环境变量"
        else:
            proxy_mode = "禁用"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        # 1. requests测试
        if self._use_requests:
            result = {}
            try:
                req_start = time.time()
                response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
                req_time = time.time() - req_start
                result["status_code"] = response.status_code
                result["response_time"] = f"{req_time:.2f}秒"
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.title.string if soup.title else "无标题"
                    result["title"] = title
                    result["success"] = True
                    result["message"] = f"连接成功! 网页标题: {title}"
                    logger.info(f"[requests] 连接成功! 状态码: {response.status_code}, 响应时间: {req_time:.2f}秒, 标题: {title}")
                else:
                    result["success"] = False
                    result["message"] = f"连接返回非200状态码: {response.status_code}"
                    logger.warning(f"[requests] 连接返回非200状态码: {response.status_code}, 响应时间: {req_time:.2f}秒")
            except requests.exceptions.RequestException as e:
                result["success"] = False
                result["message"] = f"连接失败: {str(e)}"
                logger.error(f"[requests] 连接失败: {str(e)}")
            test_record = {
                "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "url": url,
                "proxy_mode": proxy_mode,
                "proxy": proxies["http"] if proxies else "未使用",
                "proxy_source": proxy_source,
                "status": "成功" if result.get("success", False) else "失败",
                "message": result.get("message", ""),
                "response_time": result.get("response_time", "N/A"),
                "details": result,
                "method": "requests"
            }
            self._save_test_history(test_record)
            logger.info(f"[requests] 代理测试完成: {test_record['status']}")
        # 2. RequestUtils测试
        if self._use_requestutils:
            result = {}
            try:
                req_start = time.time()
                res = RequestUtils(proxies=proxies, timeout=30).get_res(url=url, headers=headers)
                req_time = time.time() - req_start
                result["status_code"] = res.status_code if res else None
                result["response_time"] = f"{req_time:.2f}秒"
                if res and res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    title = soup.title.string if soup.title else "无标题"
                    result["title"] = title
                    result["success"] = True
                    result["message"] = f"连接成功! 网页标题: {title}"
                    logger.info(f"[RequestUtils] 连接成功! 状态码: {res.status_code}, 响应时间: {req_time:.2f}秒, 标题: {title}")
                else:
                    result["success"] = False
                    result["message"] = f"连接返回非200状态码: {res.status_code if res else '无响应'}"
                    logger.warning(f"[RequestUtils] 连接返回非200状态码: {res.status_code if res else '无响应'}, 响应时间: {req_time:.2f}秒")
            except Exception as e:
                result["success"] = False
                result["message"] = f"连接失败: {str(e)}"
                logger.error(f"[RequestUtils] 连接失败: {str(e)}")
            test_record = {
                "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "url": url,
                "proxy_mode": proxy_mode,
                "proxy": proxies["http"] if proxies else "未使用",
                "proxy_source": proxy_source,
                "status": "成功" if result.get("success", False) else "失败",
                "message": result.get("message", ""),
                "response_time": result.get("response_time", "N/A"),
                "details": result,
                "method": "RequestUtils"
            }
            self._save_test_history(test_record)
            logger.info(f"[RequestUtils] 代理测试完成: {test_record['status']}")
        return True

    def _save_test_history(self, test_data):
        """保存测试历史记录"""
        try:
            # 获取现有历史记录
            history = self.get_data('test_history') or []
            
            # 添加新记录
            history.append(test_data)
            
            # 清理过期记录
            if self._history_days > 0:
                cutoff_date = datetime.now() - timedelta(days=self._history_days)
                history = [
                    record for record in history
                    if datetime.strptime(record.get('date', '1970-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S') >= cutoff_date
                ]
            
            # 保存回数据库
            self.save_data('test_history', history)
            logger.info(f"测试历史记录已保存，共 {len(history)} 条记录")
        except Exception as e:
            logger.error(f"保存测试历史记录失败: {str(e)}")

    def get_state(self) -> bool:
        return self._enabled and self._scheduler and self._scheduler.running

    def get_service(self) -> List[Dict[str, Any]]:
        """注册插件服务"""
        if self._enabled and self._cron:
            return [{
                'name': '代理地址测试服务',
                'type': '定时任务',
                'function': 'test_proxy',
                'icon': 'mdi:lan-connect',
                'trigger': self._cron
            }]
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
                                    'md': 3
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
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'use_proxy',
                                            'label': '使用环境变量代理',
                                            'hint': '使用容器的系统代理环境变量',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'use_proxy_host',
                                            'label': '使用PROXY_HOST',
                                            'hint': '使用PROXY_HOST环境变量作为代理',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
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
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'use_requests',
                                            'label': '使用requests测试',
                                            'hint': '用requests库进行代理测试',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'use_requestutils',
                                            'label': '使用RequestUtils测试',
                                            'hint': '用RequestUtils进行代理测试',
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
                                            'model': 'test_url',
                                            'label': '测试网址',
                                            'placeholder': DEFAULT_TEST_URL,
                                            'hint': '输入要测试的网址，默认为Google',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'cron',
                                            'label': '测试周期',
                                            'placeholder': DEFAULT_CRON,
                                            'hint': '五位Cron表达式，默认每4小时一次',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'history_days',
                                            'label': '历史保留天数',
                                            'placeholder': str(DEFAULT_HISTORY_DAYS),
                                            'hint': '测试历史记录的保留天数',
                                            'persistent-hint': True,
                                            'type': 'number'
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
            "use_proxy": self._use_proxy,
            "use_proxy_host": self._use_proxy_host,
            "use_requests": self._use_requests,
            "use_requestutils": self._use_requestutils,
            "onlyonce": False,
            "test_url": self._test_url or DEFAULT_TEST_URL,
            "cron": self._cron or DEFAULT_CRON,
            "history_days": self._history_days
        }

    def get_page(self) -> List[dict]:
        """获取插件页面"""
        # 获取测试历史记录
        history = self.get_data('test_history') or []
        history.sort(key=lambda x: x.get('date', ''), reverse=True)  # 按日期倒序排列
        
        # 构建数据表格的列配置
        columns = [
            {'field': 'date', 'title': '测试时间', 'width': '180px'},
            {'field': 'url', 'title': '测试网址', 'width': '200px'},
            {'field': 'proxy_mode', 'title': '代理模式', 'width': '100px'},
            {'field': 'status', 'title': '状态', 'width': '80px'}
        ]
        
        # 构建表格的选项配置
        options = {
            'headers': columns,
            'itemsPerPage': 10,
            'itemsPerPageOptions': [10, 20, 50],
            'sortBy': [{'key': 'date', 'order': 'desc'}],
            'separator': 'horizontal',
            'class': 'elevation-0',
            'footerProps': {'showFirstLastPage': True, 'itemsPerPageOptions': [10, 20, 50]}
        }
        
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
                                'component': 'VAnchor',
                                'props': {
                                    'text': '代理测试历史记录',
                                    'subtext': f'共 {len(history)} 条记录'
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
                                'component': 'VCard',
                                'props': {
                                    'variant': 'tonal',
                                    'class': 'mb-4'
                                },
                                'content': [
                                    {
                                        'component': 'VCardText',
                                        'content': [
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
                                                                'component': 'div',
                                                                'text': '环境变量中的代理设置:',
                                                                'props': {
                                                                    'class': 'text-subtitle-1 font-weight-bold'
                                                                }
                                                            },
                                                            {
                                                                'component': 'div',
                                                                'text': "HTTP_PROXY: " + (os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy') or '未设置'),
                                                                'props': {
                                                                    'class': 'text-body-1 mt-2'
                                                                }
                                                            },
                                                            {
                                                                'component': 'div',
                                                                'text': "HTTPS_PROXY: " + (os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy') or '未设置'),
                                                                'props': {
                                                                    'class': 'text-body-1'
                                                                }
                                                            },
                                                            {
                                                                'component': 'div',
                                                                'text': "NO_PROXY: " + (os.environ.get('NO_PROXY') or os.environ.get('no_proxy') or '未设置'),
                                                                'props': {
                                                                    'class': 'text-body-1'
                                                                }
                                                            },
                                                            {
                                                                'component': 'div',
                                                                'text': "PROXY_HOST: " + (os.environ.get('PROXY_HOST') or '未设置'),
                                                                'props': {
                                                                    'class': 'text-body-1'
                                                                }
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
                                'component': 'VDataTable',
                                'props': {
                                    'headers': options['headers'],
                                    'items': history,
                                    'itemsPerPage': options['itemsPerPage'], 
                                    'footer-props': options['footerProps'],
                                    'class': 'elevation-1',
                                    'expand-on-click': True
                                },
                                'slots': {
                                    'expanded-row': {
                                        'component': 'VCard',
                                        'props': {
                                            'class': 'ma-2',
                                            'elevation': 1,
                                            'variant': 'flat'
                                        },
                                        'content': [
                                            {
                                                'component': 'VCardText',
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
                                                                        'component': 'div',
                                                                        'props': {
                                                                            'class': 'text-subtitle-2 font-weight-bold'
                                                                        },
                                                                        'text': '使用代理:'
                                                                    },
                                                                    {
                                                                        'component': 'div',
                                                                        'props': {
                                                                            'class': 'text-body-1 mb-2'
                                                                        },
                                                                        'text': '{{ item.raw.proxy }}'
                                                                    },
                                                                    {
                                                                        'component': 'div',
                                                                        'props': {
                                                                            'class': 'text-subtitle-2 font-weight-bold'
                                                                        },
                                                                        'text': '响应时间:'
                                                                    },
                                                                    {
                                                                        'component': 'div',
                                                                        'props': {
                                                                            'class': 'text-body-1'
                                                                        },
                                                                        'text': '{{ item.raw.response_time }}'
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
                                                                        'component': 'div',
                                                                        'props': {
                                                                            'class': 'text-subtitle-2 font-weight-bold'
                                                                        },
                                                                        'text': '状态信息:'
                                                                    },
                                                                    {
                                                                        'component': 'div',
                                                                        'props': {
                                                                            'class': 'text-body-1'
                                                                        },
                                                                        'text': '{{ item.raw.message }}'
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        ]

    def stop_service(self):
        """停止插件服务"""
        try:
            if self._scheduler:
                self._scheduler.shutdown()
                self._scheduler = None
                logger.info("代理地址测试服务已停止")
            return True
        except Exception as e:
            logger.error(f"停止代理地址测试服务失败: {str(e)}")
            return False

    def get_command(self) -> List[Dict[str, Any]]:
        """注册命令"""
        return [{
            "cmd": "/testproxy",
            "event": self.test_proxy,
            "desc": "手动执行代理地址测试"
        }]

    def get_api(self) -> List[Dict[str, Any]]:
        """注册API"""
        return [] 
