"""
站点签到（多站点版）插件
版本: 1.1.3
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
# 重新导入 BackgroundScheduler 用于“立即运行一次”功能
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
    plugin_version = "1.1.3"
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
    _cron = None
    _site_configs = ""
    _history_days = DEFAULT_HISTORY_DAYS
    _success_keywords_str = DEFAULT_SUCCESS_KEYWORDS_STR
    _success_keywords = DEFAULT_SUCCESS_KEYWORDS.copy()
    _msgtype = None
    # 注意：这里我们不保留 scheduler 实例作为类属性，因为它只是临时使用

    def init_plugin(self, config: dict = None):
        logger.info("============= 站点签到（多站点版）插件初始化 =============")
        
        # 加载配置
        if config:
            self._enabled = config.get("enabled")
            self._site_configs = config.get("site_configs", "")
            self._notify = config.get("notify")
            self._msgtype = config.get("msgtype")
            self._cron = config.get("cron") or DEFAULT_CRON
            self._history_days = int(config.get("history_days", DEFAULT_HISTORY_DAYS))
            self._success_keywords_str = config.get("success_keywords", DEFAULT_SUCCESS_KEYWORDS_STR)
            
            self._parse_success_keywords()
            
            logger.info(f"配置: enabled={self._enabled}, notify={self._notify}, msgtype={self._msgtype}, cron={self._cron}, history_days={self._history_days}")
            logger.info(f"成功关键词: {', '.join(self._success_keywords)}")
            
            site_count = len(self._parse_site_configs())
            logger.info(f"已配置 {site_count} 个站点")

            # 【关键修改】处理“立即运行一次”的逻辑，使用临时的调度器
            onlyonce = config.get("onlyonce")
            if onlyonce:
                logger.info("创建一个临时任务，将在3秒后执行一次性签到...")
                # 创建一个临时的、独立的调度器，只用于这次任务
                temp_scheduler = BackgroundScheduler(timezone=settings.TZ)
                temp_scheduler.add_job(func=self.sign, 
                                       trigger='date',
                                       run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=3),
                                       name="站点签到（多站点版）- 单次运行")
                temp_scheduler.start()
                
                # 重置 onlyonce 状态
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
    
    def _parse_success_keywords(self):
        """解析用户输入的成功关键词"""
        if not self._success_keywords_str:
            self._success_keywords = DEFAULT_SUCCESS_KEYWORDS.copy()
            return
            
        keywords = [kw.strip() for kw in self._success_keywords_str.split('|') if kw.strip()]
        
        if keywords:
            self._success_keywords = keywords
        else:
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
                logger.error(error_msg, exc_info=True)
                results.append(error_msg)
        
        sign_record = {
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "results": results,
            "total": len(site_configs),
            "success": sum(1 for r in results if "签到成功" in r or "已经签到过了" in r),
            "failed": sum(1 for r in results if "签到失败" in r or "请检查" in r)
        }
        
        self._save_sign_history(sign_record)
        
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
        
        try:
            if request_type == 'GET':
                response = requests.get(sign_url, headers=headers, timeout=30)
            elif request_type == 'POST':
                response = requests.post(sign_url, headers=headers, timeout=30)
            else:
                return f'{site_name} 签到失败，不支持的请求类型：{request_type}'
        except requests.exceptions.RequestException as e:
            logger.error(f'签到请求失败，站点：{site_name} ({sign_url})，错误：{e}')
            return f'{site_name} 签到失败，网络请求错误：{e}'
        
        if response.status_code != 200:
            return f'{site_name} 签到失败，HTTP 状态码：{response.status_code}'
        
        for keyword in self._success_keywords:
            if keyword in response.text:
                logger.info(f'站点：{site_name} ({sign_url})，签到成功！关键词：{keyword}')
                return f'{site_name} 签到成功'

        soup = BeautifulSoup(response.text, 'html.parser')
        sign_status = soup.find('font', color='red')
        
        if sign_status and '今天已签到' in sign_status.get_text():
            logger.info(f'站点：{site_name} ({sign_url})，今天已经签到过了。')
            return f'{site_name} 今天已经签到过了'

        logger.warning(f'站点：{site_name} ({sign_url})，签到可能没有成功，请检查。')
        return f'{site_name} 签到可能没有成功，请检查'

    def _save_sign_history(self, sign_data):
        """保存签到历史记录"""
        try:
            history = self.get_data('sign_history') or []
            history.append(sign_data)
            
            if self._history_days > 0:
                cutoff_date = datetime.now() - timedelta(days=self._history_days)
                history = [
                    record for record in history
                    if datetime.strptime(record.get('date', '1970-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S') >= cutoff_date
                ]
            
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
            
            title = f"【站点签到（多站点版）结果】"
            text = (
                f"━━━━━━━━━\n"
                f"🕐 时间：{sign_date}\n"
                f"📊 统计：成功 {success} 个，失败 {failed} 个\n"
                f"━━━━━━━━━\n"
                f"📋 详细结果：\n"
            )
            for result in results:
                text += f"• {result}\n"
            
            mtype = NotificationType.SiteMessage
            if self._msgtype:
                try:
                    mtype = NotificationType[str(self._msgtype)]
                except Exception as e:
                    logger.error(f"通知类型 '{self._msgtype}' 无效，使用默认通知类型: {e}")
            
            self.post_message(mtype=mtype, title=title, text=text)
            logger.info("签到结果通知已发送")
        except Exception as e:
            logger.error(f"发送签到通知失败: {str(e)}")

    def get_state(self) -> bool:
        return self._enabled

    def get_service(self) -> List[Dict[str, Any]]:
        """
        【正确的方式】向 MoviePilot 框架注册常规的定时服务。
        """
        if self._enabled and self._cron:
            try:
                if str(self._cron).strip().count(" ") == 4:
                    return [{
                        "id": "dzdsingin",
                        "name": "站点签到（多站点版）服务",
                        "trigger": CronTrigger.from_crontab(self._cron, timezone=settings.TZ),
                        "func": self.sign,
                        "kwargs": {}
                    }]
                else:
                    logger.error(f"站点签到（多站点版）的Cron表达式 '{self._cron}' 格式不正确，服务启动失败。")
            except Exception as e:
                logger.error(f"站点签到（多站点版）注册定时任务失败：{e}", exc_info=True)
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """获取表单配置"""
        MsgTypeOptions = [{"title": item.value, "value": item.name} for item in NotificationType]
        
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {'component': 'VCol', 'props': {'cols': 12, 'md': 4},'content': [{'component': 'VSwitch', 'props': {'model': 'enabled', 'label': '启用插件', 'hint': '开启或关闭插件', 'persistent-hint': True}}]},
                            {'component': 'VCol', 'props': {'cols': 12, 'md': 4},'content': [{'component': 'VSwitch', 'props': {'model': 'notify', 'label': '开启通知', 'hint': '签到后是否发送通知消息', 'persistent-hint': True}}]},
                            {'component': 'VCol', 'props': {'cols': 12, 'md': 4},'content': [{'component': 'VSwitch', 'props': {'model': 'onlyonce', 'label': '立即运行一次', 'hint': '保存后立即执行一次', 'persistent-hint': True}}]}
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {'component': 'VCol', 'props': {'cols': 12, 'md': 4},'content': [{'component': 'VTextField', 'props': {'model': 'cron', 'label': '签到周期', 'placeholder': DEFAULT_CRON, 'hint': '五位Cron表达式，默认每天8点', 'persistent-hint': True}}]},
                            {'component': 'VCol', 'props': {'cols': 12, 'md': 4},'content': [{'component': 'VTextField', 'props': {'model': 'history_days', 'label': '历史保留天数', 'placeholder': str(DEFAULT_HISTORY_DAYS), 'hint': '签到历史记录的保留天数', 'persistent-hint': True, 'type': 'number'}}]},
                            {'component': 'VCol', 'props': {'cols': 12, 'md': 4},'content': [{'component': 'VSelect', 'props': {'model': 'msgtype', 'label': '通知渠道', 'items': MsgTypeOptions, 'hint': '选择签到结果通知渠道', 'persistent-hint': True}}]}
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {'component': 'VCol', 'props': {'cols': 12},'content': [{'component': 'VTextField', 'props': {'model': 'success_keywords', 'label': '成功关键词', 'placeholder': DEFAULT_SUCCESS_KEYWORDS_STR, 'hint': '签到成功的判断关键词，多个关键词用|分隔', 'persistent-hint': True}}]}
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {'component': 'VCol', 'props': {'cols': 12},'content': [{'component': 'VTextarea', 'props': {'model': 'site_configs', 'label': '站点配置', 'placeholder': '站点名称|签到地址|请求类型(GET/POST)|referer地址|站点cookie', 'hint': '每行一个站点，格式为：站点名称|签到地址|请求类型（GET/POST）|referer地址（一般为站点URL基础地址即可）|站点cookie', 'persistent-hint': True, 'rows': 8}}]}
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
        history = self.get_data('sign_history') or []
        history.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        columns = [
            {'title': '签到时间', 'key': 'date', 'width': '180px'},
            {'title': '总数', 'key': 'total', 'width': '70px'},
            {'title': '成功', 'key': 'success', 'width': '70px'},
            {'title': '失败', 'key': 'failed', 'width': '70px'},
            {'title': '', 'key': 'data-table-expand' },
        ]
        
        # 兼容新旧版本Vuetify的DataTable语法
        page_content = [
            {
                'component': 'VCard', 'props': {'title': '签到历史记录', 'subtitle': f'共 {len(history)} 条记录'},
                'content': [
                    {
                        'component': 'VDataTable',
                        'props': {
                            'headers': columns,
                            'items': history,
                            'items-per-page': 10,
                            'show-expand': True,
                            'expand-on-click': True,
                            'item-value': 'date'
                        },
                        'slots': {
                            'expanded-row': {
                                'component': 'VSheet', 'props': {'class': 'pa-4'},
                                'content': [
                                    {'component': 'div', 'props': {'v-html': 'props.item.raw.results.join("<br>")'}}
                                ]
                            }
                        }
                    }
                ]
            }
        ]

        # 尝试适配较新版本的VDataTable插槽语法
        try:
            from inspect import signature
            page_content[0]['content'][0]['slots']['expanded-row'] = {
                'component': 'td', 'props': {'colspan': len(columns)}, 'content': [
                    {'component': 'VSheet', 'props': {'class': 'pa-4'}, 'content': [
                        {'component': 'div', 'props': {'v-html': 'item.raw.results.join("<br>")'}}
                    ]}
                ]
            }
        except Exception:
            pass

        return page_content

    def stop_service(self):
        """停止插件服务"""
        logger.info("站点签到（多站点版）插件已停用。")
        return True

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
