# 元核主题层 · YuanCore for KernelSU

> **非官方分支 / UNOFFICIAL FORK**
> 本项目是 [tiann/KernelSU](https://github.com/tiann/KernelSU) 的下游派生版本，
> 基线提交 `28db74f6f4692e97006ce9ebd8b19b9cc614b5b7`。与 KernelSU 官方项目
> **无隶属、无背书、无官方签名关系**。"KernelSU" 名称与标识归原权利人所有，
> 此处仅用于指明上游来源。完整归属声明见 [NOTICE](NOTICE)。

English summary: an unofficial KernelSU fork adding an **optional, enabled-by-default**
Compose theme layer. With the switch off, upstream appearance and behaviour are
byte-identical. No authorisation code is touched.

---

## 1. 这个分支做了什么

把「元核 YuanCore」视觉语言重写为一套独立的 Compose 主题层：玄青/宣白表面、
混元靛紫种子色、28dp 圆角、等宽数字、会旋转呼吸的同心圆状态核、首页 Hero 卡。

```
manager/app/src/main/java/me/weishu/kernelsu/ui/theme/yuancore/
├── YuanCoreTokens.kt       色板 / Shapes / 字阶 / 动效常量（纯数据）
├── YuanCoreColorScheme.kt  只覆盖中性表面，语义色交给种子生成
├── YuanCoreTheme.kt        LocalYuanCoreEnabled（兜底 false）+ 字阶扩展
├── YuanCoreOrb.kt          同心圆 Canvas 动画
└── YuanCoreHeroCard.kt     首页状态卡，不依赖任一套主题的 ColorScheme
```

开关链路：两套设置页 → `SettingsViewModel` → `SettingsRepository`（键
`yuancore_theme`）→ `AppSettings` → `CompositionLocalProvider` → 主题与两个首页。
Material 注入种子/表面/形状/字阶，Miuix 只注入种子（其表面系统自管）。

**本分支默认开启主题**（`getBoolean("yuancore_theme", true)`），装上即呈现元核外观；
到设置里关掉「元核主题」即刻回到官方外观。`MainActivityViewModel.observedKeys`
包含该键，因此切换开关会即时重组界面，无需重启 App。

**未改动**：`applicationId`、签名配置、launcher/splash、内核 `Kbuild` 变量、
`Natives.kt`、JNI、`ksud`、`supercall`、`allowlist`、超级用户逻辑、模块安装、
`kernel/`。可用 `python tools/yuancore_compose_verify.py` 复验这条边界。

## 2. 构建

需要 JDK 21、Gradle 9.7.1 / AGP 9.4.1、compileSdk 37、NDK 29、Rust 工具链。
本分支按官方流程构建，无额外步骤。

**云端一键出 APK**：`.github/workflows/yuancore-apk.yml` 在 `yuancore` 分支 push 或手动
触发时，用 CI 临时生成的密钥完成 Gradle 构建 + ksud 注入 + 重签，产出
`KernelSU-YuanCore-Manager-<sha>.apk` artifact（无需配置任何 secret）。
完整步骤、内核信任链参数与分发边界见 [docs/YUANCORE-APK.md](docs/YUANCORE-APK.md)。
本机（JDK 17 / SDK 35）不具备完整工具链，无法本地编译管理器。

```bash
./gradlew :app:assembleRelease        # 在 manager/ 目录下
```

也可以不 fork 整个仓库，只把主题补丁打到官方源码上：

```bash
cd KernelSU-main
git apply KernelSU-YuanCore-Compose-theme.patch
```

首次启动后到 **设置 → 外观** 打开 "YuanCore theme / 元核主题"。

> 作者环境只有 JDK 17 / build-tools r35，**未做全量 Gradle 编译与真机实跑**，
> 结论来自源码级校验与 Material3 API 签名核对。

## 3. 开源与许可证（重点）

上游是**双许可证结构**，分发时必须原样保留两份文件：

| 路径 | 许可证 | 覆盖范围 |
|---|---|---|
| `LICENSE` | **GPLv3** | Manager、ksud、userspace、scripts、JS、docs |
| `kernel/LICENSE` | **GPLv2** | 内核侧代码（源码带 `GPL-2.0-only` SPDX、`MODULE_LICENSE("GPL")`） |

GPLv2-only 与 GPLv3 互不兼容，二者作为**独立组件**并存，与上游组织方式一致。
**不要把整个仓库统一标注为某一个版本，也不要删除/合并任一 LICENSE。**

据此，把这套代码开源到自己的 GitHub 是允许的，但需要履行：

1. **保留**两份 LICENSE 全文、所有原始版权与许可声明；
2. **标注修改**：说明改了什么、改动日期（本仓库用 `NOTICE` + 本次提交信息完成）；
3. **同一许可证**：以 GPLv3（用户态）/ GPLv2（内核侧）继续授权整个派生作品，
   不得附加额外限制、不得改成 MIT/Apache 或闭源；
4. **提供 Corresponding Source**：公开仓库本身即完整源码；保留 upstream remote
   与基线 commit SHA，便于取得上游完整历史；
5. **不提供担保**（GPL §15/§16），并保留免责声明；
6. 若分发 **APK/二进制**：必须随附对应源码或有效的书面获取途径，
   且不能用官方包名冒充官方构建。

新增的主题层与工具脚本统一以 `GPL-3.0-or-later`（文件头 SPDX 标注）提供，
与 Manager 模块保持一致，避免双重许可冲突。若只想让独立项目复用设计 token，
需自行评估将其拆为独立作品的许可可行性，必要时咨询法务。

**商标与命名**：README、仓库描述、Release 说明中请明确 "UNOFFICIAL / 非官方"；
不要使用官方图标、官方名称作为主品牌，也不要发布带官方包名
`me.weishu.kernelsu` 的自签 APK（签名不同，系统无法覆盖安装，也易被误认为官方版）。

## 4. 绝对不要提交的东西

`.gitignore` 已加固，推送前请再跑一次自检：

- 任何 `*.keystore` / `*.jks` / `*.p12` / `*.pk8` / 私钥 / 证书密码；
- `*.env`、`yuancore.env`、`manager/sign.properties`、`local.properties`、
  `repack-config.json`（含签名口令）；
- 自签 APK / AAB、以及从官方 APK 解出的 `classes.dex`、`libksud.so`、
  `libkernelsu.so` 等编译产物（体积大、易造成归属混淆）；
- 本地工具链（JDK、Android SDK、Gradle 缓存）与反汇编中间文件。

```bash
python tools/yuancore_prepublish_check.py       # 发布前自检
bash tools/yuancore_publish.sh --dry-run <你的仓库 URL>
```

## 5. 与上游同步

```bash
git remote -v                       # upstream -> 官方, origin -> 你的 fork
git fetch upstream main
git rebase upstream/main            # 或 merge，冲突集中在主题接线点
python tools/yuancore_compose_verify.py
```

## 6. 能力边界（别误会这个主题）

这是**纯视觉层**。KernelSU 的 root 授信由内核 `throne_tracker.c` 依据
「包名 + v2 签名证书 SHA-256」判定，官方内核只信任官方证书。自签管理器在
官方内核下拿不到授信，本主题不改变这一点，也不试图绕过它。

想让所有 KernelSU 用户免动内核用上元核，唯一路径是把这个**可选主题**提给上游、
由官方签名发布；或者自己编译内核并覆盖 `KSU_PACKAGE_NAME` /
`KSU_EXPECTED_SIZE` / `KSU_EXPECTED_HASH`。

KernelSU 是 GPL 项目，root 工具本身合法开源；但刷机与内核编译有变砖风险，
本项目不提供任何担保。
