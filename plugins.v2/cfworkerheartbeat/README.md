# CFW设备在线汇报插件

## 简介

CFW设备在线汇报插件用于定期向 Cloudflare Worker 或服务器发送心跳请求，汇报设备在线状态，适用于需要远程监控设备在线情况的场景。

- **版本**：1.0.3
- **作者**：EWEDL
- **项目地址**：[GitHub](https://github.com/EWEDLCM)

## 功能特性

- 定期向 Cloudflare Worker 或服务器发送心跳请求，保持设备在线状态
- 支持自定义 Worker URL、设备名称、设备 Token
- 支持自定义心跳发送间隔（Cron 表达式）
- 支持详细日志记录模式
- 支持立即运行一次心跳
- 支持复用环境变量 `PROXY_HOST` 作为代理

## 配置说明

插件支持以下配置项，可通过前端表单或配置文件设置：

| 配置项                | 说明                                 | 示例/默认值                  |
|-----------------------|--------------------------------------|------------------------------|
| enabled               | 是否启用插件                         | true/false                   |
| worker_url            | Cloudflare Worker 或服务器完整 URL    | https://your-worker.workers.dev |
| device_name           | 设备名称，用于标识设备                | 设备A                        |
| device_token          | 设备认证令牌                         | xxxxxxxx                     |
| cron                  | 心跳发送周期（Cron 表达式，5位）      | */2 * * * *                  |
| verbose_logging       | 是否开启详细日志                     | true/false                   |
| onlyonce              | 保存后立即执行一次心跳                | true/false                   |
| use_proxy_host_cfw    | 是否使用 PROXY_HOST 代理              | true/false                   |


## 使用方法

1. 在插件管理界面启用插件，并填写相关配置信息。
2. 保存后插件会自动按照设定周期发送心跳请求。
3. 可通过“立即运行一次”开关，保存后立即发送一次心跳。
4. 若需通过代理访问 Worker，可启用“使用PROXY_HOST代理”并设置环境变量 `PROXY_HOST`。
5. 可通过命令 `/cfheartbeat` 手动触发一次心跳。

## 日志与排错

- 启用“详细日志记录”可在日志中看到心跳请求和响应详情。
- 若配置有误（如 URL、Token 未填写），插件会自动禁用并在日志中提示。
- 若启用代理但未设置 `PROXY_HOST`，插件会自动关闭代理开关并继续运行。


## 参考

- 详细使用说明请见飞牛论坛相关帖子[利用Cloudflare或服务器实现设备离线邮件通知](https://club.fnnas.com/forum.php?mod=viewthread&tid=36122)。
- 如有问题可在作者主页或论坛反馈。

