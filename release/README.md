# dfm-asset-guard · v1.0.5

> 三角洲行动资产监控与自动冻结系统 —— Windows x64 预编译包（2026-10-10）。
> 仓库：https://gitee.com/mhwpub/dfm-asset-guard ｜ https://github.com/leporiinflabless-maker/dfm-asset-guard

## v1.0.5 更新

- **「重新授权」功能（纯 C++）**：守卫新增 `reauth` 命令，插件菜单新增「重新授权（抓取微信登录态）」；
  会话失效后，点击后只需在微信里打开一次「腾讯游戏安全中心」页面即可自动抓取恢复——
  **不再需要 Python / frida 工具**；
- **抓取组件**：新增 `dfm-authcap.dll`（注入微信网络进程，挂钩 SSL 明文层，解码 HTTP/2+HPACK 提取登录凭据）；
- **cookies 默认位置**：`cookies.json` 未配置时默认保存在 `dfm-guard.exe` 同目录（自包含，整包迁移无需改配置）；
- 其余同 v1.0.4。

## 包内容

```
DFMMonitor/                     定制版监控面板（解压即用）
├── DFMMonitor.exe              主程序（默认「0三角洲监控」皮肤）
├── config.ini / global_cfg.ini 预置配置（便携模式）
├── language/  Logo/  skins/    语言、图标、皮肤
└── plugins/DeltaGuard.dll      三角洲资产监控插件（自动拉起服务）

dfm-guard/
├── dfm-guard.exe               守卫服务（纯 VC++，零 Python 依赖）
├── dfm-authcap.dll             登录态抓取组件（“重新授权”使用）
└── service_config.example.json 服务配置样例（⚠ 复制为 service_config.json 并填写 server_token）
```

## 二进制校验（SHA256）

| 文件 | 大小 | SHA256 |
|---|---|---|
| `DFMMonitor\DFMMonitor.exe` | 1,904,128 B | `642286645594beaf569a3bb616b212bdc16dff375142a24348e9dfd59f9a12e6` |
| `DFMMonitor\plugins\DeltaGuard.dll` | 67,072 B | `30655c8238d7d8688638c00899ec0cb97325a8396d72e8f67d7f5da2b587bc09` |
| `dfm-guard\dfm-guard.exe` | 398,336 B | `f01c272784da8810d861c848e9a8dc7891219387200d6ca55defcb7b7719221e` |
| `dfm-guard\dfm-authcap.dll` | 276,992 B | `d36095b2c7002ccf0791a6dadbf24e6062d384bb2d7284ecbf4307cb75ffb296` |

## 使用说明

> 📖 **完整操作手册见包内《操作说明.md》**（安装、菜单、设置、重新授权步骤、微信版本依赖、常见问题）。

### 1. DFMMonitor（监控面板）
- 解压到任意目录（**不要放在系统 Temp 目录**），双击 `DFMMonitor.exe`；悬浮窗/任务栏窗口显示资产、哈夫币、状态；
- **检查更新**：启动自动检查或右键菜单 →「检查更新」（更新源为本项目 Gitee 仓库）；
- 每 30 分钟播放 3 遍走马灯提示（单击窗口打开 https://mhw.pub）。

### 2. dfm-guard（守卫服务）
- 复制 `service_config.example.json` 为 `service_config.json`（与 exe 同目录），填写 `email.server_token`、`email.to`；
- 双击运行或 `dfm-guard.exe run`；插件会自动拉起本服务；
- **重新授权**（会话失效后恢复）：
  - 面板右键任一窗口 → 三角洲资产监控 → **重新授权（抓取微信登录态）**；
  - 或命令行 `dfm-guard.exe reauth`；
  - 执行后按提示在微信里打开一次「腾讯游戏安全中心」页面（打开“冻结查询”停留几秒），
    抓取完成后自动写入并恢复登录态（无需 Python/frida）；
  - ⚠ **微信版本依赖**：抓取组件适配 **微信 Windows 4.1.15**（XWeb/flue 运行时 25715）；
    官方下载：https://dldir1v6.qq.com/weixin/Universal/Windows/WeChatWin_4.1.15.exe
    其他版本可能不工作；微信升级后如抓取失效，需重新定位偏移（详见《操作说明.md》第八节）。

### 3. 组合使用
解压整包后：先启动 `DFMMonitor.exe`（插件会自动拉起 `dfm-guard.exe`），即可看到实时数据。

## 版本

- **v1.0.5**（2026-10-10）：重新授权（纯 C++ 抓取）+ cookies 自包含；
- **v1.0.4**（2026-10-10）：悬浮窗插件菜单修复；M/K 显示 + 300M 上限 + 3 秒采集档；守卫登录态保活与失效告警；
- **v1.0.3**（2026-10-09）：走马灯广告位 + 更新源移除 GitHub；
- **v1.0.2**（2026-10-09）：检查更新接入 Gitee 更新源；
- **v1.0.1**（2026-10-09）：解压即用（相对路径）；
- **v1.0.0**（2026-10-09）：首个正式版。
