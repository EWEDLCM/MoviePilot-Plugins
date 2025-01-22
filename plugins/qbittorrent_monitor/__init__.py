import os
import requests
from urllib.parse import urlparse
from typing import Any, List, Dict
from app.log import logger
from app.plugins.customplugin.task import UserTaskBase
from app.core.event import eventmanager, Event
from app.schemas.types import EventType


# 全局配置：是否显示详细的错误信息
SHOW_ERROR_DETAILS = False  # 设置为 False 则不显示详细信息

# qBittorrent Web UI的配置信息列表，一个一行
QB_CONFIG = [
    {'url': 'http://192.168.2.2:18090', 'username': 'cming', 'password': 'cmingcming'},
    {'url': 'http://192.168.2.2:18091', 'username': 'cming', 'password': 'cmingcming'},
]


class QBittorrentMonitor(UserTaskBase):
    task_id = "qbittorrent_monitor"  # 添加任务 ID

    def __init__(self):
        super().__init__()
        self.enabled = True  # 默认启用
        self.session = requests.Session()

    def start(self):
        """
        开始任务时调用此方法
        """
        logger.info("QBittorrent Monitor Task Started.")
        self.check_qbittorrent_status()

    def stop(self):
        """
        停止任务时调用此方法
        """
        logger.info("QBittorrent Monitor Task Stopped.")
        # 可以添加清理资源的代码，例如关闭 session
        self.session.close()

    def login_to_qb(self, config):
        """登录到qBittorrent"""
        try:
            response = self.session.post(f"{config['url']}/api/v2/auth/login", data=config, timeout=10)
            if response.status_code == 200 and response.text.strip() == 'Ok.':
                logger.info(f"成功登录 {config['url']}")
                return True
            else:
                logger.warning(f"登录失败 {config['url']}，状态码: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"登录 {config['url']} 时出现异常: {e}")
            return False

    def get_torrents_status(self, url):
        """获取所有任务的状态和属性（包含tracker信息）"""
        try:
            response = self.session.get(f'{url}/api/v2/torrents/info', timeout=10)
            if response.status_code == 200:
                torrents_info = response.json()
                torrents_with_trackers = []
                for torrent in torrents_info:
                    hash_value = torrent.get('hash')
                    trackers_response = self.session.get(f'{url}/api/v2/torrents/trackers', params={'hash': hash_value},
                                                         timeout=10)
                    if trackers_response.status_code == 200:
                        torrent['trackers'] = trackers_response.json()
                        torrents_with_trackers.append(torrent)
                    else:
                        logger.warning(f"获取种子 {torrent.get('name')} 的 tracker 信息失败，状态码：{trackers_response.status_code}")
                return torrents_with_trackers
            else:
                logger.error(f"获取下载任务列表失败，状态码: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"获取下载任务列表时出现异常: {e}")
            return []

    def check_errors(self, torrents_info):
        """统计正常和错误的任务数量，并记录错误和tracker异常的详情"""
        error_count = 0
        error_details = []
        no_working_tracker_count = 0
        no_working_tracker_details = {}
        tracker_error_urls = set()

        for t in torrents_info:
            state = t.get('state').lower()
            if state in ['error', 'missingfiles']:
                error_count += 1
                if SHOW_ERROR_DETAILS:
                    error_details.append({
                        'name': t.get('name'),
                        'hash': t.get('hash'),
                        'state': state,
                        'progress': t.get('progress'),
                        'error': t.get('error'),
                        'tracker': t.get('tracker')
                    })

            trackers = t.get('trackers')
            if trackers is None:
                continue
            if isinstance(trackers, list):
                has_working_tracker = False
                first_error_url = None
                for tracker in trackers:
                    if tracker.get('status') == 2:
                        has_working_tracker = True
                        break
                    elif first_error_url is None:
                        url = tracker.get('url')
                        if url:
                            parsed_url = urlparse(url)
                            if parsed_url.scheme and parsed_url.netloc:
                                first_error_url = parsed_url.scheme + "://" + parsed_url.netloc
                if not has_working_tracker:
                    no_working_tracker_count += 1
                    if first_error_url:
                        if first_error_url not in no_working_tracker_details:
                            no_working_tracker_details[first_error_url] = []
                        no_working_tracker_details[first_error_url].append(t.get('name'))
                    if first_error_url:
                        tracker_error_urls.add(first_error_url)

        return len(torrents_info), error_count, error_details, no_working_tracker_count, no_working_tracker_details, tracker_error_urls

    @eventmanager.register(EventType.PluginAction)
    def check_qbittorrent_status(self, event: Event = None):
        """检查 qBittorrent 状态并发送通知"""
        if event:
            event_data = event.event_data
            if not event_data or event_data.get("action") != "qb_check":
                return
            logger.info("收到命令，开始QB下载器检测 ...")
            self.post_message(channel=event.event_data.get("channel"),
                              title="开始QB下载器检测 ...",
                              userid=event.event_data.get("user"))
        
        notification_message = "下载器状态报告:\n"
        results_log = []
        for index, config in enumerate(QB_CONFIG):
            if self.login_to_qb(config):
                torrents_info = self.get_torrents_status(config['url'])
                total, errors, error_details, no_working_tracker_count, no_working_tracker_details, tracker_error_urls = self.check_errors(torrents_info)
                status_msg = (
                    f"下载器地址: {config['url']}\n"
                    f"总任务数: {total}\n"
                    f"正常任务数: {total - errors}\n"
                    f"错误任务数: {errors}\n"
                )
                notification_message += status_msg
                results_log.append(status_msg)

                if no_working_tracker_count > 0:
                    status_msg = f"tracker 异常: {no_working_tracker_count}\n"
                else:
                    status_msg = f"tracker 异常: 0\n"
                notification_message += status_msg
                results_log.append(status_msg)

                if errors > 0:
                    if SHOW_ERROR_DETAILS:
                        details_msg = "错误种子详情:\n"
                        for detail in error_details:
                            details_msg += (
                                f"名称: {detail['name']}\n"
                                f"状态: {detail['state']}\n"
                                f"进度: {detail['progress']}\n"
                                f"错误信息: {detail['error']}\n"
                            )
                        notification_message += details_msg + "\n"
                        results_log.append(details_msg)
                    else:
                        notification_message += "错误种子详情已关闭\n"
                        results_log.append("错误种子详情已关闭\n")

                if no_working_tracker_count > 0:
                    no_tracker_msg = f"异常Tracker详情:\n"
                    for url, torrents in no_working_tracker_details.items():
                        no_tracker_msg += f"{url}  共{len(torrents)}个\n"
                        if SHOW_ERROR_DETAILS:
                            for torrent in torrents:
                                no_tracker_msg += f"{torrent}\n"
                        no_tracker_msg += "\n"
                    notification_message += no_tracker_msg
                    results_log.append(no_tracker_msg)
                else:
                    notification_message += "\n"
                    results_log.append("\n")
            else:
                status_msg = f"下载器地址: {config['url']} 登录失败。\n\n"
                notification_message += status_msg
                results_log.append(status_msg)

            if index < len(QB_CONFIG) - 1:
                notification_message += "\n"
                results_log.append("\n")

        if notification_message.endswith("\n\n"):
            notification_message = notification_message[:-2]
        
        # self.send_wechat_notification(notification_message)
        self.post_message(title="QB下载器检测结果", message=notification_message)
        print("".join(results_log))

        if event:
            self.post_message(channel=event.event_data.get("channel"),
                              title="QB下载器检测完成！",
                              userid=event.event_data.get("user"))

    def get_command(self) -> List[Dict[str, Any]]:
        """
        定义远程控制命令
        :return: 命令关键字、事件、描述、附带数据
        """
        return [{
            "cmd": "/qbcheck",
            "event": EventType.PluginAction,
            "desc": "QB下载器检测",
            "category": "",
            "data": {
                "action": "qb_check"
            }
        }]
