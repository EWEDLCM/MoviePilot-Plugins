import requests
import os
import time
from typing import Dict, List

# 导入UI组件库，例如Vuetify
# 注意：实际应用中需要根据使用的框架导入相应的UI组件
# from some_ui_library import VForm, VSwitch, VSelect, VRow, VCol, VAceEditor, VAlert, VTabs, VTab, VWindow, VWindowItem

class MessageSender(_PluginBase):
    plugin_name = "站点喊话"
    plugin_desc = "向指定的服务发送预设或自定义的消息。"
    plugin_icon = "https://ts4.cn.mm.bing.net/th?id=OIP-C.PqmdypeiQAAyeuMIHeJeXAHaHV&rs=1&pid=ImgDetMain"
    plugin_version = "1.0"
    plugin_author = "YourName"
    author_url = "https://github.com/EWEDLCM"
    plugin_config_prefix = "message_sender_"
    plugin_order = 50
    auth_level = 1

    _enabled = False
    _global_interval = 20
    _services = {
        'QW': {'enabled': True, 'messages': ['蛙总，求上传', '蛙总，求下载']},
        'QCN': {'enabled': True, 'messages': ['青虫娘，求魔力', '青虫娘，求上传']}
    }

    def init_plugin(self, config: dict = None):
        if not config:
            return

        self._enabled = config.get("enabled", False)
        self._global_interval = config.get("global_interval", 20)
        self._services = config.get("services", self._services)

    @property
    def service_infos(self) -> Optional[Dict[str, ServiceInfo]]:
        # 这里可以添加获取服务信息的逻辑
        pass

    def get_state(self) -> bool:
        return self._enabled

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        services = [
            {"title": key, "value": key}
            for key in self._services.keys()
        ]
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
                                            'persistent-hint': True
                                        }
                                    },
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'global_interval',
                                            'label': '全局等待时间(秒)',
                                            'type': 'number'
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 6},
                                'content': [
                                    {
                                        'component': 'VSelect',
                                        'props': {
                                            'multiple': True,
                                            'chips': True,
                                            'clearable': True,
                                            'model': 'selected_services',
                                            'label': '选择服务',
                                            'items': services
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
            "global_interval": self._global_interval,
            "services": self._services
        }

    def send_message_to_service(self, message, service_key):
        service = self._services.get(service_key)
        if not service or not service['enabled']:
            print(f"{service_key}未启用")
            return

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Cookie': os.getenv(f'{service_key}_COOKIE', '').strip(),
            'Referer': f'https://{service_key.lower()}.com/'  # 根据实际情况调整
        }

        params = {
            'shbox_text': message,
            'shout': '我喊',
            'sent': 'yes',
            'type': 'shoutbox'
        }

        url = f"https://{service_key.lower()}.com/shoutbox.php"  # 根据实际情况调整
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            print(f"{service_key}喊话成功: {message}")
        else:
            print(f"{service_key}喊话失败: {response.status_code} - {message}")

    def send_messages(self, service_key):
        """根据配置发送消息"""
        service_config = self._services.get(service_key)
        if not service_config or not service_config['enabled']:
            print(f"{service_key}未启用")
            return

        for i, message in enumerate(service_config['messages']):
            self.send_message_to_service(message, service_key)
            if i < len(service_config['messages']) - 1:
                print(f"等待{self._global_interval}秒...")
                time.sleep(self._global_interval)

    def main(self):
        for service_key in self._services:
            self.send_messages(service_key)

if __name__ == "__main__":
    # 初始化插件并运行
    sender = MessageSender()
    sender.init_plugin({
        "enabled": True,
        "global_interval": 20,
        "services": {
            'QW': {'enabled': True, 'messages': ['蛙总，求上传', '蛙总，求下载']},
            'QCN': {'enabled': True, 'messages': ['青虫娘，求魔力', '青虫娘，求上传']}
        }
    })
    sender.main()
