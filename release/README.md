# dfm-asset-guard · 编译产物（release）

> 三角洲行动资产监控与自动冻结系统 —— 预编译文件（Windows x64）。
> 源码工程按模块维护；此目录仅存放最新构建产物，便于直接部署。

## 文件清单

| 文件 | 大小 | 构建时间 | 说明 |
|---|---|---|---|
| `DFMMonitor.exe` | 1,907,712 B | 2026-10-09 18:15 | 定制版三角洲监控面板（TrafficMonitor 改名版；含插件数据展示 + 悬浮窗宽度自适应） |
| `DeltaGuard.dll` | 59,904 B | 2026-10-09 17:37 | TrafficMonitor 插件（三角洲资产监控：资产/哈夫币/状态显示 + 右键菜单） |
| `dfm-guard.exe` | 376,320 B | 2026-10-09 17:37 | 守卫服务（纯 VC++：采集/规则/邮件服务器代发/冻结执行/状态桥） |

## SHA256 校验

```
bfade8dee55038a5166f3c19025b45dd9fa21b8d1762734248ed60be81550e1a  DFMMonitor.exe
93244d8ff46438c35b14254ad99e53b549085f4727e00433c0542bfd933b696c  DeltaGuard.dll
ebbcc45c36d21b692d9c259861e6983ff534425ba9d226f37dc6e5d8b301952e  dfm-guard.exe
```

## 部署方式

1. **DFMMonitor.exe**（定制版 TrafficMonitor）
   - 解压到任意目录，与 `skins/`、`language/`、`plugins/` 同目录运行；
   - `plugins\DeltaGuard.dll` 放入插件目录即加载“三角洲资产监控”面板；
   - 配置保存在同目录 `config.ini`（便携模式）。
2. **DeltaGuard.dll**（TrafficMonitor 插件）
   - 放入 DFMMonitor（或官方 TrafficMonitor）的 `plugins\` 目录，重启宿主生效。
3. **dfm-guard.exe**（守卫服务，纯 VC++）
   - 默认读取 `..\service\service_config.json` 服务配置（或 `--service-config PATH`）；
   - 常用命令：`dfm-guard.exe run`（常驻监控）/ `once`（单次采集）/ `status` / `test-email`；
   - 邮件通知为**服务器代发**：配置 `email.mode=server` + `server_url` + `server_token`，
     收件邮箱在 `email.to` 指定（由服务器 SMTP 统一发出，本地无需授权码）。

## 备注

- 本目录内容由 `dfm-asset-guard` 工作区的构建输出同步而来；
- DFMMonitor 为定制构建（已去除流量/硬件/系统监控，界面改名 DFMMonitor，菜单精简）。
