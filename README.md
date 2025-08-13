# MoviePilot-Plugins

这是一个MoviePilot的第三方插件仓库，提供了各种实用的MoviePilot插件。

## 插件列表

| 插件名称 | 描述 | 版本 |
| --- | --- | --- |
| [站点签到（多站点版）](./plugins/dzdsingnin/README.md) | 支持多个站点的自动签到功能，用户可自定义签到站点配置 | 1.1.1 |
| [代理地址测试](./plugins/proxytest/README.md) | 测试容器内的HTTP代理设置，并尝试使用代理连接外网 | 1.1.1 |
| [插件代理控制器](./plugins/proxycontroller/README.md) |用于控制其他插件是否使用 PROXY_HOST 代理 | 1.6.2 |
| [邮件集](./plugins/yjj/README.md) |实时监控邮箱，支持验证码AI识别和关键词过滤，按需推送重要邮件| 1.1.8 |
## 安装插件

1. 在MoviePilot -> 设置 -> 插件 中，添加第三方插件仓库：`https://github.com/EWEDLCM/MoviePilot-Plugins`
2. 在第三方插件列表中找到需要的插件，点击安装
3. 进入插件设置页面完成配置

## 插件开发与源码说明

- 所有插件源码位于 `plugins` 目录下
- 插件图标位于 `icons` 目录下
- 每个插件目录下的 `README.md` 文件包含了该插件的详细说明和使用方法

## 问题反馈

如果在使用过程中遇到任何问题，或者有新的功能需求，欢迎提交 [Issues](https://github.com/EWEDLCM/MoviePilot-Plugins/issues)。

## 授权协议

本项目采用 MIT 协议开源，详情请参阅 [LICENSE](./LICENSE) 文件。 
