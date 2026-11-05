# 生成 YuanCore 管理器 APK

这份文档说明的是「把 `yuancore` 分支真正编译成一个可安装的 KernelSU 管理器 APK」，
不是之前那个 WebView 展示壳，也不是主题补丁文件。

- 主题层源码：`manager/app/src/main/java/me/weishu/kernelsu/ui/theme/yuancore/`
- 构建流水线：`.github/workflows/yuancore-apk.yml`
- 打包脚本（上游自带）：`repack_apk.py`

## 0. 已验证的构建（2026-11-05）

本流水线已**真机云端跑通**，不是纸面方案：

| 项 | 值 |
| --- | --- |
| Run | `https://github.com/funnyzcy/KernelSU-YuanCore-Compose/actions/runs/41988591559` |
| Commit | `b7d0d718` |
| 结果 | 6 个 job 全 success（含 8 个 KMI 的 LKM、三架构 ksud、Gradle release、repack） |
| 产物 | `KernelSU-YuanCore-Manager-b7d0d718.apk`，14,055,070 字节 |
| APK SHA-256 | `b839bd2bfd0c4bc93d1228db3f326cd17bc8390d810092d32eab4ba8718f5dca` |
| 包名 / 版本 | `me.weishu.kernelsu` / versionCode 32723, versionName `b7d0d718` |
| 签名 DN | `CN=KernelSU YuanCore UNOFFICIAL, O=YuanCore, C=CN` |
| 证书 SHA-256 | `508afe5b9b2170815ebf7b8ae064566a0fa5ace5c59a541adbc6b898eceec115` |
| 内核参数 | `KSU_EXPECTED_SIZE=0x0337` · `KSU_EXPECTED_HASH=508afe5b…ecec115` · `KSU_PACKAGE_NAME=me.weishu.kernelsu` |

产物内含 `lib/{arm64-v8a,x86_64,riscv64}/libksud.so` 与 `libkernelsu.so`；
dex 中可检索到 `yuanCoreEnabled`、`yuancore_theme`、`YuanCoreSpin`、`YuanCoreBreath`
（R8 会混淆类名，因此看不到 `YuanCoreHeroCard` 原名属正常）。

**真实编译暴露并已修复的三个问题**（源码级校验发现不了，必须靠 CI）：

1. `ui/theme/Theme.kt` 多写了 `import androidx.compose.runtime.provides` —
   `provides` 是 `ProvidableCompositionLocal` 的成员中缀函数，不是顶层扩展；
2. PKCS12 keystore 被 AGP 的 apksign 插件按 JKS 读，报
   `Tag number over 30 is not supported`；
3. 用 `::add-mask::` 处理过的密钥经 job outputs 传到下游不可靠 —
   最终改为**用同一次 run 内的私有 artifact 传 keystore + 密码**，
   Gradle 只产出 unsigned release APK，由 `repack_apk.py` 统一签名。
   这也顺带消除了第 2 个问题的触发条件。

## 1. 为什么不在本机编译

本地工作区当前只有：

| 组件 | 本机 | 源码要求 |
| --- | --- | --- |
| JDK | 17 (Corretto) | **21** (`JavaVersion.VERSION_21`) |
| Gradle | 无 | **9.7.1** (`gradle-wrapper.properties`) |
| Android SDK | platform 35 / build-tools 35 | **compileSdk 37 / build-tools 37.0.0** |
| NDK | 无 | **r29** |
| Rust / cargo-ndk | 无 | 需要，用于交叉编译 `ksud` 三架构 |
| CMake / LKM / ksuinit | 无 | 需要，用于嵌入管理器的 native 载荷 |

`manager/app/build.gradle.kts` 使用 AGP 9.x + Compose Compiler + protobuf + JNI/CMake，
`manager/build.gradle.kts` 把 `androidCompileSdkVersion` 写成 37。缺任何一环都无法产出可用的管理器。
所以走 GitHub Actions 云端构建，这是上游自己也采用的唯一完整路径。

## 2. 一键构建

`yuancore-apk.yml` 是**自包含**的：它在 CI 里临时生成签名密钥，不要求你配置任何 repository secret。

1. 在 GitHub 仓库页面确认 **Settings → Actions → General → Allow all actions** 已开启
   （fork 仓库默认可能禁用 Actions，必须手动启用一次）。
2. 把 `yuancore` 分支推上去，或进入 **Actions → YuanCore Manager APK → Run workflow**。
3. 等待约 30–60 分钟。流水线依次执行：
   - `signing-key`：生成 RSA-2048 自签证书，并导出 `KSU_EXPECTED_SIZE` / `KSU_EXPECTED_HASH`；
   - `build-lkm`：用上面两个值编译各 KMI 的 `kernelsu.ko`（让自编内核信任这个 APK）；
   - `build-ksuinit` + `build-ksud`：`arm64-v8a` / `x86_64` / `riscv64` 三架构 ksud；
   - `build-manager`：JDK 21 + Gradle 9.7.1 `assembleRelease`，产出带 YuanCore Compose 主题层的 release APK；
   - `repack-manager`：`repack_apk.py` 注入 ksud、`zipalign`、用**同一把密钥**重签并校验。
4. 在 run 页面下载 artifact **`KernelSU-YuanCore-Manager`**，文件名形如
   `KernelSU-YuanCore-Manager-<short-sha>.apk`。

勾选 `create_release` 时还会额外建一个 `yuancore-<sha>` 的 Release 并附上 APK。

> 每次构建都会换一把新密钥（CI 结束即丢弃）。**升级安装必须用同一次构建的 APK  lineage**，
> 否则签名不一致会覆盖失败。若要长期固定签名，请自建 keystore 并改成 repository secrets。

## 3. 主题开关

YuanCore 是**可选主题层，本分支默认开启**，装上就能看到与官方不同的外观。
设置里的 `元核主题 / YuanCore theme`（键 `yuancore_theme`）可以随时关掉，关闭时界面与官方
`main` 完全一致；`MainActivityViewModel.observedKeys` 已包含该键，切换即时生效、无需重启。
开启后同时作用于 Material 与 Miuix 两套界面：

- `ColorScheme.yuanCore()`：玄青 / 宣白 双色板
- `YuanCoreShapes`：22–28dp 圆角
- `Typography.yuanCoreType()`：等宽数字字阶
- `YuanCoreHeroCard` / `YuanCoreOrb`：同心圆状态环 + 靛紫流光 `#4B56F5 → #8A55F0 → #B35AE8`

## 4. 装上去就能 root 吗 —— 不能，必须先解决内核信任

官方内核通过 `throne_tracker.c` + `apk_sign.c` 校验两件事：

1. 包名必须是 `KSU_PACKAGE_NAME`（默认 `me.weishu.kernelsu`）；
2. APK 的 v2 签名证书必须与内核里编译进去的 `KSU_EXPECTED_SIZE` / `KSU_EXPECTED_HASH` 一致。

本流水线产出的 APK **包名保持官方默认值**，但**证书是自签的**。因此：


- 已刷官方 KernelSU 内核的设备：安装后管理器能看到界面，但内核不会把它认作合法管理器，无法授权 su；
- 想真正当管理器用：用 CI 的 `signing-key` job 在 Step Summary 打印的
  `KSU_EXPECTED_SIZE=0x....` / `KSU_EXPECTED_HASH=....` 重新编译内核
  （`kernel/Kbuild` 中这两个变量是 `?=`，可在编译命令里覆盖）。

这也解释了为什么 `repack_apk.py` 只负责「注入 ksud + 对齐 + 重签」，它**不负责**、也无法负责内核信任链。

## 5. 包名与分发边界（重要）

本流水线沿用上游默认包名 `me.weishu.kernelsu`，因为改包名必须**三处同步**，
否则 ksud 与内核都不认这个管理器：

| 位置 | 怎么改 |
| --- | --- |
| APK | `./gradlew assembleRelease -PKSU_PACKAGE_NAME=<你的包名>` |
| ksud | 编译时 `export KSU_PACKAGE_NAME=<你的包名>`（`.github/workflows/ksud.yml` 的 Build ksud 步骤） |
| 内核 / LKM | `.github/workflows/build-lkm.yml` 的 `package_name` input，或 `kernel/Kbuild` 的 `KSU_PACKAGE_NAME` |

因为 `README-YuanCore.md` §3 明确要求**不要对外发布带官方包名的自签 APK**，
本流水线默认**不创建 Release**（`create_release` 默认 false），只产出 Actions artifact：
请把它当作**个人自测构建**使用，不要转发、不要上传到应用市场或第三方下载站。
确需公开发布时，先按上表三处改成自己的包名，用自己的固定 keystore，
并在发布说明里写明 UNOFFICIAL + 对应源码 commit。

## 6. 合规提醒

- 这是 **UNOFFICIAL** 分支，与 KernelSU 官方无关，不提供任何担保。
- 仓库根 `LICENSE` (GPLv3) 与 `kernel/LICENSE` (GPLv2) 必须原样保留，`NOTICE` 需随 APK 分发。
- 不要把 keystore、私钥、`gradle.properties` 里的密码、官方 APK 解出的 dex/so 提交进仓库。
- 本说明不是法律意见。
