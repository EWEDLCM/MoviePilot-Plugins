"""
邮件集插件
版本: 1.0.0
作者: EWEDL
功能:
- 使用IMAP协议实时监控邮箱
- 验证码AI识别
- 关键词邮件过滤
- 支持代理环境
- 多邮箱支持
- 消息推送
"""
import os
import time
import imaplib
import email
import threading
import base64
from datetime import datetime
from typing import Any, List, Dict, Tuple, Optional
from email.header import decode_header
import re
from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings
from app.plugins import _PluginBase
from app.log import logger
from app.schemas import NotificationType

# 导入AI处理模块
from .ai_handler import AIHandler


class yjj(_PluginBase):
    # 插件名称
    plugin_name = "邮件集"
    # 插件描述
    plugin_desc = "实时监控邮箱，支持验证码AI识别和关键词过滤，自动推送重要邮件"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/EWEDLCM/MoviePilot-Plugins/main/icons/yjj.png"
    # 插件版本
    plugin_version = "1.0.0"
    # 插件作者
    plugin_author = "EWEDL"
    # 作者主页
    author_url = "https://github.com/EWEDLCM"
    # 插件配置项ID前缀
    plugin_config_prefix = "yjj_"
    # 加载顺序
    plugin_order = 1
    # 可使用的用户级别
    auth_level = 2

    # 私有属性
    _enabled = False
    _use_proxy = False
    _email_configs = ""
    _msgtype = None
    _ai_enabled = False
    _ai_url = ""
    _ai_key = ""
    _ai_model = ""
    _keywords = ""
    
    # 运行时属性
    _monitor_threads = []
    _running = False
    _imap_connections = {}

    # 验证码关键词
    _verification_keywords = ["验证码", "验证", "code", "verification", "verify", "otp", "动态密码"]

    # 异步执行器
    _executor = None

    # 已处理邮件ID记录（防止重复处理）
    _processed_emails = {}

    def init_plugin(self, config: dict = None):
        """初始化插件"""
        # 停止现有监控
        self.stop_monitoring()

        logger.info("=" * 60)
        logger.info("邮件集插件 (yjj) v1.0.0 - 初始化开始")
        logger.info("=" * 60)

        try:
            if config:
                self._enabled = config.get("enabled", False)
                self._use_proxy = config.get("use_proxy", False)
                self._email_configs = config.get("email_configs", "")
                self._msgtype = config.get("msgtype")
                self._ai_enabled = config.get("ai_enabled", False)
                self._ai_url = config.get("ai_url", "")
                self._ai_key = config.get("ai_key", "")
                self._ai_model = config.get("ai_model", "")
                self._keywords = config.get("keywords", "")

                logger.info(f"[配置] 插件启用状态: {self._enabled}")
                logger.info(f"[配置] 代理使用状态: {self._use_proxy}")
                logger.info(f"[配置] AI识别状态: {self._ai_enabled}")
                logger.info(f"[配置] 通知渠道: {self._msgtype or '默认'}")

                # 解析邮箱配置
                email_configs = self._parse_email_configs()
                logger.info(f"[邮箱] 解析到 {len(email_configs)} 个邮箱配置")

                # 验证邮箱配置
                for i, config in enumerate(email_configs, 1):
                    if config.get('imap_server'):
                        logger.info(f"[邮箱{i}] {config['email']} -> {config['imap_server']}")
                    else:
                        logger.warning(f"[邮箱{i}] {config['email']} -> 无法识别IMAP服务器")

                # 解析关键词
                keywords = self._parse_keywords()
                if keywords:
                    logger.info(f"[关键词] 配置了 {len(keywords)} 个关键词: {', '.join(keywords)}")
                else:
                    logger.info("[关键词] 未配置关键词过滤")

                # 验证AI配置
                if self._ai_enabled:
                    logger.info("[AI] 验证码AI识别已启用")
                    if self._ai_url:
                        logger.info(f"[AI] 接口地址: {self._ai_url}")
                    else:
                        logger.warning("[AI] 未配置AI接口地址")

                    if self._ai_key:
                        logger.info(f"[AI] API密钥: {'*' * (len(self._ai_key) - 8) + self._ai_key[-8:] if len(self._ai_key) > 8 else '***'}")
                    else:
                        logger.warning("[AI] 未配置API密钥")

                    if self._ai_model:
                        logger.info(f"[AI] 模型名称: {self._ai_model}")
                    else:
                        logger.info("[AI] 使用默认模型: gpt-3.5-turbo")

                    if not self._ai_url or not self._ai_key:
                        logger.warning("[AI] 配置不完整，验证码识别可能无法正常工作")
                else:
                    logger.info("[AI] 验证码AI识别已禁用")

                # 代理配置检查
                if self._use_proxy:
                    proxy_host = self.get_proxy_host()
                    if proxy_host:
                        logger.info(f"[代理] 已启用代理: {proxy_host}")
                    else:
                        logger.warning("[代理] 已启用代理但未找到PROXY_HOST环境变量")
                else:
                    logger.info("[代理] 未启用代理")

            # 如果启用，开始监控
            if self._enabled:
                if email_configs:
                    logger.info("[启动] 开始启动邮件监控服务...")
                    self.start_monitoring()
                    logger.info("[启动] 邮件监控服务启动完成")
                else:
                    logger.warning("[启动] 未配置任何邮箱，插件已启用但不会进行监控")
            else:
                logger.info("[启动] 插件未启用，跳过监控启动")

            logger.info("=" * 60)
            logger.info("邮件集插件初始化完成")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"[错误] 邮件集插件初始化失败: {str(e)}", exc_info=True)

    def get_proxy_host(self):
        """获取 PROXY_HOST 环境变量"""
        proxy_host = os.environ.get('PROXY_HOST')
        if proxy_host:
            # 确保代理地址格式正确
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

    def _parse_email_configs(self) -> List[Dict[str, str]]:
        """解析邮箱配置"""
        configs = []
        if not self._email_configs:
            return configs
            
        lines = self._email_configs.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            parts = line.split('|')
            if len(parts) >= 2:
                email_addr = parts[0].strip()
                password = parts[1].strip()
                
                if email_addr and password:
                    # 根据邮箱地址推断IMAP服务器
                    imap_server = self._get_imap_server(email_addr)
                    if imap_server:
                        configs.append({
                            'email': email_addr,
                            'password': password,
                            'imap_server': imap_server
                        })
                    else:
                        logger.warning(f"无法识别邮箱服务器: {email_addr}")
                else:
                    logger.warning(f"邮箱配置格式错误，已跳过: {line}")
        
        return configs

    def _get_imap_server(self, email_addr: str) -> str:
        """根据邮箱地址获取IMAP服务器"""
        domain = email_addr.split('@')[1].lower()
        
        imap_servers = {
            'qq.com': 'imap.qq.com',
            '163.com': 'imap.163.com',
            '126.com': 'imap.126.com',
            'gmail.com': 'imap.gmail.com',
            'outlook.com': 'outlook.office365.com',
            'hotmail.com': 'outlook.office365.com',
            'yahoo.com': 'imap.mail.yahoo.com',
            'sina.com': 'imap.sina.com',
            'sohu.com': 'imap.sohu.com'
        }
        
        return imap_servers.get(domain)

    def _parse_keywords(self) -> List[str]:
        """解析关键词"""
        if not self._keywords:
            return []
        
        keywords = [kw.strip() for kw in self._keywords.split('|') if kw.strip()]
        return keywords

    def start_monitoring(self):
        """开始邮件监控"""
        if self._running:
            logger.warning("[监控] 邮件监控已在运行中，跳过启动")
            return

        logger.info("[监控] 正在启动邮件监控服务...")
        self._running = True

        email_configs = self._parse_email_configs()
        if not email_configs:
            logger.error("[监控] 没有配置任何邮箱，监控启动失败")
            self._running = False
            return

        logger.info(f"[监控] 准备为 {len(email_configs)} 个邮箱创建监控线程")

        # 为每个邮箱创建监控线程
        for i, config in enumerate(email_configs, 1):
            try:
                thread = threading.Thread(
                    target=self._monitor_email,
                    args=(config,),
                    daemon=True,
                    name=f"EmailMonitor-{config['email']}"
                )
                thread.start()
                self._monitor_threads.append(thread)
                logger.info(f"[监控] 线程 {i}/{len(email_configs)} 启动成功: {config['email']}")
            except Exception as e:
                logger.error(f"[监控] 线程 {i}/{len(email_configs)} 启动失败: {config['email']}, 错误: {str(e)}")

        logger.info(f"[监控] 邮件监控服务启动完成，共 {len(self._monitor_threads)} 个活跃线程")

    def stop_monitoring(self):
        """停止邮件监控"""
        if not self._running:
            logger.info("[监控] 邮件监控未运行，跳过停止操作")
            return

        logger.info("[监控] 正在停止邮件监控服务...")
        self._running = False

        # 等待一小段时间让线程检测到停止信号
        time.sleep(1)

        # 关闭IMAP连接
        connection_count = len(self._imap_connections)
        if connection_count > 0:
            logger.info(f"[监控] 正在关闭 {connection_count} 个IMAP连接...")

            for email_addr, connection in list(self._imap_connections.items()):
                try:
                    if connection:
                        connection.close()
                        connection.logout()
                        logger.info(f"[监控] IMAP连接已关闭: {email_addr}")
                except Exception as e:
                    logger.error(f"[监控] 关闭IMAP连接失败 {email_addr}: {str(e)}")

        self._imap_connections.clear()

        # 等待监控线程结束
        thread_count = len(self._monitor_threads)
        if thread_count > 0:
            logger.info(f"[监控] 等待 {thread_count} 个监控线程结束...")
            for thread in self._monitor_threads:
                if thread.is_alive():
                    thread.join(timeout=3)  # 最多等待3秒
                    if thread.is_alive():
                        logger.warning(f"[监控] 线程 {thread.name} 未能正常结束")

        self._monitor_threads.clear()

        # 关闭线程池
        if self._executor:
            logger.info("[监控] 正在关闭AI线程池...")
            try:
                self._executor.shutdown(wait=False)
                self._executor = None
                logger.info("[监控] AI线程池已关闭")
            except Exception as e:
                logger.error(f"[监控] 关闭AI线程池失败: {str(e)}")

        # 清理已处理邮件记录
        self._processed_emails.clear()

        logger.info(f"[监控] 邮件监控服务已停止，清理了 {thread_count} 个线程")

    def _monitor_email(self, config: Dict[str, str]):
        """监控单个邮箱"""
        email_addr = config['email']
        password = config['password']
        imap_server = config['imap_server']

        logger.info(f"[{email_addr}] 邮箱监控线程启动")
        logger.info(f"[{email_addr}] IMAP服务器: {imap_server}")

        retry_count = 0
        max_retries = 10

        while self._running and retry_count < max_retries:
            mail = None
            try:
                logger.info(f"[{email_addr}] 正在建立IMAP连接...")

                # 建立IMAP连接
                mail = imaplib.IMAP4_SSL(imap_server, 993)
                logger.debug(f"[{email_addr}] SSL连接已建立")

                mail.login(email_addr, password)
                logger.info(f"[{email_addr}] 登录认证成功")

                mail.select('INBOX')
                logger.debug(f"[{email_addr}] 已选择收件箱")

                self._imap_connections[email_addr] = mail
                retry_count = 0  # 重置重试计数

                # 获取当前最新邮件数量作为基准
                _, messages = mail.search(None, 'ALL')
                if messages[0]:
                    message_ids = messages[0].split()
                    last_count = len(message_ids)
                else:
                    last_count = 0

                logger.info(f"[{email_addr}] 连接成功，当前邮件数量: {last_count}")

                # 开始监控新邮件
                check_count = 0
                last_noop_time = time.time()

                while self._running:
                    try:
                        check_count += 1
                        current_time = time.time()

                        # 检查邮件数量变化
                        _, current_messages = mail.search(None, 'ALL')
                        if current_messages[0]:
                            current_ids = current_messages[0].split()
                            current_count = len(current_ids)

                            # 如果有新邮件
                            if current_count > last_count:
                                new_count = current_count - last_count
                                logger.info(f"[{email_addr}] 🆕 检测到 {new_count} 封新邮件 (总数: {last_count} -> {current_count})")

                                # 处理新邮件（从last_count开始）
                                for i in range(last_count, current_count):
                                    if i < len(current_ids):
                                        msg_id = current_ids[i]
                                        logger.info(f"[{email_addr}] 📧 处理新邮件 {i+1}/{current_count}")
                                        self._process_new_email(mail, msg_id, email_addr)

                                last_count = current_count
                                logger.info(f"[{email_addr}] ✅ 新邮件处理完成")

                        # 每2分钟发送一次NOOP保持连接（静默执行，不记录日志）
                        if current_time - last_noop_time > 120:  # 2分钟
                            mail.noop()
                            last_noop_time = current_time

                        # 等待一段时间再检查（已调整为20秒）
                        time.sleep(20)

                    except Exception as e:
                        logger.error(f"[{email_addr}] ❌ 监控过程中出错: {str(e)}")
                        break

            except imaplib.IMAP4.error as e:
                retry_count += 1
                logger.error(f"[{email_addr}] ❌ IMAP协议错误 (重试 {retry_count}/{max_retries}): {str(e)}")
            except Exception as e:
                retry_count += 1
                logger.error(f"[{email_addr}] ❌ 连接失败 (重试 {retry_count}/{max_retries}): {str(e)}")

            finally:
                # 清理连接
                if mail:
                    try:
                        mail.close()
                        mail.logout()
                        logger.debug(f"[{email_addr}] IMAP连接已清理")
                    except:
                        pass
                    if email_addr in self._imap_connections:
                        del self._imap_connections[email_addr]

            # 如果连接断开，等待后重试
            if self._running and retry_count < max_retries:
                wait_time = min(30 * retry_count, 300)  # 递增等待时间，最大5分钟
                logger.warning(f"[{email_addr}] 🔄 连接断开，{wait_time}秒后进行第 {retry_count+1} 次重试...")
                time.sleep(wait_time)

        if retry_count >= max_retries:
            logger.error(f"[{email_addr}] ❌ 达到最大重试次数 ({max_retries})，停止监控")
        else:
            logger.info(f"[{email_addr}] 📴 邮箱监控线程正常退出")

    def get_state(self) -> bool:
        return self._enabled and self._running

    def _process_new_email(self, mail, msg_id, email_addr):
        """处理新邮件"""
        try:
            msg_id_str = msg_id.decode() if isinstance(msg_id, bytes) else str(msg_id)

            # 检查是否已处理过此邮件（防止重复处理）
            email_key = f"{email_addr}:{msg_id_str}"
            if email_key in self._processed_emails:
                logger.debug(f"[{email_addr}] 📧 邮件 ID: {msg_id_str} 已处理过，跳过")
                return

            # 标记为已处理
            self._processed_emails[email_key] = time.time()

            # 清理过期的处理记录（保留最近1小时的记录）
            current_time = time.time()
            expired_keys = [k for k, v in self._processed_emails.items() if current_time - v > 3600]
            for k in expired_keys:
                del self._processed_emails[k]

            logger.info(f"[{email_addr}] 📧 开始处理邮件 ID: {msg_id_str}")

            # 获取邮件
            _, msg_data = mail.fetch(msg_id, '(RFC822)')
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)

            # 解析邮件基本信息
            subject = self._decode_header(email_message.get('Subject', ''))
            sender = self._decode_header(email_message.get('From', ''))
            date = self._decode_header(email_message.get('Date', ''))

            logger.info(f"[{email_addr}] 📬 邮件信息:")
            logger.info(f"[{email_addr}]   标题: {subject}")
            logger.info(f"[{email_addr}]   发件人: {sender}")
            logger.info(f"[{email_addr}]   日期: {date}")

            # 提取邮件内容和附件
            logger.debug(f"[{email_addr}] 🔍 正在提取邮件内容...")
            text_content, html_content, attachments = self._extract_email_content(email_message)

            # 记录内容统计
            text_len = len(text_content) if text_content else 0
            html_len = len(html_content) if html_content else 0
            attachment_count = len(attachments)

            logger.info(f"[{email_addr}] 📄 内容统计: 文本({text_len}字符), HTML({html_len}字符), 附件({attachment_count}个)")

            if attachments:
                for i, att in enumerate(attachments, 1):
                    logger.info(f"[{email_addr}]   附件{i}: {att['filename']} ({att['content_type']})")

            # 组合邮件内容
            email_content = text_content or html_content or ""
            full_content = f"{subject}\n{email_content}"

            # 检查是否为验证码邮件
            logger.debug(f"[{email_addr}] 🔍 检查是否为验证码邮件...")
            is_verification = self._is_verification_email(full_content)

            if is_verification:
                logger.info(f"[{email_addr}] 🔐 识别为验证码邮件")
                if self._ai_enabled:
                    logger.info(f"[{email_addr}] 🤖 启用AI识别，异步调用AI处理")
                    # 使用线程池异步处理AI调用，避免阻塞邮件监控
                    self._handle_verification_email_async(subject, email_content, attachments, sender, email_addr)
                else:
                    logger.info(f"[{email_addr}] 🤖 AI识别未启用，直接发送邮件")
                    # 统一格式：验证码邮件（未使用AI）
                    formatted_content = self._format_email_notification(
                        "", sender, subject, email_content
                    )
                    self._send_notification("邮件通知", formatted_content, attachments, email_addr)
            else:
                logger.debug(f"[{email_addr}] 🔍 检查关键词匹配...")
                keywords = self._parse_keywords()
                if keywords:
                    matched_keywords = [kw for kw in keywords if self._check_keywords(full_content, [kw])]
                    if matched_keywords:
                        logger.info(f"[{email_addr}] 🎯 关键词匹配成功: {', '.join(matched_keywords)}")
                        self._send_keyword_email(subject, email_content, attachments, sender, email_addr)
                    else:
                        logger.debug(f"[{email_addr}] 🎯 关键词不匹配，跳过邮件")
                else:
                    logger.debug(f"[{email_addr}] 🎯 未配置关键词，跳过邮件")

            logger.info(f"[{email_addr}] ✅ 邮件处理完成")

        except Exception as e:
            logger.error(f"[{email_addr}] ❌ 处理邮件失败: {str(e)}", exc_info=True)

    def _decode_header(self, header_value):
        """解码邮件头"""
        if not header_value:
            return ""

        decoded_parts = decode_header(header_value)
        decoded_string = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    decoded_string += part.decode(encoding)
                else:
                    decoded_string += part.decode('utf-8', errors='ignore')
            else:
                decoded_string += part

        return decoded_string

    def _extract_email_content(self, email_message):
        """提取邮件内容和附件"""
        text_content = ""
        html_content = ""
        attachments = []

        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition", ""))

                    if "attachment" in content_disposition:
                        # 处理附件
                        filename = part.get_filename()
                        if filename and self._is_image_file(filename):
                            try:
                                payload = part.get_payload(decode=True)
                                if payload:
                                    attachments.append({
                                        'filename': filename,
                                        'content': base64.b64encode(payload).decode('utf-8'),
                                        'content_type': content_type
                                    })
                            except Exception as e:
                                logger.warning(f"处理附件失败: {filename}, {str(e)}")
                    elif content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            charset = part.get_content_charset() or 'utf-8'
                            payload = part.get_payload(decode=True)
                            if payload:
                                text_content += payload.decode(charset, errors='ignore')
                        except Exception as e:
                            logger.warning(f"解析文本内容失败: {str(e)}")
                    elif content_type == "text/html" and "attachment" not in content_disposition:
                        try:
                            charset = part.get_content_charset() or 'utf-8'
                            payload = part.get_payload(decode=True)
                            if payload:
                                html_content += payload.decode(charset, errors='ignore')
                        except Exception as e:
                            logger.warning(f"解析HTML内容失败: {str(e)}")
            else:
                # 非多部分邮件
                try:
                    charset = email_message.get_content_charset() or 'utf-8'
                    payload = email_message.get_payload(decode=True)
                    if payload:
                        content = payload.decode(charset, errors='ignore')
                        if email_message.get_content_type() == "text/html":
                            html_content = content
                        else:
                            text_content = content
                except Exception as e:
                    logger.warning(f"解析邮件内容失败: {str(e)}")
        except Exception as e:
            logger.error(f"提取邮件内容失败: {str(e)}")

        return text_content, html_content, attachments

    def _is_image_file(self, filename):
        """检查是否为图片文件"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        return any(filename.lower().endswith(ext) for ext in image_extensions)

    def _is_verification_email(self, content):
        """检查是否为验证码邮件"""
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in self._verification_keywords)

    def _check_keywords(self, content, keywords):
        """检查关键词匹配"""
        content_lower = content.lower()
        return any(keyword.lower() in content_lower for keyword in keywords)

    def _handle_verification_email_async(self, subject, content, attachments, sender, email_addr):
        """异步处理验证码邮件"""
        try:
            logger.info(f"[{email_addr}] 🤖 启动异步AI验证码识别")

            # 初始化线程池执行器（如果还没有）
            if self._executor is None:
                self._executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="AI-Worker")
                logger.debug(f"[{email_addr}] 🤖 创建AI线程池执行器")

            # 提交AI处理任务到线程池
            self._executor.submit(
                self._handle_verification_email_sync,
                subject, content, attachments, sender, email_addr
            )

            logger.info(f"[{email_addr}] 🤖 AI任务已提交到线程池，继续监控邮件")

        except Exception as e:
            logger.error(f"[{email_addr}] 🤖 ❌ 异步AI处理启动失败: {str(e)}")
            # 失败时直接发送原邮件
            self._send_notification(f"邮件通知 - {subject}", content, attachments, email_addr)

    def _handle_verification_email_sync(self, subject, content, attachments, sender, email_addr):
        """同步处理验证码邮件（在独立线程中运行）"""
        try:
            logger.info(f"[{email_addr}] 🤖 [AI线程] 开始AI验证码识别")

            if attachments:
                logger.info(f"[{email_addr}] 🤖 [AI线程] 包含 {len(attachments)} 个图片附件")

            # 创建AI处理器
            proxy_url = None
            if self._use_proxy:
                proxy_url = self.get_proxy_host()

            ai_handler = AIHandler(
                api_url=self._ai_url,
                api_key=self._ai_key,
                model=self._ai_model,
                proxy_url=proxy_url
            )

            # 调用AI处理验证码
            ai_response = ai_handler.get_verification_code(subject, content, attachments)

            if ai_response:
                if "不包含验证码" not in ai_response:
                    # AI识别成功，发送AI处理后的消息
                    logger.info(f"[{email_addr}] 🤖 [AI线程] ✅ AI识别成功")
                    logger.debug(f"[{email_addr}] 🤖 [AI线程] AI响应: {ai_response}")

                    lines = ai_response.strip().split('\n')
                    ai_title = lines[0].replace('标题：', '') if lines else subject
                    ai_content = lines[1].replace('内容：', '') if len(lines) > 1 else ai_response

                    logger.info(f"[{email_addr}] 🤖 [AI线程] 格式化标题: {ai_title}")
                    logger.info(f"[{email_addr}] 🤖 [AI线程] 格式化内容: {ai_content}")

                    # 使用统一格式发送AI处理后的消息
                    notification_title, formatted_content = self._format_ai_notification(sender, ai_title, ai_content)
                    self._send_notification(notification_title, formatted_content, [], email_addr)
                else:
                    # AI认为不包含验证码，直接发送原邮件
                    logger.info(f"[{email_addr}] 🤖 [AI线程] ❌ AI判断不包含验证码，发送原邮件")
                    formatted_content = self._format_email_notification("", sender, subject, content)
                    self._send_notification("邮件通知", formatted_content, attachments, email_addr)
            else:
                # AI调用失败，直接发送原邮件
                logger.warning(f"[{email_addr}] 🤖 [AI线程] ❌ AI调用失败，发送原邮件")
                formatted_content = self._format_email_notification("", sender, subject, content)
                self._send_notification("邮件通知", formatted_content, attachments, email_addr)

        except Exception as e:
            logger.error(f"[{email_addr}] 🤖 [AI线程] ❌ AI处理验证码邮件异常: {str(e)}")
            # 失败时直接发送原邮件
            self._send_notification(f"邮件通知 - {subject}", content, attachments, email_addr)

    def _send_keyword_email(self, subject, content, attachments, sender, email_addr):
        """发送关键词匹配的邮件"""
        logger.info(f"[{email_addr}] 🎯 发送关键词匹配邮件")
        # 统一格式：关键词邮件
        formatted_content = self._format_email_notification(
            "", sender, subject, content
        )
        self._send_notification("邮件通知", formatted_content, attachments, email_addr)

    def _format_email_notification(self, notification_type: str, sender: str, subject: str, content: str) -> str:
        """
        格式化邮件通知内容

        Args:
            notification_type: 通知类型（邮件通知/验证码邮件），为空时不显示
            sender: 发件人
            subject: 邮件标题
            content: 邮件内容

        Returns:
            格式化后的通知内容
        """
        if notification_type:
            return f"{notification_type}\n发件人：{sender}\n标题：{subject}\n内容：{content}"
        else:
            return f"发件人：{sender}\n标题：{subject}\n内容：{content}"

    def _format_ai_notification(self, sender: str, ai_title: str, ai_content: str) -> tuple[str, str]:
        """
        格式化AI处理后的通知内容

        Args:
            sender: 发件人
            ai_title: AI返回的标题
            ai_content: AI返回的内容

        Returns:
            (通知标题, 格式化后的通知内容)
        """
        formatted_content = f"发件人：{sender}\n标题：{ai_title}\n内容：{ai_content}"
        return "邮件通知", formatted_content





    def _send_notification(self, title, content, attachments=None, email_addr=""):
        """发送通知"""
        try:
            logger.info(f"[{email_addr}] 📢 开始发送通知")
            logger.info(f"[{email_addr}] 📢 标题: {title}")
            logger.info(f"[{email_addr}] 📢 内容长度: {len(content)} 字符")

            # 根据配置选择通知类型
            mtype = NotificationType.SiteMessage
            if self._msgtype:
                try:
                    mtype = NotificationType.__getitem__(str(self._msgtype)) or NotificationType.SiteMessage
                    logger.info(f"[{email_addr}] 📢 使用通知类型: {mtype.value}")
                except Exception as e:
                    logger.error(f"[{email_addr}] 📢 通知类型转换错误: {str(e)}，使用默认类型")
            else:
                logger.info(f"[{email_addr}] 📢 使用默认通知类型: {mtype.value}")

            # 发送主要消息
            logger.debug(f"[{email_addr}] 📢 发送主消息...")
            self.post_message(
                mtype=mtype,
                title=title,
                text=content
            )
            logger.info(f"[{email_addr}] 📢 ✅ 主消息发送成功")

            # 如果有图片附件，分别发送
            if attachments:
                logger.info(f"[{email_addr}] 📢 准备发送 {len(attachments)} 个附件")
                attachment_count = 0

                for attachment in attachments:
                    if attachment.get('content_type', '').startswith('image/'):
                        attachment_count += 1
                        attachment_title = f"{title} - 图片附件 {attachment_count}"
                        attachment_text = f"图片文件: {attachment['filename']}"

                        logger.debug(f"[{email_addr}] 📢 发送附件 {attachment_count}: {attachment['filename']}")

                        # 这里简化处理，实际可能需要保存图片到临时文件
                        self.post_message(
                            mtype=mtype,
                            title=attachment_title,
                            text=attachment_text
                        )

                        logger.info(f"[{email_addr}] 📢 ✅ 附件 {attachment_count} 发送成功")

                if attachment_count == 0:
                    logger.info(f"[{email_addr}] 📢 附件中无图片文件，跳过附件发送")
            else:
                logger.debug(f"[{email_addr}] 📢 无附件需要发送")

            logger.info(f"[{email_addr}] 📢 ✅ 通知发送完成")

        except Exception as e:
            logger.error(f"[{email_addr}] 📢 ❌ 发送通知失败: {str(e)}", exc_info=True)

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
                                            'hint': '开启或关闭邮件监控',
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
                                            'model': 'use_proxy',
                                            'label': '使用代理',
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
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'ai_enabled',
                                            'label': '验证码AI识别',
                                            'hint': '开启AI辅助识别验证码邮件',
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
                                        'component': 'VSelect',
                                        'props': {
                                            'model': 'msgtype',
                                            'label': '通知渠道',
                                            'items': MsgTypeOptions,
                                            'hint': '选择邮件通知渠道',
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
                                            'model': 'keywords',
                                            'label': '关键词',
                                            'placeholder': '关键词1|关键词2|关键词3',
                                            'hint': '邮件关键词过滤，多个关键词用|分隔',
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
                                            'model': 'ai_url',
                                            'label': 'AI接口URL',
                                            'placeholder': 'https://api.openai.com/v1/chat/completions',
                                            'hint': 'AI服务接口地址',
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
                                            'model': 'ai_key',
                                            'label': 'AI API Key',
                                            'placeholder': 'sk-xxxxxxxxxxxxxxxx',
                                            'hint': 'AI服务的API密钥',
                                            'persistent-hint': True,
                                            'type': 'password'
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
                                            'model': 'ai_model',
                                            'label': 'AI模型名称',
                                            'placeholder': 'gpt-3.5-turbo',
                                            'hint': 'AI模型名称',
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
                                            'model': 'email_configs',
                                            'label': '邮箱配置',
                                            'placeholder': 'example@qq.com|授权码\nexample@163.com|授权码',
                                            'hint': '每行一个邮箱，格式为：邮箱地址|授权码',
                                            'persistent-hint': True,
                                            'rows': 6
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
            "email_configs": self._email_configs,
            "msgtype": self._msgtype or "SiteMessage",
            "ai_enabled": self._ai_enabled,
            "ai_url": self._ai_url,
            "ai_key": self._ai_key,
            "ai_model": self._ai_model,
            "keywords": self._keywords
        }

    def get_page(self) -> List[dict]:
        """获取插件页面"""
        try:
            # 获取运行状态
            status = "运行中" if self._running else "已停止"
            email_configs = self._parse_email_configs()
            email_count = len(email_configs)

            # 安全获取关键词数量
            try:
                keywords_count = len(self._parse_keywords())
            except:
                keywords_count = 0

            # 构建邮箱状态表格数据
            email_rows = []
            if email_configs:
                for config in email_configs:
                    email_addr = config['email']
                    # 检查连接状态
                    is_connected = email_addr in self._imap_connections
                    status_text = "已连接" if is_connected else "未连接"
                    status_color = "success" if is_connected else "error"

                    email_rows.append({
                        'component': 'tr',
                        'props': {
                            'class': 'text-sm'
                        },
                        'content': [
                            {
                                'component': 'td',
                                'props': {
                                    'class': 'whitespace-nowrap break-keep text-high-emphasis'
                                },
                                'text': email_addr
                            },
                            {
                                'component': 'td',
                                'text': config.get('imap_server', 'N/A')
                            },
                            {
                                'component': 'td',
                                'content': [
                                    {
                                        'component': 'VChip',
                                        'props': {
                                            'color': status_color,
                                            'variant': 'tonal',
                                            'size': 'small',
                                            'class': 'font-weight-bold'
                                        },
                                        'text': status_text
                                    }
                                ]
                            }
                        ]
                    })
            else:
                email_rows.append({
                    'component': 'tr',
                    'props': {
                        'class': 'text-sm'
                    },
                    'content': [
                        {
                            'component': 'td',
                            'props': {
                                'colspan': 3,
                                'class': 'text-center text-medium-emphasis'
                            },
                            'text': '暂无配置的邮箱，请在设置页面添加邮箱配置'
                        }
                    ]
                })

        except Exception as e:
            logger.error(f"获取页面数据失败: {str(e)}")
            # 返回错误页面
            return [
                {
                    'component': 'VAlert',
                    'props': {
                        'type': 'error',
                        'text': f'页面加载失败: {str(e)}'
                    }
                }
            ]

        return [
            {
                'component': 'VRow',
                'props': {
                    'class': 'mb-4'
                },
                'content': [
                    {
                        'component': 'VCol',
                        'props': {
                            'cols': 12,
                            'md': 4
                        },
                        'content': [
                            {
                                'component': 'VCard',
                                'props': {
                                    'variant': 'tonal',
                                    'color': 'primary',
                                    'class': 'pa-3'
                                },
                                'content': [
                                    {
                                        'component': 'VCardText',
                                        'props': {
                                            'class': 'text-center'
                                        },
                                        'content': [
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'text-h5 font-weight-bold'
                                                },
                                                'text': str(email_count)
                                            },
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'text-body-2'
                                                },
                                                'text': '监控邮箱'
                                            }
                                        ]
                                    }
                                ]
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
                                'component': 'VCard',
                                'props': {
                                    'variant': 'tonal',
                                    'color': 'success' if self._running else 'warning',
                                    'class': 'pa-3'
                                },
                                'content': [
                                    {
                                        'component': 'VCardText',
                                        'props': {
                                            'class': 'text-center'
                                        },
                                        'content': [
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'text-h5 font-weight-bold'
                                                },
                                                'text': status
                                            },
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'text-body-2'
                                                },
                                                'text': '运行状态'
                                            }
                                        ]
                                    }
                                ]
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
                                'component': 'VCard',
                                'props': {
                                    'variant': 'tonal',
                                    'color': 'info' if self._ai_enabled else 'surface-variant',
                                    'class': 'pa-3'
                                },
                                'content': [
                                    {
                                        'component': 'VCardText',
                                        'props': {
                                            'class': 'text-center'
                                        },
                                        'content': [
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'text-h5 font-weight-bold'
                                                },
                                                'text': '已启用' if self._ai_enabled else '已禁用'
                                            },
                                            {
                                                'component': 'div',
                                                'props': {
                                                    'class': 'text-body-2'
                                                },
                                                'text': 'AI识别'
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
                'component': 'VCard',
                'content': [
                    {
                        'component': 'VCardTitle',
                        'props': {
                            'text': '邮箱监控状态'
                        }
                    },
                    {
                        'component': 'VTable',
                        'props': {
                            'hover': True
                        },
                        'content': [
                            {
                                'component': 'thead',
                                'content': [
                                    {
                                        'component': 'tr',
                                        'content': [
                                            {
                                                'component': 'th',
                                                'props': {
                                                    'class': 'text-start ps-4'
                                                },
                                                'text': '邮箱地址'
                                            },
                                            {
                                                'component': 'th',
                                                'props': {
                                                    'class': 'text-start ps-4'
                                                },
                                                'text': 'IMAP服务器'
                                            },
                                            {
                                                'component': 'th',
                                                'props': {
                                                    'class': 'text-start ps-4'
                                                },
                                                'text': '连接状态'
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                'component': 'tbody',
                                'content': email_rows
                            }
                        ]
                    }
                ]
            }
        ]

    def get_api(self) -> List[Dict[str, Any]]:
        """获取插件API"""
        return []

    def get_command(self) -> List[Dict[str, Any]]:
        """获取插件命令"""
        return []

    def get_service(self) -> List[Dict[str, Any]]:
        """获取插件服务"""
        return []

    def stop_service(self):
        """停止插件服务"""
        self.stop_monitoring()
        return True
