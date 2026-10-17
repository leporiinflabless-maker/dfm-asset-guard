# -*- coding: utf-8 -*-
"""dfm 微信小程序后台启动器 —— 纯后台打开指定小程序并进入「我的」页面。

原理（2026-10-15 逆向验证）：
  注入微信主进程 Weixin.exe → wmpf_host_export_x64.dll
  → GetAppletManagerV3() (RVA 0x240F10) 取管理器实例
  → AppletManagerV3::LaunchApplet(mgr, appid_cstr, "", 0, NULL) (RVA 0x243200)
  → 内部走 LaunchAppletStandalone → 命令发给 WMPF 运行时
  → 运行时（若已死会自动重建）冷加载小程序并打开窗口

冷启动需要重试：运行时已死时，第一次调用只触发「重建运行时」，需再调用一次才真正拉起小程序。

「我的」页面：小程序窗口打开后，点击窗口底部 Tab 栏中的「我的」标签（默认开启，--no-mine 可跳过）。

用法：
  python dfm_wechat_open_applet.py                # 打开默认小程序（三角洲行动）并进入「我的」
  python dfm_wechat_open_applet.py --no-mine      # 只打开小程序
  python dfm_wechat_open_applet.py wxXXXX         # 指定 appid
  python dfm_wechat_open_applet.py --wait 20      # 每次尝试等待窗口/事件的秒数（默认 18）

输出示例：
  [ok] 已向微信 (pid=50060) 发送启动指令 appid=wx1c36464bbea2507a (第1次)
  [warn] 第1次尝试未打开（可能触发了运行时重建），重试...
  [ok] 第2次尝试：小程序窗口已出现 ✓ (hwnd=..., rect=...)
  [ok] 已点击「我的」Tab
  RESULT: OPENED appid=wx1c36464bbea2507a mine=1

依赖：pip 安装 frida（本机已装 frida 17.x）
维护：微信大版本升级后需重新核对 3 个 RVA（见 docs/wechat-applet-launcher.md）。
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import json
import sys
import time

try:
    import frida
except ImportError:
    print('RESULT: FAIL frida 未安装（pip install frida）')
    sys.exit(2)

DEFAULT_APPID = 'wx1c36464bbea2507a'  # 三角洲行动
DEFAULT_TITLE = '三角洲行动'
RVA_GETTER = 0x240F10                 # GetAppletManagerV3
RVA_LAUNCH = 0x243200                 # AppletManagerV3::LaunchApplet
RVA_EVENT = 0x243060                  # SendAppletEventNoCallback（事件观测）
MODULE = 'wmpf_host_export_x64.dll'

JS = r'''
const MOD = '%(module)s';
const base = Process.getModuleByName(MOD).base;

Interceptor.attach(base.add(%(off_event)s), {
  onEnter(args) {
    const b = args[1];
    let name = null;
    try {
      const x = b.add(0x17).readU8();
      if (x & 0x80) {
        const len = b.add(8).readU64().toNumber();
        name = b.readPointer().readUtf8String(Math.min(len | 0, 200));
      } else {
        name = b.readUtf8String(x & 0x7f);
      }
    } catch (e) {}
    if (name) send({ev: 'evt', name: name});
  }
});

function doLaunch(appid) {
  try {
    const g = new NativeFunction(base.add(%(off_getter)s), 'pointer', []);
    const mgr = g();
    const f = new NativeFunction(base.add(%(off_launch)s), 'void',
        ['pointer', 'pointer', 'pointer', 'size_t', 'pointer']);
    const a = Memory.allocUtf8String(appid);
    const cfg = Memory.allocUtf8String('');
    f(mgr, a, cfg, 0, ptr(0));
    send({ev: 'called', appid: appid});
    return 'ok';
  } catch (e) {
    send({ev: 'error', error: 'js: ' + e});
    return 'err';
  }
}

rpc.exports = {
  launch: function (appid) { return doLaunch(appid); }
};
send({ev: 'ready'});
'''


# ---------------------------------------------------------------- Win32 helpers
user32 = ctypes.WinDLL('user32', use_last_error=True)
user32.SetForegroundWindow.argtypes = [wt.HWND]
user32.BringWindowToTop.argtypes = [wt.HWND]
user32.ShowWindow.argtypes = [wt.HWND, ctypes.c_int]
user32.SwitchToThisWindow.argtypes = [wt.HWND, wt.BOOL]
user32.SetWindowPos.argtypes = [wt.HWND, wt.HWND, ctypes.c_int, ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_uint]
user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
user32.keybd_event.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_uint, ctypes.c_size_t]


def find_applet_window(title_substr: str):
    """枚举顶层可见窗口，返回 (hwnd, title, (l,t,r,b))；找不到返回 None。"""
    result = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def _enum(hwnd, lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        buf = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, buf, 256)
        t = buf.value
        if t and title_substr in t:
            r = wt.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(r))
            w = r.right - r.left
            h = r.bottom - r.top
            if w > 300 and h > 300:  # 排除小提示窗
                result.append((hwnd, t, (r.left, r.top, r.right, r.bottom)))
        return True

    user32.EnumWindows(_enum, 0)
    return result[0] if result else None


def click(x: int, y: int):
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.25)
    user32.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
    time.sleep(0.09)
    user32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP


def force_foreground(hwnd):
    """强制把目标窗口置前并恢复显示（绕过前台锁 + 处理 WeChatAppEx 的隐藏态）。
    返回是否成功成为前台窗口（失败时不要盲目点击，避免误点其他窗口）。"""
    user32.keybd_event(0x12, 0, 0, 0)   # Alt 解锁前台限制
    time.sleep(0.08)
    user32.keybd_event(0x12, 0, 2, 0)
    time.sleep(0.15)
    user32.ShowWindow(wt.HWND(hwnd), 9)  # SW_RESTORE
    time.sleep(0.25)
    try:
        user32.SwitchToThisWindow(wt.HWND(hwnd), True)
    except Exception:
        pass
    user32.BringWindowToTop(wt.HWND(hwnd))
    user32.SetForegroundWindow(wt.HWND(hwnd))
    user32.SetWindowPos(wt.HWND(hwnd), None, 0, 0, 0, 0,
                        0x0001 | 0x0002 | 0x0040)  # NOSIZE|NOMOVE|SHOWWINDOW
    time.sleep(0.6)
    try:
        return int(user32.GetForegroundWindow()) == int(hwnd)
    except Exception:
        return False


def click_mine_tab(hwnd, rect):
    """点击小程序窗口底部「我的」Tab。

    三角洲行动小程序底部 Tab 栏：爆破 | 工具 | 首页 | 攻略 | 我的
    「我的」位于右下角 —— 已按 430x788 窗口实测校准：相对 (0.860, 0.945)。
    """
    l, t, r, b = rect
    w = r - l
    h = b - t
    x = l + int(w * 0.860)
    y = t + int(h * 0.945)
    click(x, y)
    return (x, y)


# ---------------------------------------------------------------- main
def find_weixin_pids():
    dev = frida.get_local_device()
    return [p.pid for p in dev.enumerate_processes() if p.name.lower() == 'weixin.exe']


def main():
    argv = list(sys.argv[1:])
    wait_s = 18
    if '--wait' in argv:
        i = argv.index('--wait')
        try:
            wait_s = int(argv[i + 1]) if i + 1 < len(argv) else wait_s
        except Exception:
            pass
        if i + 1 < len(argv):
            del argv[i:i + 2]
        else:
            del argv[i:i + 1]
    do_mine = '--no-mine' not in argv
    if '--no-mine' in argv:
        argv.remove('--no-mine')
    title = DEFAULT_TITLE
    if '--title' in argv:
        i = argv.index('--title')
        if i + 1 < len(argv):
            title = argv[i + 1]
            del argv[i:i + 2]
    appid = argv[0] if argv else DEFAULT_APPID

    pids = find_weixin_pids()
    if not pids:
        print('RESULT: FAIL 微信未运行')
        sys.exit(3)

    js = JS % {'module': MODULE, 'off_getter': RVA_GETTER,
               'off_launch': RVA_LAUNCH, 'off_event': RVA_EVENT}
    last_err = ''
    for pid in pids:
        session = None
        try:
            session = frida.attach(pid)
        except Exception as e:
            last_err = str(e)
            continue

        opened = False
        called = False
        events = []
        err = None

        def on_message(msg, data):
            nonlocal opened, called, err
            if msg.get('type') == 'error':
                err = str(msg.get('description') or msg)[:300]
                return
            if msg.get('type') != 'send':
                return
            p = msg.get('payload') or {}
            ev = p.get('ev')
            if ev == 'evt':
                events.append(p.get('name'))
                if p.get('name') == 'OnAppletOpeningEvent':
                    opened = True
            elif ev == 'called':
                called = True
            elif ev == 'error':
                err = p.get('error')

        try:
            script = session.create_script(js)
            script.on('message', on_message)
            script.load()
        except Exception as e:
            last_err = str(e)
            try:
                session.detach()
            except Exception:
                pass
            continue

        # 等 script ready / 模块缺失错误
        t0 = time.time()
        while time.time() - t0 < 3 and not err and 'ready' not in [e for e in events]:
            time.sleep(0.1)
            if called:
                break
        if err:
            last_err = err
            try:
                session.detach()
            except Exception:
                pass
            continue

        # 最多 3 次尝试（冷启动第一次可能只触发运行时重建）
        win = None
        for attempt in range(1, 4):
            try:
                script.exports_sync.launch(appid)
            except Exception as e:
                last_err = str(e)
                break
            print('[ok] 已向微信 (pid=%s) 发送启动指令 appid=%s (第%d次)' % (pid, appid, attempt))
            per_deadline = time.time() + wait_s
            while time.time() < per_deadline and not opened:
                time.sleep(0.4)
                win = find_applet_window(title)
                if win:
                    break
            if opened or win:
                break
            print('[warn] 第%d次尝试未打开（可能触发了运行时重建），重试...' % attempt)
            time.sleep(1.5)

        if not win:
            win = find_applet_window(title)

        if win or opened:
            if opened:
                print('[ok] 捕获到 OnAppletOpeningEvent —— 小程序已开始加载')
            if events:
                print('[ok] 事件序列: ' + ', '.join(events[:6]))
            if win:
                print('[ok] 小程序窗口已出现 hwnd=%s title=%s rect=%s' % (win[0], win[1], win[2]))
                # 等待渲染稳定后点击「我的」
                time.sleep(3.5)
                clicked = False
                if do_mine:
                    win2 = find_applet_window(title) or win
                    if force_foreground(win2[0]):
                        pos = click_mine_tab(win2[0], win2[2])
                        print('[ok] 已点击「我的」Tab @%s' % (pos,))
                        clicked = True
                    else:
                        print('[warn] 小程序窗口未能置前，跳过「我的」点击（避免误点其他窗口）')
                    time.sleep(2.5)
                print('RESULT: OPENED appid=%s mine=%d' % (appid, 1 if clicked else 0))
            else:
                print('[warn] 未检测到小程序窗口（事件已触发，窗口可能短暂延迟）')
                print('RESULT: OPENED appid=%s mine=0' % appid)
            time.sleep(3)
            try:
                session.detach()
            except Exception:
                pass
            sys.exit(0)
        else:
            print('[fail] pid=%s 多次尝试后仍未打开: %s' % (pid, last_err or err or 'unknown'))
            try:
                session.detach()
            except Exception:
                pass
            continue

    print('RESULT: FAIL 无法注入/打开: %s' % last_err)
    sys.exit(4)


if __name__ == '__main__':
    main()
