#!/usr/bin/env python3
"""
CloudImg123 插件测试脚本
用于验证后端功能是否正常工作
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加插件路径到 Python 路径
plugin_path = Path(__file__).parent
sys.path.insert(0, str(plugin_path))

try:
    from api_client import CloudAPI123
    from upload_manager import UploadManager
    from history_manager import HistoryManager, UploadRecord
    from utils import validate_image_file, format_file_size
    from token_manager import TokenManager
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有模块文件都存在且正确")
    sys.exit(1)


class MockLogger:
    """模拟日志类，用于测试环境"""
    
    @staticmethod
    def info(msg):
        print(f"[INFO] {msg}")
    
    @staticmethod
    def error(msg):
        print(f"[ERROR] {msg}")
    
    @staticmethod
    def warning(msg):
        print(f"[WARNING] {msg}")


# 替换日志模块
sys.modules['app.log'] = type('MockModule', (), {'logger': MockLogger()})


class CloudImg123Tester:
    """插件测试类"""
    
    def __init__(self):
        self.client_id = ""
        self.client_secret = ""
        self.manual_token = ""  # 新增：手动输入的token
        self.config_path = Path(__file__).parent / "test_config"  # 使用测试配置目录
        
        # 组件
        self.api_client = None
        self.history_manager = None
        self.upload_manager = None
        self.token_manager = None

    def setup_credentials(self):
        """设置API凭证或直接输入token"""
        print("\n=== CloudImg123 插件测试 ===")
        print("选择认证方式：")
        print("1. 使用Client ID和Client Secret（会获取新token）")
        print("2. 直接输入已有的access_token")
        
        while True:
            choice = input("请选择 (1 或 2): ").strip()
            
            if choice == "1":
                return self._setup_client_credentials()
            elif choice == "2":
                return self._setup_manual_token()
            else:
                print("无效选择，请输入1或2")
    
    def _setup_client_credentials(self):
        """设置Client ID和Secret"""
        print("\n--- 输入123云盘API凭证 ---")
        
        self.client_id = input("Client ID: ").strip()
        if not self.client_id:
            print("Client ID不能为空")
            return False
        
        self.client_secret = input("Client Secret: ").strip()
        if not self.client_secret:
            print("Client Secret不能为空") 
            return False
        
        return True
    
    def _setup_manual_token(self):
        """设置手动token"""
        print("\n--- 输入已有的access_token ---")
        
        self.manual_token = input("Access Token: ").strip()
        if not self.manual_token:
            print("Access Token不能为空")
            return False
        
        # 为手动token模式设置默认值
        self.client_id = "manual_token_mode"
        self.client_secret = "manual_token_mode"
        
        return True

    def initialize_components(self):
        """初始化组件"""
        try:
            print("\n--- 初始化组件 ---")
            
            # 创建配置目录
            if not self.config_path.exists():
                self.config_path.mkdir(parents=True, exist_ok=True)
                print(f"创建配置目录: {self.config_path}")

            # 初始化Token管理器
            self.token_manager = TokenManager(self.config_path)
            print("✓ Token管理器初始化成功")

            # 初始化API客户端
            self.api_client = CloudAPI123(
                client_id=self.client_id,
                client_secret=self.client_secret,
                config_path=self.config_path,
                debug=True
            )
            
            # 如果是手动token模式，先设置token
            if self.manual_token:
                token_set = self.api_client.set_manual_token(self.manual_token)
                if token_set:
                    print("✓ 手动token设置成功")
                else:
                    print("✗ 手动token设置失败")
                    return False
                    
            print("✓ API客户端初始化成功")

            # 初始化历史管理器
            self.history_manager = HistoryManager(
                config_path=self.config_path,
                limit=10
            )
            print("✓ 历史管理器初始化成功")

            # 初始化上传管理器
            self.upload_manager = UploadManager(
                api_client=self.api_client,
                history_manager=self.history_manager
            )
            print("✓ 上传管理器初始化成功")
            
            return True

        except Exception as e:
            print(f"✗ 初始化组件失败: {e}")
            return False

    async def test_api_connection(self):
        """测试API连接"""
        try:
            print("\n--- 测试API连接 ---")
            
            # 显示token信息
            token_info = self.api_client.get_token_info()
            print(f"Token信息:")
            print(f"  是否有token: {token_info.get('has_token')}")
            print(f"  是否有效: {token_info.get('is_valid')}")
            if token_info.get('has_token'):
                print(f"  token年龄: {token_info.get('age_days', 0):.1f}天")
                print(f"  剩余天数: {token_info.get('remaining_days', 0):.1f}天")
                print(f"  创建日期: {token_info.get('created_date')}")
                print(f"  过期日期: {token_info.get('expires_date')}")
            
            token = await self.api_client.get_access_token()
            
            if token:
                print("✓ API连接测试成功")
                print(f"获取到Token: {token[:20]}...")
                return True
            else:
                print("✗ API连接测试失败")
                return False

        except Exception as e:
            print(f"✗ API连接测试异常: {e}")
            return False

    def test_token_manager(self):
        """测试Token管理器"""
        try:
            print("\n--- 测试Token管理器 ---")
            
            # 获取token信息
            token_info = self.token_manager.get_token_info()
            print(f"✓ Token信息获取成功")
            print(f"  是否有token: {token_info.get('has_token')}")
            print(f"  是否有效: {token_info.get('is_valid')}")
            print(f"  应否刷新: {token_info.get('should_refresh')}")
            
            if token_info.get('has_token'):
                print(f"  创建日期: {token_info.get('created_date')}")
                print(f"  过期日期: {token_info.get('expires_date')}")
            
            # 测试是否可以获取存储的token
            stored_token = self.token_manager.get_stored_token()
            if stored_token:
                print(f"✓ 获取到存储的token: {stored_token[:20]}...")
            else:
                print("✓ 没有存储的token（正常）")
            
            return True

        except Exception as e:
            print(f"✗ Token管理器测试异常: {e}")
            return False

    def test_history_manager(self):
        """测试历史管理器"""
        try:
            print("\n--- 测试历史管理器 ---")
            
            # 创建测试记录
            test_record = UploadRecord(
                filename="test_image.jpg",
                file_id="test_file_id",
                download_url="https://example.com/test.jpg",
                file_size=102400,
                formats={
                    "url": "https://example.com/test.jpg",
                    "html": '<img src="https://example.com/test.jpg" alt="test_image">',
                    "markdown": '![test_image](https://example.com/test.jpg)',
                    "bbcode": '[img]https://example.com/test.jpg[/img]'
                }
            )
            
            # 添加记录
            success = self.history_manager.add_record(test_record)
            if success:
                print("✓ 添加测试记录成功")
            else:
                print("✗ 添加测试记录失败")
                return False

            # 获取历史记录
            history = self.history_manager.get_history(limit=5)
            print(f"✓ 获取历史记录成功，数量: {len(history)}")

            # 获取统计信息
            stats = self.history_manager.get_statistics()
            print(f"✓ 统计信息 - 总数: {stats['total_count']}, 总大小: {format_file_size(stats['total_size'])}")

            return True

        except Exception as e:
            print(f"✗ 历史管理器测试异常: {e}")
            return False

    def test_file_validation(self):
        """测试文件验证"""
        try:
            print("\n--- 测试文件验证 ---")
            
            # 创建一个测试图片文件
            test_image_path = self.config_path / "test_image.jpg"
            with open(test_image_path, 'wb') as f:
                # 创建一个简单的测试文件
                f.write(b"fake_image_data" * 100)  # 创建一个较小的测试文件

            # 验证文件
            validation = validate_image_file(str(test_image_path))
            
            if validation["valid"]:
                print(f"✓ 文件验证成功: {validation['size_formatted']}")
            else:
                print(f"✗ 文件验证失败: {validation['message']}")

            # 测试不存在的文件
            fake_file = validate_image_file("nonexistent.jpg")
            if not fake_file["valid"]:
                print("✓ 不存在文件验证正确")

            # 清理测试文件
            if test_image_path.exists():
                test_image_path.unlink()

            return True

        except Exception as e:
            print(f"✗ 文件验证测试异常: {e}")
            return False

    def test_upload_capability(self):
        """测试上传能力"""
        try:
            print("\n--- 测试上传能力 ---")
            
            result = self.upload_manager.test_upload_capability()
            
            if result["success"]:
                print("✓ 上传能力测试成功")
                print(f"  {result['message']}")
                return True
            else:
                print(f"✗ 上传能力测试失败: {result['message']}")
                return False

        except Exception as e:
            print(f"✗ 上传能力测试异常: {e}")
            return False

    async def run_all_tests(self):
        """运行所有测试"""
        try:
            # 设置凭证
            if not self.setup_credentials():
                return False

            # 初始化组件
            if not self.initialize_components():
                return False

            # 执行所有测试
            tests = [
                ("API连接测试", self.test_api_connection()),
                ("Token管理测试", self.test_token_manager()),
                ("历史管理器测试", self.test_history_manager()),
                ("文件验证测试", self.test_file_validation()),
                ("上传能力测试", self.test_upload_capability())
            ]

            results = []
            for test_name, test_coro in tests:
                try:
                    if asyncio.iscoroutine(test_coro):
                        result = await test_coro
                    else:
                        result = test_coro
                    results.append((test_name, result))
                except Exception as e:
                    print(f"✗ {test_name} 执行异常: {e}")
                    results.append((test_name, False))

            # 输出测试结果
            print("\n" + "=" * 40)
            print("测试结果汇总：")
            print("=" * 40)
            
            passed = 0
            total = len(results)
            
            for test_name, result in results:
                status = "✓ 通过" if result else "✗ 失败"
                print(f"{test_name}: {status}")
                if result:
                    passed += 1

            print("=" * 40)
            print(f"测试完成: {passed}/{total} 通过")
            
            if passed == total:
                print("🎉 所有测试通过！后端功能正常")
                return True
            else:
                print("⚠️ 部分测试失败，请检查相关功能")
                return False

        except Exception as e:
            print(f"测试执行异常: {e}")
            return False


async def main():
    """主函数"""
    tester = CloudImg123Tester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✨ CloudImg123 后端功能验证完成，可以继续开发前端")
    else:
        print("\n❌ 后端功能存在问题，请先修复后再继续")
    
    return success


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n用户取消测试")
    except Exception as e:
        print(f"测试脚本执行异常: {e}")