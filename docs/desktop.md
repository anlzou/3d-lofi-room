# Windows 本地版

Windows x64 便携包将网页、模型、贴图、原创音乐与 Electron 运行时一起内置，不使用 Vite 或 localhost 开发服务器。双击启动；音乐仍需手动开启。免安装 EXE 解压到临时目录运行，设置保存在当前 Windows 用户的应用数据目录，关闭后保留。打包产物名为 `3D-Lofi-Room-Portable-<版本>.exe`（`package.json` 的 `build.portable.artifactName`）。

使用 `room://home/` 受限内部协议读取应用内资源，渲染进程关闭 Node 集成、开启沙箱与上下文隔离；拒绝新窗口、外部导航和权限请求。参照 [Electron 上下文隔离](https://www.electronjs.org/docs/latest/tutorial/context-isolation) 与 [electron-builder 便携目标](https://www.electron.build/docs/targets/)。

```powershell
pnpm install
pnpm package:win
```

当前机器首次自动下载较慢，使用镜像取得运行时后，已与 npm Electron 包内官方 SHA256 清单核对一致。已下载的运行时也可复用：

```powershell
pnpm exec electron-builder --win portable --x64 --config.electronDist=node_modules/electron/dist
```

源码调试可运行 `pnpm desktop`（Electron 44 会在首次运行时按需下载运行时二进制）。`pnpm exec electron . --smoke-test` 检查离线页面就绪、内置 WAV 存在、渲染控制台错误，并保存 `release-check/desktop.png`。本机启动成功不等于所有朋友电脑均已验收。

当前分享包未做代码签名，Windows 可能提示未知发布者；不宣称正式签名发行。Mac/Linux 安装包未构建。项目仍有天气专属细节、猫行为、DVD/VCR 和长期稳定性等待办，便携包属于可体验开发版。
