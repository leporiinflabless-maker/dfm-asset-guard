# dfm-asset-guard · v1.0.1

> 三角洲行动资产监控与自动冻结系统 —— Windows x64 预编译包（2026-10-09）。
> 仓库：https://gitee.com/mhwpub/dfm-asset-guard

## v1.0.1 更新

- **解压即用**：插件（DeltaGuard.dll）支持**相对路径**查找并拉起守卫服务
  （`<包根>\dfm-guard\dfm-guard.exe`、插件同目录等，按顺序探测），无需再设置 `DFM_GUARD_ROOT` 环境变量；
- **守卫服务相对定位**：`ProjectRoot` 自动探测（环境变量 → 包内相对位置 → 开发路径），
  `service_config.json` 优先取与 `dfm-guard.exe` 同目录；
- **修复发布配置文件缺失 UTF-8 BOM** 导致的启动异常（含中文的配置需 BOM，现已随包提供）；
- 其余功能同 v1.0.0。

## 包内容

```
DFMMonitor/                     定制版监控面板（解压即用）
├── DFMMonitor.exe              主程序（默认「0三角洲监控」皮肤，首次启动自动放置窗口）
├── config.ini / global_cfg.ini 预置配置（便携模式）
├── language/  Logo/  skins/    语言、图标、皮肤
└── plugins/DeltaGuard.dll      三角洲资产监控插件（自动拉起服务）

dfm-guard/
├── dfm-guard.exe               守卫服务（纯 VC++，零 Python 依赖）
└── service_config.example.json 服务配置样例（⚠ 复制为 service_config.json 并填写 server_token）
```

## 二进制校验（SHA256）

| 文件 | 大小 | SHA256 |
|---|---|---|
| `DFMMonitor\DFMMonitor.exe` | 1,907,712 B | `bfade8dee55038a5166f3c19025b45dd9fa21b8d1762734248ed60be81550e1a` |
| `DFMMonitor\plugins\DeltaGuard.dll` | 66,560 B | `6ebd9c9dc65940b65ab0976b29699b3e339bdfe672a73fecf81061320a70cfee` |
| `dfm-guard\dfm-guard.exe` | 380,416 B | `8787d7d0277f1da9761a91c9e6592ea6eada1e9a0d8afb67617b3b1a98afe866` |

## 使用说明

### 1. DFMMonitor（监控面板）
- 将 `DFMMonitor/` 解压到任意目录（**不要放在系统 Temp 目录**，否则配置会转存到 `%APPDATA%\TrafficMonitor`），双击 `DFMMonitor.exe`；
- 悬浮窗显示 `资产 / 哈夫币 / 状态`，宽度随内容自动调整；任务栏窗口同步显示；
- 首次启动窗口自动出现，拖动到合适位置即可（位置自动记忆）。

### 2. dfm-guard（守卫服务）
- 将 `service_config.example.json` 复制为 `service_config.json`（与 dfm-guard.exe 同目录）并填写：
  `email.server_token`（服务器代发令牌）、`email.to`（接收告警邮箱）；
- 可直接双击运行 `dfm-guard.exe`（带界面）或命令行 `dfm-guard.exe run`；
- **插件会自动查找并拉起本服务**（无需手动启动）；
- 邮件为服务器代发：告警 POST 到 `server_url/api/guard/notify`，由服务器 SMTP 统一发出。

### 3. 组合使用
解压整包后：先启动 `DFMMonitor.exe`（插件会自动拉起 `dfm-guard.exe`），即可看到实时数据。

## 版本

- **v1.0.1**（2026-10-09）：解压即用（插件/服务相对路径）+ 发布配置修复；
- **v1.0.0**（2026-10-09）：首个正式版（DFMMonitor 改名/自适应/菜单精简；服务器代发邮件；冻结/解冻执行）。
