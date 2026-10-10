# dfm-asset-guard · v1.0.4

> 三角洲行动资产监控与自动冻结系统 —— Windows x64 预编译包（2026-10-10）。
> 仓库：https://gitee.com/mhwpub/dfm-asset-guard ｜ https://github.com/leporiinflabless-maker/dfm-asset-guard

## v1.0.4 更新

- **DFMMonitor**：悬浮窗右键菜单新增「**三角洲资产监控**」子菜单（与任务栏一致，含暂停/刷新/冻结/解冻/测试邮件等命令）；修复隐藏条目拦截点击判定导致插件菜单与选项入口不稳定的问题；
- **DeltaGuard 插件**：
  - 采集频率最低可设 **3 秒**（3-600）；
  - 总资产/哈夫币输入框右侧**实时显示 M/K 单位**（如 5M、2.64M、500K）；
  - 阈值**上限 300M**（输入自动钳制，滑块支持 0~300M，输入限 9 位数字）；
- **dfm-guard 守卫**：
  - 游戏安全中心**登录态自动保活**（每 4 分钟滚动刷新 token，避免长时间空闲掉线）；
  - 登录态失效时**邮件告警**（最多 1 小时一封）；
  - 执行冻结/解冻前**自动重载最新凭据**；
  - 采集频率支持 **3 秒**档。

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
| `DFMMonitor\DFMMonitor.exe` | 1,904,128 B | `642286645594beaf569a3bb616b212bdc16dff375142a24348e9dfd59f9a12e6` |
| `DFMMonitor\plugins\DeltaGuard.dll` | 67,072 B | `5a26eef96a95b566c46eabcf868ca982bd4d868b32eec47a4f094681fc432823` |
| `dfm-guard\dfm-guard.exe` | 381,952 B | `2732c3a16617c6dc9ea5df38e9b346d501f42ea324d20ce9425610405fec9535` |

## 使用说明

### 1. DFMMonitor（监控面板）
- 解压到任意目录（**不要放在系统 Temp 目录**），双击 `DFMMonitor.exe`；
- 悬浮窗显示 `资产 / 哈夫币 / 状态`，宽度随内容自动调整；
- **检查更新**：启动时自动检查（可关闭），或右键菜单 →「检查更新」；更新源为本项目 Gitee 仓库；
- 每 30 分钟播放 3 遍走马灯提示（单击窗口打开 https://mhw.pub）。

### 2. dfm-guard（守卫服务）
- 复制 `service_config.example.json` 为 `service_config.json`（与 exe 同目录）并填写 `email.server_token`、`email.to`；
- 可双击运行或命令行 `dfm-guard.exe run`；插件会自动拉起本服务；
- 邮件为服务器代发；游戏安全中心登录态由服务自动保活。

### 3. 组合使用
解压整包后：先启动 `DFMMonitor.exe`（插件会自动拉起 `dfm-guard.exe`），即可看到实时数据。

## 版本

- **v1.0.4**（2026-10-10）：悬浮窗插件菜单修复；M/K 显示 + 300M 上限 + 3 秒采集档；守卫登录态保活与失效告警；
- **v1.0.3**（2026-10-09）：走马灯广告位 + 更新源移除 GitHub；
- **v1.0.2**（2026-10-09）：检查更新接入 Gitee 更新源；
- **v1.0.1**（2026-10-09）：解压即用（相对路径）；
- **v1.0.0**（2026-10-09）：首个正式版。
