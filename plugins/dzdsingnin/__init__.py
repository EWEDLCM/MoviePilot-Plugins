"""
站点签到（多站点版）插件
版本: 1.1.0
作者: EWEDL
功能:
- 支持多个站点同时签到
- 支持用户通过文本框自定义站点配置
- 支持GET和POST两种签到请求方式
- 自定义成功关键词检测
- 可配置签到时间和频率
- 签到结果通知（支持自定义通知渠道）
- 签到历史记录查看
"""
import time
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.plugins import _PluginBase
from typing import Any, List, Dict, Tuple, Optional
from app.log import logger
from app.schemas import NotificationType


# 定义默认值常量
DEFAULT_SUCCESS_KEYWORDS = ["获得魔力值", "签到成功", "已签到", "签到过了"]
DEFAULT_SUCCESS_KEYWORDS_STR = "|".join(DEFAULT_SUCCESS_KEYWORDS)
DEFAULT_HISTORY_DAYS = 30
DEFAULT_CRON = "0 8 * * *"


class dzdsingnin(_PluginBase):
    # 插件名称
    plugin_name = "站点签到（多站点版）"
    # 插件描述
    plugin_desc = "支持多个站点的自动签到功能，用户可自定义签到站点配置"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/EWEDLCM/MoviePilot-Plugins/main/icons/dzdsingnin.png"
    # 插件版本
    plugin_version = "1.1.0"
    # 插件作者
    plugin_author = "EWEDL"
    # 作者主页
    author_url = "https://github.com/EWEDLCM"
    # 插件配置项ID前缀
    plugin_config_prefix = "dzdsingnin_"
    # 加载顺序
    plugin_order = 1
    # 可使用的用户级别
    auth_level = 2

    # 私有属性
    _enabled = False
    _notify = False
    _onlyonce = False
    _cron = None
    _site_configs = ""
    _history_days = DEFAULT_HISTORY_DAYS  # 历史保留天数
    _success_keywords_str = DEFAULT_SUCCESS_KEYWORDS_STR  # 存储用户输入的关键词字符串
    # 全局签到检查关键词
    _success_keywords = DEFAULT_SUCCESS_KEYWORDS.copy()
    # 通知渠道
    _msgtype = None
    # 定时器
    _scheduler: Optional[BackgroundScheduler] = None

    def init_plugin(self, config: dict = None):
        # 停止现有任务
        self.stop_service()

        logger.info("============= 站点签到（多站点版）插件初始化 =============")
        try:
            if config:
                self._enabled = config.get("enabled")
                self._site_configs = config.get("site_configs", "")
                self._notify = config.get("notify")
                self._msgtype = config.get("msgtype")
                self._cron = config.get("cron")
                self._onlyonce = config.get("onlyonce")
                self._history_days = int(config.get("history_days", DEFAULT_HISTORY_DAYS))
                self._success_keywords_str = config.get("success_keywords", DEFAULT_SUCCESS_KEYWORDS_STR)
                
                # 解析成功关键词
                self._parse_success_keywords()
                
                logger.info(f"配置: enabled={self._enabled}, notify={self._notify}, msgtype={self._msgtype}, cron={self._cron}, history_days={self._history_days}")
                logger.info(f"成功关键词: {', '.join(self._success_keywords)}")
                
                # 解析站点配置
                site_count = len(self._parse_site_configs())
                logger.info(f"已配置 {site_count} 个站点")
            
            if self._onlyonce:
                logger.info("执行一次性签到")
                self._scheduler = BackgroundScheduler(timezone=settings.TZ)
                self._scheduler.add_job(func=self.sign, trigger='date',
                                    run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=3),
                                    name="站点签到（多站点版）")
                self._onlyonce = False
                self.update_config({
                    "onlyonce": False,
                    "enabled": self._enabled,
                    "site_configs": self._site_configs,
                    "notify": self._notify,
                    "msgtype": self._msgtype,
                    "cron": self._cron,
                    "history_days": self._history_days,
                    "success_keywords": self._success_keywords_str
                })

                # 启动任务
                if self._scheduler.get_jobs():
                    self._scheduler.print_jobs()
                    self._scheduler.start()
            elif self._enabled and self._cron:
                # 启动定时任务
                self._scheduler = BackgroundScheduler(timezone=settings.TZ)
                self._scheduler.add_job(func=self.sign,
                                     trigger=CronTrigger.from_crontab(self._cron),
                                     name="站点签到（多站点版）")
                logger.info(f"已启动定时任务，cron: {self._cron}")
                
                # 启动任务
                if self._scheduler.get_jobs():
                    self._scheduler.print_jobs()
                    self._scheduler.start()

        except Exception as e:
            logger.error(f"站点签到（多站点版）插件初始化错误: {str(e)}", exc_info=True)
    
    def _parse_success_keywords(self):
        """解析用户输入的成功关键词"""
        if not self._success_keywords_str:
            # 如果用户未输入，使用默认值
            self._success_keywords = DEFAULT_SUCCESS_KEYWORDS.copy()
            return
            
        # 按分隔符分割并去除空白
        keywords = [kw.strip() for kw in self._success_keywords_str.split('|') if kw.strip()]
        
        if keywords:
            self._success_keywords = keywords
            logger.info(f"已设置自定义成功关键词: {', '.join(keywords)}")
        else:
            # 如果解析后为空，使用默认值
            self._success_keywords = DEFAULT_SUCCESS_KEYWORDS.copy()
            logger.warning("自定义关键词解析为空，使用默认关键词")

    def _parse_site_configs(self) -> List[Dict[str, str]]:
        """解析用户输入的站点配置"""
        configs = []
        if not self._site_configs:
            return configs
            
        lines = self._site_configs.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            parts = line.split('|')
            if len(parts) >= 5:
                site_name = parts[0].strip()
                sign_url = parts[1].strip()
                request_type = parts[2].strip().upper()
                referer = parts[3].strip()
                cookie = parts[4].strip()
                
                if site_name and sign_url and request_type in ['GET', 'POST'] and cookie:
                    configs.append({
                        'site_name': site_name,
                        'sign_url': sign_url,
                        'request_type': request_type,
                        'referer': referer,
                        'cookie': cookie
                    })
                else:
                    logger.warning(f"站点配置格式错误，已跳过: {line}")
        
        return configs

    def sign(self):
        """执行所有站点的签到"""
        logger.info("============= 开始站点签到（多站点版） =============")
        results = []
        site_configs = self._parse_site_configs()
        
        if not site_configs:
            logger.warning("没有配置任何站点，签到已跳过")
            return

        # 记录开始时间
        start_time = datetime.now()
        
        # 执行每个站点的签到
        for config in site_configs:
            site_name = config['site_name']
            sign_url = config['sign_url']
            request_type = config['request_type']
            referer = config['referer']
            cookie = config['cookie']
            
            try:
                result = self._do_sign(sign_url, cookie, site_name, request_type, referer)
                results.append(result)
            except Exception as e:
                error_msg = f"{site_name} 签到失败，错误: {str(e)}"
                logger.error(error_msg)
                results.append(error_msg)
        
        # 构建签到记录
        sign_record = {
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "results": results,
            "total": len(site_configs),
            "success": sum(1 for r in results if "签到成功" in r or "已经签到过了" in r),
            "failed": sum(1 for r in results if "签到失败" in r or "请检查" in r)
        }
        
        # 保存签到记录
        self._save_sign_history(sign_record)
        
        # 发送通知
        if self._notify:
            self._send_sign_notification(sign_record)
            
        logger.info(f"所有站点签到完成，成功: {sign_record['success']}，失败: {sign_record['failed']}")
        return sign_record

    def _do_sign(self, sign_url, cookie, site_name, request_type, referer):
        """执行单个站点的签到"""
        logger.info(f'开始签到，站点：{site_name} ({sign_url})')
        
        if not cookie:
            logger.error(f'站点 {site_name} 的Cookie为空，跳过此站点')
            return f'{site_name} 签到失败，Cookie为空'
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Content-Type': 'text/html; charset=UTF-8',
            'Cookie': cookie,
            'Referer': referer
        }
        
        # 发送签到请求
        try:
            if request_type == 'GET':
                response = requests.get(sign_url, headers=headers, timeout=30)
            elif request_type == 'POST':
                response = requests.post(sign_url, headers=headers, timeout=30)
            else:
                logger.error(f'不支持的请求类型：{request_type}，站点：{site_name} ({sign_url})')
                return f'{site_name} 签到失败，不支持的请求类型：{request_type}'
        except requests.exceptions.RequestException as e:
            logger.error(f'签到请求失败，站点：{site_name} ({sign_url})，错误：{e}')
            return f'{site_name} 签到失败，网络请求错误：{e}'
        
        # 检查响应状态码
        if response.status_code != 200:
            logger.error(f'签到请求失败，站点：{site_name} ({sign_url})，HTTP {response.status_code}')
            return f'{site_name} 签到失败，HTTP 状态码：{response.status_code}'
        
        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        sign_status = soup.find('font', color='red')
        
        if sign_status and '今天已签到' in sign_status.get_text():
            # 今天已经签到了
            logger.info(f'站点：{site_name} ({sign_url})，今天已经签到过了。')
            return f'{site_name} 今天已经签到过了'
        
        # 查找签到成功的标志，使用用户配置的关键词
        for keyword in self._success_keywords:
            if keyword in response.text:
                logger.info(f'站点：{site_name} ({sign_url})，签到成功！关键词：{keyword}')
                return f'{site_name} 签到成功'
        
        # 如果没有匹配到任何关键词
        logger.warning(f'站点：{site_name} ({sign_url})，签到可能没有成功，请检查。')
        return f'{site_name} 签到可能没有成功，请检查'

    def _save_sign_history(self, sign_data):
        """保存签到历史记录"""
        try:
            # 获取现有历史记录
            history = self.get_data('sign_history') or []
            
            # 添加新记录
            history.append(sign_data)
            
            # 清理过期记录
            if self._history_days > 0:
                cutoff_date = datetime.now() - timedelta(days=self._history_days)
                history = [
                    record for record in history
                    if datetime.strptime(record.get('date', '1970-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S') >= cutoff_date
                ]
            
            # 保存回数据库
            self.save_data('sign_history', history)
            logger.info(f"签到历史记录已保存，共 {len(history)} 条记录")
        except Exception as e:
            logger.error(f"保存签到历史记录失败: {str(e)}")

    def _send_sign_notification(self, sign_record):
        """发送签到结果通知"""
        try:
            total = sign_record['total']
            success = sign_record['success']
            failed = sign_record['failed']
            results = sign_record['results']
            sign_date = sign_record['date']
            
            # 构建通知标题和内容
            title = f"【站点签到（多站点版）结果】"
            
            text = (
                f"━━━━━━━━━━━━━━━━━\n"
                f"🕐 时间：{sign_date}\n"
                f"📊 统计：成功 {success} 个，失败 {failed} 个\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"📋 详细结果：\n"
            )
            
            for result in results:
                text += f"• {result}\n"
            
            # 根据配置选择通知类型
            mtype = NotificationType.SiteMessage
            if self._msgtype:
                try:
                    mtype = NotificationType.__getitem__(str(self._msgtype)) or NotificationType.SiteMessage
                    logger.info(f"使用自定义通知类型: {mtype}")
                except Exception as e:
                    logger.error(f"通知类型转换错误: {str(e)}，使用默认通知类型")
            
            # 发送通知
            self.post_message(
                mtype=mtype,
                title=title,
                text=text
            )
            logger.info("签到结果通知已发送")
        except Exception as e:
            logger.error(f"发送签到通知失败: {str(e)}")

    def get_state(self) -> bool:
        return self._enabled and self._scheduler and self._scheduler.running

    def get_service(self) -> List[Dict[str, Any]]:
        """注册插件服务"""
        if self._enabled and self._cron:
            return [{
                'name': '站点签到（多站点版）服务',
                'type': '定时任务',
                'function': 'sign',
                'icon': 'calendar-check',
                'trigger': self._cron
            }]
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """获取表单配置"""
        # 编历 NotificationType 枚举，生成消息类型选项
        MsgTypeOptions = []
        for item in NotificationType:
            MsgTypeOptions.append({
                "title": item.value,
                "value": item.name
            })
        
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
                                            'model': 'notify',
                                            'label': '开启通知',
                                            'hint': '签到后是否发送通知消息',
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
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'cron',
                                            'label': '签到周期',
                                            'placeholder': DEFAULT_CRON,
                                            'hint': '五位Cron表达式，默认每天8点',
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
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'history_days',
                                            'label': '历史保留天数',
                                            'placeholder': str(DEFAULT_HISTORY_DAYS),
                                            'hint': '签到历史记录的保留天数',
                                            'persistent-hint': True,
                                            'type': 'number'
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
                                        'component': 'VSelect',
                                        'props': {
                                            'model': 'msgtype',
                                            'label': '通知渠道',
                                            'items': MsgTypeOptions,
                                            'hint': '选择签到结果通知渠道',
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
                                            'model': 'success_keywords',
                                            'label': '成功关键词',
                                            'placeholder': DEFAULT_SUCCESS_KEYWORDS_STR,
                                            'hint': '签到成功的判断关键词，多个关键词用|分隔',
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
                                        'component': 'VTextarea',
                                        'props': {
                                            'model': 'site_configs',
                                            'label': '站点配置',
                                            'placeholder': '站点名称|签到地址|请求类型(GET/POST)|referer地址|站点cookie',
                                            'hint': '每行一个站点，格式为：站点名称|签到地址|请求类型（GET/POST）|referer地址（一般为站点URL基础地址即可）|站点cookie',
                                            'persistent-hint': True,
                                            'rows': 8
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
            "notify": self._notify,
            "onlyonce": False,
            "cron": self._cron or DEFAULT_CRON,
            "site_configs": self._site_configs,
            "history_days": self._history_days,
            "success_keywords": self._success_keywords_str,
            "msgtype": self._msgtype or "SiteMessage"
        }

    def get_page(self) -> List[dict]:
        """获取插件页面"""
        # 获取签到历史记录
        history = self.get_data('sign_history') or []
        history.sort(key=lambda x: x.get('date', ''), reverse=True)  # 按日期倒序排列
        
        # 构建数据表格的列配置
        columns = [
            {'field': 'date', 'title': '签到时间', 'width': '180px'},
            {'field': 'total', 'title': '总数', 'width': '70px'},
            {'field': 'success', 'title': '成功', 'width': '70px'},
            {'field': 'failed', 'title': '失败', 'width': '70px'}
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
                                    'text': '签到历史记录',
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
                                                'props': {
                                                    'style': 'white-space: pre-line;'
                                                },
                                                'slots': {
                                                    'default': {
                                                        'component': 'div',
                                                        'props': {
                                                            'innerHTML': '{{ item.raw.results.join("<br>") }}'
                                                        }
                                                    }
                                                }
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
                logger.info("站点签到（多站点版）服务已停止")
            return True
        except Exception as e:
            logger.error(f"停止站点签到（多站点版）服务失败: {str(e)}")
            return False

    def get_command(self) -> List[Dict[str, Any]]:
        """注册命令"""
        return [{
            "cmd": "/dzdsingnin",
            "event": self.sign,
            "desc": "手动执行站点签到（多站点版）"
        }]

    def get_api(self) -> List[Dict[str, Any]]:
        """注册API"""
        return [] 
