# -*- coding: utf-8 -*-
"""dfm 微信「腾讯游戏安全中心·自助服务」后台打开器（非模拟点击）。

原理（2026-10-18 逆向验证）：
  注入微信主进程 Weixin.exe → wmpf_host_export_x64.dll
  → GetBrowsingService()（导出，RVA 0xCC890）取浏览服务
  → QueryInterface("IWeChatBrowserManager") 取浏览器管理器（vtable 0x4E0690）
  → AddTab(mgr, type=0, url, len, params, len)（vtable 槽 3 / RVA 0x23EBE0）
  → 在微信内置浏览器中打开网页（与点击服务号菜单等价，但无需任何鼠标/键盘模拟）

默认 URL = 「腾讯游戏安全中心」服务号「自助服务」菜单的 OAuth 地址：
  （从微信进程内存的 MMBizMenu 配置中提取；appid=wx9206e762eb33a598）
  打开后微信自动完成 snsapi_base 授权 → 安全中心页面重新登录
  → dfm-authcap 捕获新的 cookies 写回 cookies.json。

用法：
  python dfm_wechat_open_gamesafe.py                # 打开「自助服务」
  python dfm_wechat_open_gamesafe.py <url>          # 打开指定 URL
  python dfm_wechat_open_gamesafe.py --type 0       # AddTab 类型（默认 0）
  python dfm_wechat_open_gamesafe.py --params '{"add_tab_params":{}}'
  python dfm_wechat_open_gamesafe.py --wait 2       # 调用后等待秒数

输出：
  [ok] 已定位微信主进程 (pid=49868)
  [ok] 已调用 IWeChatBrowserManager::AddTab type=0
  RESULT: OPENED url=...
  （失败：RESULT: FAIL <原因>）

依赖：pip install frida（本机 17.x）。维护：微信升级后需重核 3 个 RVA（见 docs/wechat-applet-launcher.md）。
"""
from __future__ import annotations

import json
import sys
import time

try:
    import frida
except ImportError:
    print('RESULT: FAIL frida 未安装（pip install frida）')
    sys.exit(2)

MODULE = 'wmpf_host_export_x64.dll'
RVA_GET_BROWSING_SERVICE = 0xCC890   # 导出 GetBrowsingService（jmp 0x1B20B0）
RVA_QI = 0x1B8150                    # wmpf BrowsingService::QueryInterface（vtable 槽 0）
RVA_ADD_TAB = 0x23EBE0               # IWeChatBrowserManager::AddTab（vtable 槽 3）

DEFAULT_URL = (
    'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx9206e762eb33a598'
    '&redirect_uri=https%3A//wx.gamesafe.qq.com/static/proxy/main-new/index.html'
    '&response_type=code&scope=snsapi_base&state=123#wechat_redirect'
)
DEFAULT_PARAMS = '{"add_tab_params":{}}'

JS = r'''
const MOD = '%(module)s';
let base;
try { base = Process.getModuleByName(MOD).base; } catch (e) {
  send({ev: 'no_module', err: String(e)});
}
if (base) {
  const URL = %(url)s;
  const TYPE = %(type)d;
  const PARAMS = %(params)s;
  try {
    const getSvc = new NativeFunction(base.add(%(off_svc)s), 'pointer', []);
    const svc = getSvc();
    if (svc.isNull()) throw new Error('GetBrowsingService returned null');
    const qi = new NativeFunction(base.add(%(off_qi)s), 'int',
        ['pointer', 'pointer', 'pointer']);
    const out = Memory.alloc(8);
    out.writePointer(ptr(0));
    const hr = qi(svc, Memory.allocUtf8String('IWeChatBrowserManager'), out);
    const mgr = out.readPointer();
    if (hr !== 0 || mgr.isNull()) throw new Error('QueryInterface failed hr=' + hr);
    const vt = mgr.readPointer();
    const addTab = new NativeFunction(vt.add(0x18).readPointer(), 'void',
        ['pointer', 'int', 'pointer', 'size_t', 'pointer', 'size_t']);
    const u = Memory.allocUtf8String(URL);
    const p = Memory.allocUtf8String(PARAMS);
    addTab(mgr, TYPE, u, URL.length, p, PARAMS.length);
    send({ev: 'called', url: URL, type: TYPE});
  } catch (e) {
    send({ev: 'error', err: String(e)});
  }
}
'''


def parse_args(argv):
    url = DEFAULT_URL
    tab_type = 0
    params = DEFAULT_PARAMS
    wait_s = 2.0
    rest = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--type' and i + 1 < len(argv):
            tab_type = int(argv[i + 1]); i += 2; continue
        if a == '--params' and i + 1 < len(argv):
            params = argv[i + 1]; i += 2; continue
        if a == '--wait' and i + 1 < len(argv):
            wait_s = float(argv[i + 1]); i += 2; continue
        if not a.startswith('-'):
            rest.append(a)
        i += 1
    if rest:
        url = rest[0]
    return url, tab_type, params, wait_s


def find_weixin_pids():
    dev = frida.get_local_device()
    return [p.pid for p in dev.enumerate_processes() if p.name.lower() == 'weixin.exe']


def main():
    url, tab_type, params, wait_s = parse_args(sys.argv[1:])
    pids = find_weixin_pids()
    if not pids:
        print('RESULT: FAIL 微信未运行')
        sys.exit(3)

    js = JS % {'module': MODULE, 'url': json.dumps(url), 'type': tab_type,
               'params': json.dumps(params), 'off_svc': RVA_GET_BROWSING_SERVICE,
               'off_qi': RVA_QI}

    for pid in pids:
        result = {'called': False, 'error': None, 'no_module': False}
        session = None
        try:
            session = frida.attach(pid)
            script = session.create_script(js)

            def on_message(msg, data):
                if msg.get('type') == 'error':
                    result['error'] = str(msg.get('description') or msg)[:300]
                    return
                p = msg.get('payload') or {}
                ev = p.get('ev')
                if ev == 'called':
                    result['called'] = True
                elif ev == 'error':
                    result['error'] = p.get('err')
                elif ev == 'no_module':
                    result['no_module'] = True

            script.on('message', on_message)
            script.load()
            deadline = time.time() + 8
            while time.time() < deadline and not result['called'] and not result['error'] \
                    and not result['no_module']:
                time.sleep(0.1)
        except Exception as e:
            result['error'] = str(e)
        finally:
            try:
                if session:
                    session.detach()
            except Exception:
                pass
        if result['no_module']:
            continue  # 不是加载 WMPF 宿主的主进程
        if result['called']:
            print('[ok] 已定位微信主进程 (pid=%s)' % pid)
            print('[ok] 已调用 IWeChatBrowserManager::AddTab type=%d' % tab_type)
            print('RESULT: OPENED url=%s' % url)
            time.sleep(max(0.0, wait_s))
            sys.exit(0)
        print('[warn] pid=%s 调用失败: %s' % (pid, result['error']))
    print('RESULT: FAIL 未能调用 AddTab（%s）' % (result['error'] or '找不到 WMPF 宿主进程'))
    sys.exit(4)


if __name__ == '__main__':
    main()
