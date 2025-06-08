"""
插件代理控制器
版本: 1.5.0
作者: EWEDL
功能:
- 控制其他插件是否使用 PROXY_HOST 代理
- 为指定插件提供代理功能
- 支持按插件单独设置代理状态
- 支持一键开关所有插件代理
- 区分系统插件和用户插件
- 提供单独的用户插件和系统插件选择下拉框
"""
import os
import sys
import importlib
import requests
from functools import wraps
from datetime import datetime
import json
import traceback
from pathlib import Path
import re

from app.core.config import settings
from app.core.plugin import PluginManager
from app.db.systemconfig_oper import SystemConfigOper
from app.schemas.types import SystemConfigKey
from app.plugins import _PluginBase
from typing import Any, List, Dict, Tuple, Optional, Set
from app.log import logger

# 定义常量
PROXY_MODULE_NAME = "proxycontroller"
PLUGIN_CONFIG_FILE = "plugin_proxy_config.json"


class proxycontroller(_PluginBase):
    # 插件名称
    plugin_name = "插件代理控制器"
    # 插件描述
    plugin_desc = "控制其他插件是否使用 PROXY_HOST 代理"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/EWEDLCM/MoviePilot-Plugins/main/icons/proxycontroller.png"
    # 插件版本
    plugin_version = "1.5.0"
    # 插件作者
    plugin_author = "EWEDL"
    # 作者主页
    author_url = "https://github.com/EWEDLCM"
    # 插件配置项ID前缀
    plugin_config_prefix = "proxycontroller_"
    # 加载顺序
    plugin_order = 0  # 设置为0，确保最先加载
    # 可使用的用户级别
    auth_level = 2

    # 私有属性
    _enabled = False
    _all_plugins_enabled = False
    _patched_plugins = set()
    _enabled_plugins = set()
    _enabled_user_plugins = []  # 用户插件列表
    _enabled_system_plugins = []  # 系统插件列表
    _original_requests = {}
    _proxy_host = None
    _installed_plugins = []  # 缓存已安装的插件列表
    _plugins_source = {}  # 记录每个插件的检测方法

    def init_plugin(self, config: dict = None):
        logger.info("============= 插件代理控制器初始化 =============")
        try:
            # 首先获取已安装的插件列表（提前获取，以便在配置中使用）
            self._installed_plugins, self._plugins_source = self.get_installed_plugins()
            logger.info(f"检测到已安装插件: {', '.join(self._installed_plugins) if self._installed_plugins else '无'}")
            
            # 获取用户插件和系统插件
            user_plugins, system_plugins = self.get_plugins_by_type()
            user_plugin_ids = [p.get('id') for p in user_plugins]
            system_plugin_ids = [p.get('id') for p in system_plugins]
            
            logger.info(f"用户插件: {', '.join(user_plugin_ids) if user_plugin_ids else '无'}")
            logger.info(f"系统插件: {', '.join(system_plugin_ids) if system_plugin_ids else '无'}")
            
            if config:
                logger.info(f"加载配置: {config}")
                self._enabled = config.get("enabled", False)
                self._all_plugins_enabled = config.get("all_plugins_enabled", False)
                
                # 获取用户和系统插件配置
                self._enabled_user_plugins = config.get("enabled_user_plugins", [])
                self._enabled_system_plugins = config.get("enabled_system_plugins", [])
                
                logger.info(f"配置中的用户插件: {self._enabled_user_plugins}")
                logger.info(f"配置中的系统插件: {self._enabled_system_plugins}")
                
                # 确保配置的插件ID都是有效的
                self._enabled_user_plugins = [p for p in self._enabled_user_plugins if p in user_plugin_ids]
                self._enabled_system_plugins = [p for p in self._enabled_system_plugins if p in system_plugin_ids]
                
                # 合并为总的启用插件列表
                self._enabled_plugins = set(self._enabled_user_plugins + self._enabled_system_plugins)
                
                logger.info(f"配置: enabled={self._enabled}, all_plugins_enabled={self._all_plugins_enabled}")
                logger.info(f"已启用代理的用户插件: {', '.join(self._enabled_user_plugins) if self._enabled_user_plugins else '无'}")
                logger.info(f"已启用代理的系统插件: {', '.join(self._enabled_system_plugins) if self._enabled_system_plugins else '无'}")
                logger.info(f"总启用插件数: {len(self._enabled_plugins)}")
            
            # 获取 PROXY_HOST
            self._proxy_host = self._get_proxy_host()
            if self._proxy_host:
                logger.info(f"检测到 PROXY_HOST: {self._proxy_host}")
            else:
                logger.warning("未检测到 PROXY_HOST 环境变量，插件代理功能可能无法正常工作")
            
            if self._enabled:
                # 应用猴子补丁
                self._apply_patches()
            else:
                # 恢复原始函数
                self._restore_patches()
        
        except Exception as e:
            logger.error(f"插件代理控制器初始化错误: {str(e)}", exc_info=True)
            logger.debug(f"错误详情: {traceback.format_exc()}")

    def _get_proxy_host(self):
        """获取 PROXY_HOST 环境变量"""
        proxy_host = os.environ.get('PROXY_HOST')
        if proxy_host:
            # 确保代理地址格式正确（添加 http:// 前缀如果没有的话）
            if not proxy_host.startswith('http://') and not proxy_host.startswith('https://'):
                proxy_host = f"http://{proxy_host}"
            return proxy_host
        
        # 尝试从 settings 中获取 PROXY_HOST
        try:
            if hasattr(settings, 'PROXY_HOST') and settings.PROXY_HOST:
                proxy_host = settings.PROXY_HOST
                if not proxy_host.startswith('http://') and not proxy_host.startswith('https://'):
                    proxy_host = f"http://{proxy_host}"
                return proxy_host
        except Exception as e:
            logger.debug(f"尝试从 settings 获取 PROXY_HOST 失败: {str(e)}")
        
        return None

    def _should_apply_proxy(self, module_name):
        """判断是否应该为指定模块应用代理"""
        # 如果插件未启用，不应用代理
        if not self._enabled:
            return False
        
        # 如果是本插件自身，不应用代理
        if module_name == PROXY_MODULE_NAME:
            return False
        
        # 如果启用了所有插件代理，或者该插件在启用列表中，则应用代理
        return self._all_plugins_enabled or module_name in self._enabled_plugins

    def _get_calling_plugin(self):
        """获取调用请求的插件名称"""
        try:
            # 遍历调用栈，查找插件模块
            import inspect
            frame = inspect.currentframe()
            frames = []
            
            # 收集调用栈信息
            while frame:
                frames.append(frame)
                frame = frame.f_back
            
            # 反向遍历调用栈，找到最早的插件调用者
            for frame in reversed(frames):
                if 'self' in frame.f_locals:
                    instance = frame.f_locals.get('self')
                    if hasattr(instance, '__module__'):
                        module_name = instance.__module__
                        # 如果是插件模块
                        if module_name.startswith('plugins.'):
                            # 提取插件名称
                            plugin_name = module_name.split('.')[1]
                            if plugin_name != PROXY_MODULE_NAME:
                                logger.debug(f"检测到调用插件: {plugin_name}")
                                return plugin_name
            
            # 如果上面的方法失败，尝试通过堆栈跟踪查找
            stack = traceback.extract_stack()
            for frame in stack:
                file_path = frame.filename
                if '/plugins/' in file_path:
                    parts = file_path.split('/plugins/')
                    if len(parts) > 1:
                        plugin_path = parts[1].split('/')[0]
                        if plugin_path and plugin_path != PROXY_MODULE_NAME:
                            logger.debug(f"通过路径检测到调用插件: {plugin_path}")
                            return plugin_path
        except Exception as e:
            logger.debug(f"获取调用插件失败: {str(e)}")
        return None

    def _proxy_decorator(self, original_func):
        """装饰器，为请求添加代理"""
        @wraps(original_func)
        def wrapper(*args, **kwargs):
            try:
                # 获取调用的插件名
                calling_plugin = self._get_calling_plugin()
                
                # 判断是否应该应用代理
                if calling_plugin and self._should_apply_proxy(calling_plugin) and self._proxy_host:
                    # 如果没有传入 proxies 参数，或者传入的是空字典，则添加代理
                    if 'proxies' not in kwargs or not kwargs['proxies']:
                        proxies = {
                            'http': self._proxy_host,
                            'https': self._proxy_host
                        }
                        kwargs['proxies'] = proxies
                        logger.info(f"为插件 {calling_plugin} 的请求添加代理: {self._proxy_host}")
            except Exception as e:
                logger.debug(f"应用代理装饰器失败: {str(e)}")
            
            # 调用原始函数
            return original_func(*args, **kwargs)
        
        return wrapper

    def _apply_patches(self):
        """应用猴子补丁，修改 requests 模块的行为"""
        try:
            # 保存原始函数引用
            if not self._original_requests:
                self._original_requests = {
                    'get': requests.get,
                    'post': requests.post,
                    'request': requests.request,
                    'Session.get': requests.Session.get,
                    'Session.post': requests.Session.post,
                    'Session.request': requests.Session.request
                }
            
            # 替换为代理版本
            requests.get = self._proxy_decorator(self._original_requests['get'])
            requests.post = self._proxy_decorator(self._original_requests['post'])
            requests.request = self._proxy_decorator(self._original_requests['request'])
            requests.Session.get = self._proxy_decorator(self._original_requests['Session.get'])
            requests.Session.post = self._proxy_decorator(self._original_requests['Session.post'])
            requests.Session.request = self._proxy_decorator(self._original_requests['Session.request'])
            
            logger.info("已应用请求代理补丁")
        except Exception as e:
            logger.error(f"应用猴子补丁失败: {str(e)}", exc_info=True)

    def _restore_patches(self):
        """恢复原始函数"""
        try:
            if self._original_requests:
                requests.get = self._original_requests['get']
                requests.post = self._original_requests['post']
                requests.request = self._original_requests['request']
                requests.Session.get = self._original_requests['Session.get']
                requests.Session.post = self._original_requests['Session.post']
                requests.Session.request = self._original_requests['Session.request']
                logger.info("已恢复原始请求函数")
        except Exception as e:
            logger.error(f"恢复原始函数失败: {str(e)}")

    def get_installed_plugins(self):
        """获取已安装的插件列表"""
        try:
            # 使用PluginManager获取插件信息
            plugin_manager = PluginManager()
            local_plugins = plugin_manager.get_local_plugins() or []
            
            # 获取所有插件ID，排除自身
            plugin_ids = []
            plugins_source = {}
            
            for plugin in local_plugins:
                plugin_id = getattr(plugin, 'id', None)
                if plugin_id and plugin_id != PROXY_MODULE_NAME:  # 排除自身
                    plugin_ids.append(plugin_id)
                    plugins_source[plugin_id] = "PluginManager"
            
            logger.info(f"通过PluginManager获取到 {len(plugin_ids)} 个插件")
            return plugin_ids, plugins_source
            
        except Exception as e:
            logger.error(f"获取已安装插件失败: {str(e)}", exc_info=True)
            return [], {}

    def get_state(self) -> bool:
        return self._enabled

    def get_service(self) -> List[Dict[str, Any]]:
        """注册插件服务"""
        if self._enabled:
            return [{
                'name': '插件代理控制服务',
                'type': '系统服务',
                'function': '_apply_patches',
                'icon': 'mdi:lan-connect'
            }]
        return []

    def get_user_plugins(self):
        """
        获取用户插件选项列表
        返回格式为[{"title": "插件名 v版本号", "value": "插件ID"}, ...]
        """
        user_plugins, _ = self.get_plugins_by_type()
        user_plugin_options = []
        
        for plugin in user_plugins:
            plugin_id = plugin.get('id')
            plugin_name = plugin.get('name', plugin_id)
            plugin_version = plugin.get('version', '未知')
            user_plugin_options.append({
                "title": f"{plugin_name} v{plugin_version}",
                "value": plugin_id
            })
            logger.debug(f"添加用户插件选项: {plugin_name} ({plugin_id}) v{plugin_version}")
        
        # 如果没有找到任何插件，添加提示信息
        if not user_plugin_options:
            user_plugin_options = [{
                "title": "未找到用户插件",
                "value": "",
                "disabled": True
            }]
        
        return user_plugin_options
    
    def get_system_plugins(self):
        """
        获取系统插件选项列表
        返回格式为[{"title": "插件名 v版本号", "value": "插件ID"}, ...]
        """
        _, system_plugins = self.get_plugins_by_type()
        system_plugin_options = []
        
        for plugin in system_plugins:
            plugin_id = plugin.get('id')
            plugin_name = plugin.get('name', plugin_id)
            plugin_version = plugin.get('version', '未知')
            system_plugin_options.append({
                "title": f"{plugin_name} v{plugin_version}",
                "value": plugin_id
            })
            logger.debug(f"添加系统插件选项: {plugin_name} ({plugin_id}) v{plugin_version}")
        
        # 如果没有找到任何插件，添加提示信息
        if not system_plugin_options:
            system_plugin_options = [{
                "title": "未找到系统插件",
                "value": "",
                "disabled": True
            }]
        
        return system_plugin_options
    
    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """获取表单配置"""
        try:
            # 获取插件列表
            user_plugins, system_plugins = self.get_plugins_by_type()
            # 记录插件数量
            user_plugin_count = len(user_plugins)
            system_plugin_count = len(system_plugins)
            total_plugin_count = user_plugin_count + system_plugin_count
            logger.info(f"检测到 {user_plugin_count} 个用户插件，{system_plugin_count} 个系统插件")

            # 构建用户插件选项
            user_plugin_options = []
            for plugin in user_plugins:
                plugin_id = plugin.get('id')
                plugin_name = plugin.get('name', plugin_id)
                plugin_version = plugin.get('version', '未知')
                if plugin_id:
                    user_plugin_options.append({
                        "title": f"{plugin_name} v{plugin_version}",
                        "value": plugin_id
                    })

            # 构建系统插件选项
            system_plugin_options = []
            for plugin in system_plugins:
                plugin_id = plugin.get('id')
                plugin_name = plugin.get('name', plugin_id)
                plugin_version = plugin.get('version', '未知')
                if plugin_id:
                    system_plugin_options.append({
                        "title": f"{plugin_name} v{plugin_version}",
                        "value": plugin_id
                    })

            # 如果没有找到任何插件，添加提示信息
            if not user_plugin_options:
                user_plugin_options = [{
                    "title": "暂无用户插件",
                    "value": "",
                    "disabled": True
                }]
            if not system_plugin_options:
                system_plugin_options = [{
                    "title": "暂无系统插件",
                    "value": "",
                    "disabled": True
                }]

            # 构建表单结构
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
                                                'label': '启用插件代理控制'
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
                                                'model': 'all_plugins_enabled',
                                                'label': '为所有插件启用代理'
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
                                            'component': 'VSelect',
                                            'props': {
                                                'multiple': True,
                                                'chips': True,
                                                'closable-chips': True,
                                                'model': 'enabled_user_plugins',
                                                'label': '选择用户插件',
                                                'items': user_plugin_options,
                                                ':disabled': 'formData.all_plugins_enabled',  # ✅ 修复点
                                                'persistent-hint': True,
                                                'hint': '选择需要启用代理的用户插件'
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
                                            'component': 'VSelect',
                                            'props': {
                                                'multiple': True,
                                                'chips': True,
                                                'closable-chips': True,
                                                'model': 'enabled_system_plugins',
                                                'label': '选择系统插件',
                                                'items': system_plugin_options,
                                                ':disabled': 'formData.all_plugins_enabled',  # ✅ 修复点
                                                'persistent-hint': True,
                                                'hint': '选择需要启用代理的系统插件'
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
                                            'component': 'VAlert',
                                            'props': {
                                                'type': 'info',
                                                'variant': 'tonal',
                                                'text': f'当前 PROXY_HOST: {self._proxy_host or "未设置"}, 共检测到 {total_plugin_count} 个插件 (用户插件: {user_plugin_count}, 系统插件: {system_plugin_count})'
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
                "all_plugins_enabled": self._all_plugins_enabled,
                "enabled_user_plugins": self._enabled_user_plugins or [],
                "enabled_system_plugins": self._enabled_system_plugins or []
            }

        except Exception as e:
            logger.error(f"获取表单配置失败: {str(e)}", exc_info=True)
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
                                        'cols': 12
                                    },
                                    'content': [
                                        {
                                            'component': 'VAlert',
                                            'props': {
                                                'type': 'error',
                                                'text': f'加载配置失败: {str(e)}'
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
                "all_plugins_enabled": False,
                "enabled_user_plugins": [],
                "enabled_system_plugins": []
            }

    def get_plugins_by_type(self) -> Tuple[List[Dict], List[Dict]]:
        """
        获取用户插件和系统插件
        返回两个列表：用户插件列表和系统插件列表
        """
        user_plugins = []
        system_plugins = []
        
        try:
            # 使用 PluginManager 获取插件信息
            plugin_manager = PluginManager()
            local_plugins = plugin_manager.get_local_plugins() or []
            
            # 获取已安装的用户插件列表
            installed_user_plugins = SystemConfigOper().get(SystemConfigKey.UserInstalledPlugins) or []
            
            for plugin in local_plugins:
                plugin_id = getattr(plugin, 'id', None)
                if not plugin_id:
                    continue
                
                # 排除插件自身
                if plugin_id == PROXY_MODULE_NAME:
                    continue
                
                plugin_info = {
                    'id': plugin_id,
                    'name': getattr(plugin, 'plugin_name', plugin_id),
                    'version': getattr(plugin, 'plugin_version', '未知'),
                    'author': getattr(plugin, 'plugin_author', '未知'),
                    'desc': getattr(plugin, 'plugin_desc', '')
                }
                
                # 判断是否为用户插件
                if plugin_id in installed_user_plugins:
                    user_plugins.append(plugin_info)
                else:
                    system_plugins.append(plugin_info)
            
            logger.info(f"通过 PluginManager 获取到 {len(user_plugins)} 个用户插件，{len(system_plugins)} 个系统插件")
                
        except Exception as e:
            logger.error(f"通过 PluginManager 获取插件失败: {str(e)}")
            # 如果获取失败，返回空列表
            return [], []
        
        # 确保返回的是非空列表，即使为空也要返回空列表而不是None
        return user_plugins or [], system_plugins or []
    
    def update_config(self, config: dict):
        """更新配置时合并用户插件和系统插件"""
        if config:
            logger.info(f"更新配置: {config}")
            self._enabled = config.get("enabled", False)
            self._all_plugins_enabled = config.get("all_plugins_enabled", False)
            
            # 获取并记录用户和系统插件
            self._enabled_user_plugins = config.get("enabled_user_plugins", [])
            self._enabled_system_plugins = config.get("enabled_system_plugins", [])
            
            logger.info(f"更新后的用户插件: {self._enabled_user_plugins}")
            logger.info(f"更新后的系统插件: {self._enabled_system_plugins}")
            
            # 合并为总的启用插件列表
            self._enabled_plugins = set(self._enabled_user_plugins + self._enabled_system_plugins)
            logger.info(f"更新后的总启用插件数: {len(self._enabled_plugins)}")
            
            # 如果启用了代理控制，应用猴子补丁
            if self._enabled:
                self._apply_patches()
            else:
                self._restore_patches()

    def get_page(self) -> List[dict]:
        """获取插件页面"""
        # 使用缓存的插件列表
        installed_plugins = self._installed_plugins
        
        # 构建数据表格的列配置
        columns = [
            {'field': 'plugin', 'title': '插件名称', 'width': '200px'},
            {'field': 'detection_method', 'title': '检测方法', 'width': '150px'},
            {'field': 'proxy_status', 'title': '代理状态', 'width': '120px'}
        ]
        
        # 构建表格的数据
        items = []
        for plugin in installed_plugins:
            proxy_status = "已启用" if (self._all_plugins_enabled or plugin in self._enabled_plugins) and self._enabled else "未启用"
            detection_method = self._plugins_source.get(plugin, "未知")
            items.append({
                "plugin": plugin,
                "detection_method": detection_method,
                "proxy_status": proxy_status
            })
        
        # 构建表格的选项配置
        options = {
            'headers': columns,
            'itemsPerPage': 20,  # 增加默认显示数量
            'itemsPerPageOptions': [10, 20, 50, 100],  # 增加更多选项
            'sortBy': [{'key': 'plugin', 'order': 'asc'}],
            'separator': 'horizontal',
            'class': 'elevation-0',
            'footerProps': {'showFirstLastPage': True, 'itemsPerPageOptions': [10, 20, 50, 100]}
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
                                    'text': '插件代理状态',
                                    'subtext': f'共 {len(installed_plugins)} 个插件'
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
                                                                'text': '代理设置信息:',
                                                                'props': {
                                                                    'class': 'text-subtitle-1 font-weight-bold'
                                                                }
                                                            },
                                                            {
                                                                'component': 'div',
                                                                'text': f"PROXY_HOST: {self._proxy_host or '未设置'}",
                                                                'props': {
                                                                    'class': 'text-body-1 mt-2'
                                                                }
                                                            },
                                                            {
                                                                'component': 'div',
                                                                'text': f"插件代理控制: {'已启用' if self._enabled else '未启用'}",
                                                                'props': {
                                                                    'class': 'text-body-1'
                                                                }
                                                            },
                                                            {
                                                                'component': 'div',
                                                                'text': f"全局代理模式: {'已启用' if self._all_plugins_enabled else '未启用'}",
                                                                'props': {
                                                                    'class': 'text-body-1'
                                                                }
                                                            },
                                                            {
                                                                'component': 'div',
                                                                'text': f"已启用代理的插件数: {len(self._enabled_plugins) if not self._all_plugins_enabled else len(installed_plugins)}",
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
                                'component': 'VTextField',
                                'props': {
                                    'label': '搜索插件',
                                    'prepend-inner-icon': 'mdi-magnify',
                                    'hide-details': True,
                                    'variant': 'outlined',
                                    'density': 'compact',
                                    'class': 'mb-4',
                                    'v-model': 'searchQuery'
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
                                    'items': items,
                                    'itemsPerPage': options['itemsPerPage'], 
                                    'footer-props': options['footerProps'],
                                    'class': 'elevation-1',
                                    'search': '{{searchQuery}}'
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
                                    'class': 'mt-4'
                                },
                                'content': [
                                    {
                                        'component': 'VCardText',
                                        'content': [
                                            {
                                                'component': 'div',
                                                'text': '使用说明:',
                                                'props': {
                                                    'class': 'text-subtitle-1 font-weight-bold'
                                                }
                                            },
                                            {
                                                'component': 'div',
                                                'text': '1. 启用插件代理控制后，可以选择为所有插件启用代理，或者只为特定插件启用代理',
                                                'props': {
                                                    'class': 'text-body-1 mt-2'
                                                }
                                            },
                                            {
                                                'component': 'div',
                                                'text': '2. 插件代理控制只对使用Python requests库发送网络请求的插件有效',
                                                'props': {
                                                    'class': 'text-body-1'
                                                }
                                            },
                                            {
                                                'component': 'div',
                                                'text': '3. 如果插件自身已经设置了代理，则不会被覆盖',
                                                'props': {
                                                    'class': 'text-body-1'
                                                }
                                            },
                                            {
                                                'component': 'div',
                                                'text': '4. 检测方法显示了每个插件是通过哪种方式被发现的',
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

    def stop_service(self):
        """停止插件服务"""
        try:
            # 恢复原始函数
            self._restore_patches()
            logger.info("插件代理控制服务已停止")
            return True
        except Exception as e:
            logger.error(f"停止插件代理控制服务失败: {str(e)}")
            return False

    def get_command(self) -> List[Dict[str, Any]]:
        """注册命令"""
        return [{
            "cmd": "/proxycontrol",
            "event": self.handle_command,
            "desc": "控制插件代理设置"
        }]
    
    def handle_command(self, cmd: str, data: Any = None) -> Dict[str, Any]:
        """处理命令"""
        # 简单返回当前状态
        return {
            "success": True,
            "data": {
                "enabled": self._enabled,
                "all_plugins_enabled": self._all_plugins_enabled,
                "enabled_plugins": list(self._enabled_plugins),
                "proxy_host": self._proxy_host,
                "installed_plugins": self._installed_plugins,
                "plugins_source": self._plugins_source
            }
        }

    def get_api(self) -> List[Dict[str, Any]]:
        """注册API"""
        return [] 
