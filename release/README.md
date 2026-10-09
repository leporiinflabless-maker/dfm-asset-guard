# dfm-asset-guard · v1.0.0 正式版

> 三角洲行动资产监控与自动冻结系统 —— Windows x64 预编译包（2026-10-09）。
> 仓库：https://gitee.com/mhwpub/dfm-asset-guard

## 包内容

```
DFMMonitor/                     定制版监控面板（解压即用）
├── DFMMonitor.exe              主程序（默认已选「0三角洲监控」皮肤）
├── config.ini / global_cfg.ini 预置配置（便携模式）
├── Language/  Logo/  skins/    语言、图标、皮肤
└── plugins/DeltaGuard.dll      自带的三角洲资产监控插件

dfm-guard/
├── dfm-guard.exe               守卫服务（纯 VC++，零 Python 依赖）
└── service_config.example.json 服务配置样例（⚠ 需填写 server_token）
```

## 二进制校验（SHA256）

| 文件 | 大小 | SHA256 |
|---|---|---|
| `DFMMonitor\DFMMonitor.exe` | 1,907,712 B | `bfade8dee55038a5166f3c19025b45dd9fa21b8d1762734248ed60be81550e1a` |
| `DFMMonitor\plugins\DeltaGuard.dll` | 59,904 B | `93244d8ff46438c35b14254ad99e53b549085f4727e00433c0542bfd933b696c` |
| `dfm-guard\dfm-guard.exe` | 376,320 B | `ebbcc45c36d21b692d9c259861e6983ff534425ba9d226f37dc6e5d8b301952e` |

## 使用说明

### 1. DFMMonitor（监控面板）
- 将 `DFMMonitor/` 解压到任意目录，双击 `DFMMonitor.exe` 运行；
- 悬浮窗显示 `资产 / 哈夫币 / 状态`，宽度随内容自动调整；任务栏窗口同步显示；
- 右键菜单：置顶 / 穿透 / 锁定 / 透明度 / 皮肤 / 插件管理 / 选项 / 退出（已移除帮助与外部链接）。

### 2. dfm-guard（守卫服务）
- 将 `service_config.example.json` 复制为 `service_config.json` 填写配置
  （`email.server_token` 为服务器代发令牌，`email.to` 为接收告警的邮箱）；
- 常用命令：`dfm-guard.exe run`（常驻监控）/ `once`（单次采集）/ `status` / `test-email`；
- 邮件通知为**服务器代发**：告警 POST 到 `server_url/api/guard/notify`，由服务器 SMTP 统一发出，本地无需授权码；
- 面板通过 `plugins/DeltaGuard.dll` 显示服务状态（服务未运行时显示“服务离线”）。

### 3. 组合使用
`dfm-guard.exe run`（保持后台运行）+ `DFMMonitor.exe`（面板/托盘），即为完整监控形态。

## 版本

- **v1.0.0**（2026-10-09）首个正式版：
  - DFMMonitor：TrafficMonitor 定制（去流量/硬件/系统监控）+ 改名 + 悬浮窗宽度自适应 + 菜单精简（移除帮助/外链）；
  - DeltaGuard 插件：服务器代发邮件 + 收件邮箱可配置 + 插件对话框支持代发模式；
  - dfm-guard：服务器代发邮件（token 鉴权、白名单、限流）、配置热更新、`test-email` 按当前窗口设置测试。
