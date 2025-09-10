import asyncio
import hashlib
import os
import time
from typing import Optional, Dict, Any
from pathlib import Path

import aiohttp
import requests
from app.log import logger
from .token_manager import TokenManager


class CloudAPI123:
    """
    123云盘API客户端
    """
    
    def __init__(self, client_id: str, client_secret: str, config_path: Path, debug: bool = False):
        self.client_id = client_id
        self.client_secret = client_secret
        self.debug = debug
        self.config_path = config_path
        
        # 初始化Token管理器
        self.token_manager = TokenManager(config_path)
        
        # 内存中的token缓存（用于当前会话）
        self.access_token = None
        self.token_expires_at = 0
        
        # API配置
        self.base_url = "https://open-api.123pan.com"
        self.platform = "open_platform"
        
        # 默认父目录ID（根目录）
        self.parent_file_id = ""
        
        # 文件类型（1表示文件）
        self.file_type = 1

    def _log(self, level: str, message: str):
        """
        安全的日志记录方法
        """
        log_message = f"[CloudImg123-API] {message}"
        if level == "info":
            logger.info(log_message)
        elif level == "error":
            logger.error(log_message)
        elif level == "warning":
            logger.warning(log_message)
        elif level == "debug" and self.debug:
            logger.info(log_message)  # debug信息以info级别输出

    async def get_access_token(self) -> Optional[str]:
        """
        获取访问令牌，优先使用存储的有效token
        """
        try:
            # 1. 检查内存中的token是否还有效（用于当前会话）
            if self.access_token and time.time() < self.token_expires_at:
                logger.debug(f"[CloudImg123-API] 使用内存缓存的access_token")
                return self.access_token

            # 2. 尝试从存储中获取有效的token
            stored_token = self.token_manager.get_stored_token()
            if stored_token:
                # 更新内存缓存
                self.access_token = stored_token
                # 设置内存缓存过期时间为1小时（避免频繁检查存储）
                self.token_expires_at = time.time() + 3600
                logger.info(f"[CloudImg123-API] 使用存储的有效access_token")
                return stored_token

            # 3. 如果没有有效的存储token，则从API获取新token
            logger.info(f"[CloudImg123-API] 正在从API获取新的access_token...")
            
            url = f"{self.base_url}/api/v1/access_token"
            headers = {
                'Platform': self.platform,
                'Content-Type': 'application/json',
            }
            data = {
                'clientID': self.client_id,
                'clientSecret': self.client_secret,
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"[CloudImg123-API] 获取token失败，HTTP状态码: {response.status}")
                        return None
                    
                    resp_json = await response.json()
                    
                    if resp_json.get('code') != 0:
                        logger.error(f"[CloudImg123-API] 获取token失败，错误码: {resp_json.get('code')}，消息: {resp_json.get('message')}")
                        return None
                    
                    token_data = resp_json.get('data', {})
                    new_access_token = token_data.get('accessToken')
                    expires_in = token_data.get('expiresIn', 2592000)  # 默认30天（秒）
                    
                    if not new_access_token:
                        logger.error(f"[CloudImg123-API] API返回的token数据无效")
                        return None
                    
                    # 4. 保存新token到存储
                    save_success = self.token_manager.save_token(new_access_token, expires_in)
                    if save_success:
                        logger.info(f"[CloudImg123-API] 新token已保存到存储")
                    else:
                        logger.warning(f"[CloudImg123-API] 新token保存到存储失败，但仍可使用")
                    
                    # 5. 更新内存缓存
                    self.access_token = new_access_token
                    self.token_expires_at = time.time() + 3600  # 内存缓存1小时
                    
                    logger.info(f"[CloudImg123-API] 获取新access_token成功")
                    return new_access_token

        except Exception as e:
            logger.error(f"[CloudImg123-API] 获取access_token异常: {str(e)}")
            return None

    def _calc_md5(self, filepath: str) -> str:
        """
        计算文件MD5值
        """
        hash_md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _get_file_size(self, filepath: str) -> int:
        """
        获取文件大小
        """
        return os.path.getsize(filepath)

    async def upload_file(self, file_path: str, filename: str = None) -> Dict[str, Any]:
        """
        上传文件到123云盘
        """
        try:
            if not os.path.exists(file_path):
                return {"success": False, "message": "文件不存在"}

            # 获取访问令牌
            token = await self.get_access_token()
            if not token:
                return {"success": False, "message": "无法获取访问令牌"}

            # 文件信息
            if not filename:
                filename = os.path.basename(file_path)
            
            file_md5 = self._calc_md5(file_path)
            file_size = self._get_file_size(file_path)
            
            logger.info(f"[CloudImg123-API] 开始上传文件: {filename}，大小: {file_size} bytes")

            # 步骤1：创建文件（判断秒传/预上传）
            headers = {
                'Authorization': f'Bearer {token}',
                'Platform': self.platform,
                'Content-Type': 'application/json',
            }

            create_body = {
                'parentFileID': self.parent_file_id,
                'filename': filename,
                'etag': file_md5,
                'size': file_size,
                'type': self.file_type,
            }

            async with aiohttp.ClientSession() as session:
                # 创建文件
                async with session.post(f'{self.base_url}/upload/v1/oss/file/create', 
                                      json=create_body, headers=headers) as response:
                    if response.status != 200:
                        return {"success": False, "message": f"创建文件失败，状态码: {response.status}"}
                    
                    resp_json = await response.json()
                    
                    if resp_json.get('code') != 0:
                        return {"success": False, "message": f"创建文件失败: {resp_json.get('message')}"}

                    create_data = resp_json.get('data', {})
                    
                    # 检查是否秒传成功
                    if create_data.get('reuse'):
                        file_id = create_data['fileID']
                        logger.info(f"[CloudImg123-API] 文件秒传成功，fileID: {file_id}")
                        return await self._get_download_url(file_id, filename)

                    # 需要分片上传
                    preupload_id = create_data.get('preuploadID')
                    slice_size = create_data.get('sliceSize', 1024 * 1024 * 5)  # 默认5MB
                    total_slice = (file_size + slice_size - 1) // slice_size
                    
                    logger.info(f"[CloudImg123-API] 需分片上传，共 {total_slice} 片，每片 {slice_size} 字节")

                    # 步骤2&3：上传分片
                    with open(file_path, 'rb') as f:
                        for slice_no in range(1, total_slice + 1):
                            chunk = f.read(slice_size)
                            
                            # 获取分片上传地址
                            get_url_body = {
                                'preuploadID': preupload_id,
                                'sliceNo': slice_no,
                            }
                            
                            async with session.post(f'{self.base_url}/upload/v1/oss/file/get_upload_url',
                                                   json=get_url_body, headers=headers) as url_response:
                                if url_response.status != 200:
                                    return {"success": False, "message": f"获取上传地址失败，分片: {slice_no}"}
                                
                                url_json = await url_response.json()
                                if url_json.get('code') != 0:
                                    return {"success": False, "message": f"获取上传地址失败: {url_json.get('message')}"}
                                
                                presigned_url = url_json['data']['presignedURL']
                                
                                # 上传分片
                                put_headers = {'Content-Type': 'application/octet-stream'}
                                async with session.put(presigned_url, data=chunk, headers=put_headers) as put_response:
                                    if put_response.status not in [200, 201]:
                                        return {"success": False, "message": f"上传分片失败，分片: {slice_no}"}
                                
                                logger.debug(f"[CloudImg123-API] 分片 {slice_no}/{total_slice} 上传完成")

                    # 步骤4：通知上传完成
                    complete_body = {'preuploadID': preupload_id}
                    async with session.post(f'{self.base_url}/upload/v1/oss/file/upload_complete',
                                          json=complete_body, headers=headers) as complete_response:
                        if complete_response.status != 200:
                            return {"success": False, "message": "通知上传完成失败"}
                        
                        complete_json = await complete_response.json()
                        if complete_json.get('code') != 0:
                            return {"success": False, "message": f"通知上传完成失败: {complete_json.get('message')}"}
                        
                        complete_data = complete_json.get('data', {})
                        
                        # 检查是否需要异步等待
                        if not complete_data.get('async', False) and complete_data.get('fileID'):
                            file_id = complete_data['fileID']
                            logger.info(f"[CloudImg123-API] 同步上传完成，fileID: {file_id}")
                            return await self._get_download_url(file_id, filename)
                        else:
                            # 异步上传，需要轮询结果
                            logger.info(f"[CloudImg123-API] 异步上传，开始轮询...")
                            return await self._wait_for_async_upload(preupload_id, filename, headers, session)

        except Exception as e:
            logger.error(f"[CloudImg123-API] 上传文件异常: {str(e)}")
            return {"success": False, "message": f"上传异常: {str(e)}"}

    async def _wait_for_async_upload(self, preupload_id: str, filename: str, 
                                   headers: dict, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """
        等待异步上传完成
        """
        try:
            max_wait_time = 300  # 最大等待5分钟
            wait_interval = 2    # 每2秒查询一次
            waited = 0
            
            while waited < max_wait_time:
                async_body = {'preuploadID': preupload_id}
                async with session.post(f'{self.base_url}/upload/v1/oss/file/upload_async_result',
                                      json=async_body, headers=headers) as async_response:
                    if async_response.status != 200:
                        return {"success": False, "message": "查询异步上传结果失败"}
                    
                    async_json = await async_response.json()
                    if async_json.get('code') != 0:
                        return {"success": False, "message": f"查询异步上传结果失败: {async_json.get('message')}"}
                    
                    async_data = async_json.get('data', {})
                    if async_data.get('completed') and async_data.get('fileID'):
                        file_id = async_data['fileID']
                        logger.info(f"[CloudImg123-API] 异步上传完成，fileID: {file_id}")
                        return await self._get_download_url(file_id, filename)
                    
                    # 等待一段时间后重试
                    await asyncio.sleep(wait_interval)
                    waited += wait_interval
                    logger.debug(f"[CloudImg123-API] 异步上传等待中，已等待 {waited} 秒")
            
            return {"success": False, "message": "异步上传超时"}
            
        except Exception as e:
            logger.error(f"[CloudImg123-API] 等待异步上传异常: {str(e)}")
            return {"success": False, "message": f"异步上传异常: {str(e)}"}

    async def _get_download_url(self, file_id: str, filename: str) -> Dict[str, Any]:
        """
        获取文件下载链接
        """
        try:
            token = await self.get_access_token()
            if not token:
                return {"success": False, "message": "无法获取访问令牌"}

            headers = {
                'Authorization': f'Bearer {token}',
                'Platform': self.platform,
            }
            
            params = {'fileID': file_id}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.base_url}/api/v1/oss/file/detail',
                                     params=params, headers=headers) as response:
                    if response.status != 200:
                        return {"success": False, "message": f"获取文件详情失败，状态码: {response.status}"}
                    
                    detail_json = await response.json()
                    if detail_json.get('code') != 0:
                        return {"success": False, "message": f"获取文件详情失败: {detail_json.get('message')}"}
                    
                    detail_data = detail_json.get('data', {})
                    download_url = detail_data.get('downloadURL')
                    
                    if not download_url:
                        return {"success": False, "message": "未获取到下载链接"}
                    
                    logger.info(f"[CloudImg123-API] 获取下载链接成功: {download_url}")
                    
                    return {
                        "success": True,
                        "file_id": file_id,
                        "filename": filename,
                        "download_url": download_url,
                        "user_self_url": detail_data.get('userSelfURL'),
                        "size": detail_data.get('size'),
                        "upload_time": detail_data.get('createTime')
                    }

        except Exception as e:
            logger.error(f"[CloudImg123-API] 获取下载链接异常: {str(e)}")
            return {"success": False, "message": f"获取下载链接异常: {str(e)}"}

    def test_connection(self) -> bool:
        """
        测试API连接
        """
        try:
            # 使用同步方式测试连接
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            token = loop.run_until_complete(self.get_access_token())
            loop.close()
            return token is not None
        except Exception as e:
            logger.error(f"[CloudImg123-API] 测试连接异常: {str(e)}")
            return False

    def set_manual_token(self, access_token: str) -> bool:
        """
        手动设置token（用于测试或已有token）
        """
        try:
            # 保存到Token管理器
            save_success = self.token_manager.set_manual_token(access_token)
            
            if save_success:
                # 同时更新内存缓存
                self.access_token = access_token
                self.token_expires_at = time.time() + 3600  # 内存缓存1小时
                logger.info(f"[CloudImg123-API] 手动token设置成功")
                return True
            else:
                logger.error(f"[CloudImg123-API] 手动token设置失败")
                return False
                
        except Exception as e:
            logger.error(f"[CloudImg123-API] 手动设置token异常: {str(e)}")
            return False

    def get_token_info(self) -> Dict[str, Any]:
        """
        获取token详细信息
        """
        try:
            return self.token_manager.get_token_info()
        except Exception as e:
            logger.error(f"[CloudImg123-API] 获取token信息异常: {str(e)}")
            return {
                "has_token": False,
                "is_valid": False,
                "should_refresh": True,
                "error": str(e)
            }

    def clear_stored_token(self) -> bool:
        """
        清除存储的token
        """
        try:
            # 清除存储的token
            clear_success = self.token_manager.clear_token()
            
            # 清除内存缓存
            self.access_token = None
            self.token_expires_at = 0
            
            if clear_success:
                logger.info(f"[CloudImg123-API] token已清除")
            else:
                logger.warning(f"[CloudImg123-API] token清除可能不完整")
                
            return clear_success
            
        except Exception as e:
            logger.error(f"[CloudImg123-API] 清除token异常: {str(e)}")
            return False