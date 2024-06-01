import threading
from dataclasses import asdict, fields
from typing import Any, List, Dict, Tuple

from app.helper.sites import SitesHelper
from apscheduler.triggers.cron import CronTrigger
from ruamel.yaml import YAMLError

from app.core.plugin import PluginManager
from app.log import logger
from app.plugins import _PluginBase
from app.plugins.trafficassistant.trafficconfig import TrafficConfig

lock = threading.Lock()


class TrafficAssistant(_PluginBase):
    # 插件名称
    plugin_name = "流量管理"
    # 插件描述
    plugin_desc = "自动管理流量，保障站点分享率。"
    # 插件图标
    plugin_icon = "https://github.com/InfinityPacer/MoviePilot-Plugins/raw/main/icons/trafficassistant.png"
    # 插件版本
    plugin_version = "1.0"
    # 插件作者
    plugin_author = "InfinityPacer"
    # 作者主页
    author_url = "https://github.com/InfinityPacer"
    # 插件配置项ID前缀
    plugin_config_prefix = "trafficassistant_"
    # 加载顺序
    plugin_order = 19
    # 可使用的用户级别
    auth_level = 1

    # region 私有属性

    # 插件Manager
    pluginmanager = None
    siteshelper = None

    # 流量管理配置
    _traffic_config = TrafficConfig()

    # 定时器
    _scheduler = None
    # 退出事件
    _event = threading.Event()

    # endregion

    def init_plugin(self, config: dict = None):
        self.pluginmanager = PluginManager()
        self.siteshelper = SitesHelper()

        if not config:
            return

        result, reason = self.__validate_and_fix_config(config=config)

        if not result and not self._traffic_config:
            self.__update_config_if_error(config=config, error=reason)
            return

        self.__update_config()

    def get_state(self) -> bool:
        return self._traffic_config and self._traffic_config.enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        """
        定义远程控制命令
        :return: 命令关键字、事件、描述、附带数据
        """
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        pass

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
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件',
                                            'hint': '开启后插件将处于激活状态',
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
                                            'label': '发送通知',
                                            'hint': '是否在特定事件发生时发送通知',
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
                                            'label': '立即执行一次',
                                            'hint': '插件将立即执行一次',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 8
                                },
                                'content': [
                                    {
                                        'component': 'VSelect',
                                        'props': {
                                            'multiple': True,
                                            'chips': True,
                                            'closable-chips': True,
                                            'clearable': True,
                                            'model': 'sites',
                                            'label': '站点列表',
                                            'hint': '选择参与配置的站点',
                                            'persistent-hint': True,
                                            'items': self.__get_site_options()
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4,
                                },
                                'content': [
                                    {
                                        'component': 'VSelect',
                                        'props': {
                                            'model': 'brush_plugin',
                                            'label': '站点刷流插件',
                                            'hint': '选择参与配置的刷流插件',
                                            'persistent-hint': True,
                                            'items': self.__get_plugin_options()
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
                                            'label': '运行周期',
                                            'placeholder': '5位cron表达式',
                                            'hint': '设置任务的执行周期，如每天8点执行一次',
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
                                            'model': 'ratio_lower_limit',
                                            'label': '分享率下限',
                                            'type': 'number',
                                            "min": "0",
                                            'hint': '设置最低分享率阈值',
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
                                            'model': 'ratio_upper_limit',
                                            'label': '分享率上限',
                                            'type': 'number',
                                            "min": "0",
                                            'hint': '设置最高分享率阈值',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
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
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'add_to_subscription_if_above',
                                            'label': '添加订阅站点',
                                            'hint': '分享率高于上限时自动添加到订阅站点',
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
                                            'model': 'add_to_search_if_above',
                                            'label': '添加搜索站点',
                                            'hint': '分享率高于上限时自动添加到搜索站点',
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
                                            'model': 'disable_auto_brush_if_above',
                                            'label': '停止刷流',
                                            'hint': '分享率超过上限时自动停止刷流功能',
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
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'remove_from_subscription_if_below',
                                            'label': '移除订阅站点',
                                            'hint': '分享率低于下限时自动从订阅中移除站点',
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
                                            'model': 'remove_from_search_if_below',
                                            'label': '移除搜索站点',
                                            'hint': '分享率低于下限时自动从搜索中移除站点',
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
                                            'model': 'enable_auto_brush_if_below',
                                            'label': '开启刷流',
                                            'hint': '分享率超过上限时自动开启刷流功能',
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
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'send_alert_if_below',
                                            'label': '发送预警',
                                            'hint': '分享率低于下限时发送预警通知',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                },
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'error',
                                            'variant': 'tonal',
                                            'text': '警告：本插件仍在完善阶段，可能会导致流量管理异常，分享率降低等，严重甚至导致站点封号，请慎重使用'
                                        }
                                    }
                                ]
                            },
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                },
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'error',
                                            'variant': 'tonal',
                                            'text': '警告：本插件依赖站点刷流插件，请提前安装对应插件中进行相关配置，否则可能导致开启站点刷流后，分享率降低或命中H&R种子，严重甚至导致站点封号，请慎重使用'
                                        }
                                    }
                                ]
                            },
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                },
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'error',
                                            'variant': 'tonal',
                                            'text': '注意：本插件依赖站点数据统计插件，请提前安装对应插件中进行相关配置，否则可能导致无法获取到分享率等信息，从而影响后续流量管理'
                                        }
                                    }
                                ]
                            },
                        ]
                    }
                ]
            }
        ], {
            "enabled": False,
            "onlyonce": False,
            "notify": True
        }

    def get_page(self) -> List[dict]:
        pass

    def get_service(self) -> List[Dict[str, Any]]:
        """
        注册插件公共服务
        [{
            "id": "服务ID",
            "name": "服务名称",
            "trigger": "触发器：cron/interval/date/CronTrigger.from_crontab()",
            "func": self.xxx,
            "kwargs": {} # 定时器参数
        }]
        """

        if not self._traffic_config:
            return []

        if self._traffic_config.enabled and self._traffic_config.cron:
            return [{
                "id": "TrafficAssistant",
                "name": "流量管理服务",
                "trigger": CronTrigger.from_crontab(self._traffic_config.cron),
                "func": self.traffic,
                "kwargs": {}
            }]

    def stop_service(self):
        """
        退出插件
        """
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._event.set()
                    self._scheduler.shutdown()
                    self._event.clear()
                self._scheduler = None
        except Exception as e:
            print(str(e))

    def traffic(self):
        """流量管理"""
        pass

    def __validate_config(self, traffic_config: TrafficConfig) -> (bool, str):
        """
        验证配置是否有效
        """
        if not traffic_config.enabled:
            return True, "插件未启用，无需进行验证"

        # 检查必需的插件是否已启用
        result, message = self.__check_required_plugins_running(traffic_config=traffic_config)
        if not result:
            return False, message

        # 检查站点列表是否为空
        if not traffic_config.sites:
            return False, "站点列表不能为空"

        # 检查是否配置了站点刷流插件
        if not traffic_config.brush_plugin:
            return False, "站点刷流插件不能为空"

        # 检查分享率的设置是否有效
        if traffic_config.ratio_lower_limit <= 0 or traffic_config.ratio_upper_limit <= 0:
            return False, "分享率必须大于0"

        # 检查分享率的上下限是否正确
        if traffic_config.ratio_upper_limit < traffic_config.ratio_lower_limit:
            return False, "分享率上限必须大于等于下限"

        return True, "所有配置项都有效"

    def __validate_and_fix_config(self, config: dict = None) -> [bool, str]:
        """
        检查并修正配置值
        """
        if not config:
            return False, ""

        try:
            # 使用字典推导来提取所有字段，并用config中的值覆盖默认值
            traffic_config = TrafficConfig(
                **{field.name: config.get(field.name, getattr(TrafficConfig, field.name, None))
                   for field in fields(TrafficConfig)})

            result, reason = self.__validate_config(traffic_config=traffic_config)
            if result:
                # 过滤掉已删除的站点并保存
                if traffic_config.sites:
                    site_id_to_public_status = {site.get("id"): site.get("public") for site in
                                                self.siteshelper.get_indexers()}
                    traffic_config.sites = [
                        site_id for site_id in traffic_config.sites
                        if site_id in site_id_to_public_status and not site_id_to_public_status[site_id]
                    ]
                self._traffic_config = traffic_config
                return True, ""
            else:
                self._traffic_config = None
                return result, reason
        except YAMLError as e:
            self._traffic_config = None
            logger.error(e)
            return False, str(e)
        except Exception as e:
            self._traffic_config = None
            logger.error(e)
            return False, str(e)

    def __update_config_if_error(self, config: dict = None, error: str = None):
        """异常时停用插件并保存配置"""
        if config:
            if config.get("enabled", False):
                # config["enabled"] = False
                self.__log_and_notify_error(
                    f"配置异常，已停用流量管理，原因：{error}" if error else "配置异常，已停用流量管理，请检查")
            self.update_config(config)

    def __update_config(self):
        """保存配置"""
        config_mapping = asdict(self._traffic_config)
        self.update_config(config_mapping)

    def __log_and_notify_error(self, message):
        """
        记录错误日志并发送系统通知
        """
        logger.error(message)
        self.systemmessage.put(message, title="流量管理")

    def __get_site_options(self):
        """获取当前可选的站点"""
        site_options = [{"title": site.get("name"), "value": site.get("id")}
                        for site in self.siteshelper.get_indexers()]
        return site_options

    def __get_plugin_options(self) -> List[dict]:
        """获取插件选项列表"""
        # 获取运行的插件选项
        running_plugins = self.pluginmanager.get_running_plugin_ids()

        # 需要检查的插件名称
        filter_plugins = {"BrushFlow", "BrushFlowLowFreq"}

        # 获取本地插件列表
        local_plugins = self.pluginmanager.get_local_plugins()

        # 初始化插件选项列表
        plugin_options = []

        # 从本地插件中筛选出符合条件的插件
        for local_plugin in local_plugins:
            if local_plugin.id in running_plugins and local_plugin.id in filter_plugins:
                plugin_options.append({
                    "title": f"{local_plugin.plugin_name} v{local_plugin.plugin_version}",
                    "value": local_plugin.id,
                    "name": local_plugin.plugin_name
                })

        # 重新编号，保证显示为 1. 2. 等
        for index, option in enumerate(plugin_options, start=1):
            option["title"] = f"{index}. {option['title']}"

        return plugin_options

    def __check_required_plugins_running(self, traffic_config: TrafficConfig) -> (bool, str):
        """
        检查所有必需的依赖插件是否已启用
        """
        if not traffic_config:
            return False, "配置信息不完整，无法进行插件状态检查。"

        # 定义需要检查的插件集合及其友好名称
        plugin_names = {"SiteStatistic": "站点数据统计"}
        if traffic_config.brush_plugin:
            plugin_names[traffic_config.brush_plugin] = "站点刷流"

        # 获取本地插件列表
        local_plugins = self.pluginmanager.get_local_plugins()

        # 检查必需的插件是否都已启用
        missing_plugins = []
        for plugin_id, friendly_name in plugin_names.items():
            if not any(plugin.state and plugin.id == plugin_id for plugin in local_plugins):
                missing_plugins.append(friendly_name)

        if missing_plugins:
            missing_plugins_str = ", ".join(missing_plugins)
            return False, f"存在依赖插件未启用: {missing_plugins_str}"

        return True, "所有必需插件均已启用"
