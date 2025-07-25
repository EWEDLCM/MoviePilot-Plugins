"""
AI处理模块
支持多种AI服务：OpenAI、DeepSeek、Gemini、Claude等
"""
import time
import httpx
from typing import Optional, Dict, Any
from app.log import logger


class AIHandler:
    """AI处理器，支持多种AI服务"""
    
    def __init__(self, api_url: str, api_key: str, model: str = None, proxy_url: str = None):
        """
        初始化AI处理器
        
        Args:
            api_url: AI服务的API地址
            api_key: API密钥
            model: 模型名称
            proxy_url: 代理地址
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.proxy_url = proxy_url
        
        # 检测AI服务类型
        self.service_type = self._detect_service_type()
        logger.info(f"[AI] 检测到AI服务类型: {self.service_type}")
    
    def _detect_service_type(self) -> str:
        """检测AI服务类型"""
        url_lower = self.api_url.lower()
        
        if 'generativelanguage.googleapis.com' in url_lower:
            return 'gemini'
        elif 'api.anthropic.com' in url_lower:
            return 'claude'
        elif 'api.deepseek.com' in url_lower:
            return 'deepseek'
        elif 'api.openai.com' in url_lower:
            return 'openai'
        elif 'open.bigmodel.cn' in url_lower:
            return 'zhipu'
        elif 'aip.baidubce.com' in url_lower:
            return 'baidu'
        else:
            # 默认使用OpenAI兼容格式
            return 'openai_compatible'
    
    def get_verification_code(self, subject: str, content: str, attachments: list = None) -> Optional[str]:
        """
        从邮件内容中提取验证码信息

        Args:
            subject: 邮件标题
            content: 邮件内容
            attachments: 附件列表

        Returns:
            AI处理后的结果，如果失败返回None
        """
        try:
            # 检查是否有图片附件
            has_images = attachments and any(
                att.get('content_type', '').startswith('image/') and att.get('content')
                for att in attachments
            )

            if has_images:
                logger.info(f"[AI] 检测到图片附件，启用图片验证码识别")
                # 构建图片验证码提示词
                prompt = (
                    "请从邮件内容和图片中提取验证码信息，形成格式：\n"
                    "标题：接收到来自xx的验证码\n"
                    "内容：验证码是xxxxxx\n"
                    "请注意：\n"
                    "1. 如果图片中包含验证码，请优先识别图片中的验证码\n"
                    "2. 如果文字内容中也有验证码，请一并提取\n"
                    "3. 必须按上述格式回复，不要添加其他内容\n"
                    "4. 如果都不包含验证码，请回复\"不包含验证码\"\n"
                    f"邮件标题：{subject}\n"
                    f"邮件内容：{content}"
                )
            else:
                # 构建普通文本验证码提示词
                prompt = (
                    "我需要你从以下邮件内容中进行验证码提取，形成格式：\n"
                    "标题：接收到来自xx的验证码\n"
                    "内容：验证码是xxxxxx\n"
                    "请注意必须按此格式发送，不要添加其他任何内容，如果你认为内容中不包含验证码，请回复\"不包含验证码\"，"
                    "同样不要添加任何其他内容，以下是邮件内容：\n"
                    f"邮件标题：{subject}\n"
                    f"邮件内容：{content}"
                )

            logger.info(f"[AI] 开始验证码识别，服务类型: {self.service_type}，包含图片: {has_images}")

            # 根据服务类型调用相应的API
            if self.service_type == 'gemini':
                return self._call_gemini_api(prompt, attachments)
            elif self.service_type == 'claude':
                return self._call_claude_api(prompt, attachments)
            else:
                # OpenAI兼容格式（包括DeepSeek、OpenAI、智谱等）
                return self._call_openai_compatible_api(prompt, attachments)

        except Exception as e:
            logger.error(f"[AI] 验证码识别异常: {str(e)}")
            return None
    
    def _call_gemini_api(self, prompt: str, attachments: list = None) -> Optional[str]:
        """调用Gemini API"""
        try:
            # 检查是否有图片，选择合适的模型
            has_images = attachments and any(
                att.get('content_type', '').startswith('image/') and att.get('content')
                for att in attachments
            )

            if has_images:
                model_name = self.model or "gemini-1.5-flash"  # 支持图片的模型
            else:
                model_name = self.model or "gemini-pro"

            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"

            headers = {'Content-Type': 'application/json'}

            # 构建内容部分
            parts = [{"text": prompt}]

            # 添加图片
            if has_images:
                for att in attachments:
                    if att.get('content_type', '').startswith('image/') and att.get('content'):
                        # 获取图片的MIME类型
                        mime_type = att.get('content_type', 'image/jpeg')
                        parts.append({
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": att['content']  # base64编码的图片数据
                            }
                        })
                        logger.debug(f"[AI] 添加图片到Gemini请求: {att.get('filename', 'unknown')} ({mime_type})")

            data = {
                "contents": [{
                    "parts": parts
                }],
                "generationConfig": {
                    "maxOutputTokens": 8192,
                    "temperature": 0.1
                }
            }
            
            return self._make_request(api_url, headers, data, 'gemini')
            
        except Exception as e:
            logger.error(f"[AI] Gemini API调用异常: {str(e)}")
            return None
    
    def _call_claude_api(self, prompt: str, attachments: list = None) -> Optional[str]:
        """调用Claude API"""
        try:
            api_url = f"{self.api_url}/v1/messages"

            headers = {
                'x-api-key': self.api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }

            # 构建消息内容
            content = [{"type": "text", "text": prompt}]

            # 添加图片
            if attachments:
                for att in attachments:
                    if att.get('content_type', '').startswith('image/') and att.get('content'):
                        # Claude支持的图片格式
                        mime_type = att.get('content_type', 'image/jpeg')
                        if mime_type in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']:
                            content.append({
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": mime_type,
                                    "data": att['content']
                                }
                            })
                            logger.debug(f"[AI] 添加图片到Claude请求: {att.get('filename', 'unknown')} ({mime_type})")

            data = {
                "model": self.model or "claude-3-sonnet-20240229",
                "max_tokens": 500,
                "temperature": 0.1,
                "messages": [
                    {"role": "user", "content": content}
                ]
            }
            
            return self._make_request(api_url, headers, data, 'claude')
            
        except Exception as e:
            logger.error(f"[AI] Claude API调用异常: {str(e)}")
            return None
    
    def _call_openai_compatible_api(self, prompt: str, attachments: list = None) -> Optional[str]:
        """调用OpenAI兼容的API"""
        try:
            # 构建完整的API URL
            if self.service_type == 'openai_compatible':
                api_url = f"{self.api_url}/chat/completions"
            else:
                api_url = f"{self.api_url}/v1/chat/completions"

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            # 构建消息内容
            content = [{"type": "text", "text": prompt}]

            # 添加图片（仅对支持vision的模型）
            if attachments and self.service_type in ['openai']:
                for att in attachments:
                    if att.get('content_type', '').startswith('image/') and att.get('content'):
                        mime_type = att.get('content_type', 'image/jpeg')
                        content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{att['content']}"
                            }
                        })
                        logger.debug(f"[AI] 添加图片到OpenAI请求: {att.get('filename', 'unknown')} ({mime_type})")

            # 如果有图片，使用支持vision的模型
            model = self.model or "gpt-3.5-turbo"
            if attachments and any(att.get('content_type', '').startswith('image/') for att in attachments):
                if self.service_type == 'openai' and not model.startswith('gpt-4'):
                    model = "gpt-4-vision-preview"  # 使用支持图片的模型

            data = {
                "model": model,
                "messages": [
                    {"role": "user", "content": content if len(content) > 1 else prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.1
            }
            
            return self._make_request(api_url, headers, data, 'openai_compatible')
            
        except Exception as e:
            logger.error(f"[AI] OpenAI兼容API调用异常: {str(e)}")
            return None
    
    def _make_request(self, url: str, headers: dict, data: dict, service_type: str) -> Optional[str]:
        """发送HTTP请求"""
        try:
            logger.debug(f"[AI] 请求URL: {url}")
            logger.debug(f"[AI] 请求数据: {data}")
            
            # 设置客户端参数
            client_kwargs = {"timeout": 30.0}
            if self.proxy_url:
                client_kwargs["proxies"] = self.proxy_url
                logger.debug(f"[AI] 使用代理: {self.proxy_url}")
            
            start_time = time.time()
            
            with httpx.Client(**client_kwargs) as client:
                response = client.post(url, headers=headers, json=data)
            
            elapsed_time = time.time() - start_time
            logger.info(f"[AI] API响应时间: {elapsed_time:.2f}秒")
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_response(result, service_type)
            else:
                logger.error(f"[AI] API调用失败: HTTP {response.status_code}")
                logger.error(f"[AI] 错误响应: {response.text[:500]}")
                return None
                
        except httpx.TimeoutException:
            logger.error(f"[AI] API调用超时")
            return None
        except httpx.ConnectError:
            logger.error(f"[AI] API连接失败")
            return None
        except Exception as e:
            logger.error(f"[AI] 请求异常: {str(e)}")
            return None
    
    def _parse_response(self, result: dict, service_type: str) -> Optional[str]:
        """解析API响应"""
        try:
            if service_type == 'gemini':
                if 'candidates' in result and result['candidates']:
                    candidate = result['candidates'][0]

                    # 检查是否因为token限制而截断
                    finish_reason = candidate.get('finishReason', '')
                    if finish_reason == 'MAX_TOKENS':
                        logger.warning(f"[AI] Gemini响应被截断 (MAX_TOKENS)")

                    # 尝试提取内容
                    if 'content' in candidate:
                        content_obj = candidate['content']
                        if 'parts' in content_obj and content_obj['parts']:
                            content = content_obj['parts'][0]['text']
                            logger.info(f"[AI] Gemini响应成功，长度: {len(content)} 字符")
                            return content
                        else:
                            logger.error(f"[AI] Gemini响应缺少parts: {content_obj}")
                    else:
                        logger.error(f"[AI] Gemini响应缺少content: {candidate}")

            elif service_type == 'claude':
                if 'content' in result and result['content']:
                    content = result['content'][0]['text']
                    logger.info(f"[AI] Claude响应成功，长度: {len(content)} 字符")
                    return content

            else:  # OpenAI兼容格式
                if 'choices' in result and result['choices']:
                    content = result['choices'][0]['message']['content']
                    logger.info(f"[AI] OpenAI兼容API响应成功，长度: {len(content)} 字符")
                    return content

            logger.error(f"[AI] 响应格式异常: {result}")
            return None

        except Exception as e:
            logger.error(f"[AI] 响应解析异常: {str(e)}")
            return None
    
    def test_connection(self) -> tuple[bool, str]:
        """测试AI服务连接"""
        try:
            result = self.get_verification_code("测试", "这是一个测试消息")
            if result:
                return True, "连接成功"
            else:
                return False, "API调用失败"
        except Exception as e:
            return False, f"连接测试失败: {str(e)}"
