# dfm-asset-guard · v1.0.3

> 三角洲行动资产监控与自动冻结系统 —— Windows x64 预编译包（2026-10-09）。
> 仓库：https://gitee.com/mhwpub/dfm-asset-guard

## v1.0.3 更新

- **新增走马灯广告位**：悬浮窗与任务栏窗口每 **30 分钟**播放 3 遍
  「卖哈夫币就到猛号网，https://mhw.pub」（启动 60 秒后首次播放）；
- **单击窗口直达猛号网**：广告播放或正常显示时，单击（无拖动）悬浮窗/任务栏窗口即打开 https://mhw.pub；
- **更新源移除 GitHub**：仅保留本项目 Gitee 更新源（设置界面同步精简）；
- 其余功能同 v1.0.2。

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
| `DFMMonitor\DFMMonitor.exe` | 1,904,128 B | `0500282eea467e2425f1188f3b5ef8ef0f6e067633b203b45e260dade74324e6` |
| `DFMMonitor\plugins\DeltaGuard.dll` | 66,560 B | `6ebd9c9dc65940b65ab0976b29699b3e339bdfe672a73fecf81061320a70cfee` |
| `dfm-guard\dfm-guard.exe` | 380,416 B | `8787d7d0277f1da9761a91c9e6592ea6eada1e9a0d8afb67617b3b1a98afe866` |

## 使用说明

### 1. DFMMonitor（监控面板）
- 将 `DFMMonitor/` 解压到任意目录（**不要放在系统 Temp 目录**，否则配置会转存到 `%APPDATA%\TrafficMonitor`），双击 `DFMMonitor.exe`；
- 悬浮窗显示 `资产 / 哈夫币 / 状态`，宽度随内容自动调整；任务栏窗口同步显示；
- 首次启动窗口自动出现，拖动到合适位置即可（位置自动记忆）；
- **走马灯广告**：每 30 分钟轮播 3 遍（启动 60 秒后首次），单击窗口打开猛号网；
- **检查更新**：启动时自动检查（可在 设置-常规 关闭），或右键菜单 →「检查更新」；更新源为项目 Gitee 仓库。

### 2. dfm-guard（守卫服务）
- 将 `service_config.example.json` 复制为 `service_config.json`（与 dfm-guard.exe 同目录）并填写：
  `email.server_token`（服务器代发令牌）、`email.to`（接收告警邮箱）；
- 可直接双击运行 `dfm-guard.exe`（带界面）或命令行 `dfm-guard.exe run`；
- **插件会自动查找并拉起本服务**（无需手动启动）；
- 邮件为服务器代发：告警 POST 到 `server_url/api/guard/notify`，由服务器 SMTP 统一发出。

### 3. 组合使用
解压整包后：先启动 `DFMMonitor.exe`（插件会自动拉起 `dfm-guard.exe`），即可看到实时数据。

## 版本

- **v1.0.3**（2026-10-09）：走马灯广告位（悬浮窗/任务栏，30 分钟×3 遍，单击直达 mhw.pub）+ 更新源移除 GitHub；
- **v1.0.2**（2026-10-09）：检查更新接入 Gitee 更新源 + 数值版本比较 + 缓存修复 + 启动自检；
- **v1.0.1**（2026-10-09）：解压即用（插件/服务相对路径）+ 发布配置修复；
- **v1.0.0**（2026-10-09）：首个正式版（DFMMonitor 改名/自适应/菜单精简；服务器代发邮件；冻结/解冻执行）。
