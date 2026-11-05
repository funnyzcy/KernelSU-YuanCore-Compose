"""Static verification for the YuanCore Compose theme branch.

Run from anywhere:  python tools/yuancore_compose_verify.py

This does NOT compile Kotlin (no JDK 21 / Gradle / NDK in the authoring env).
It verifies source-level integrity, wiring, resource closure, and that the
authorization chain is byte-identical to the upstream commit.
"""
import io
import pathlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
M = ROOT / "manager/app/src/main/java/me/weishu/kernelsu"
RES = ROOT / "manager/app/src/main/res"
YC = M / "ui/theme/yuancore"

# Always compare against the upstream commit, never against HEAD: the checks
# must keep proving "authorization chain untouched" after the branch is committed.
BASE = "28db74f6f4692e97006ce9ebd8b19b9cc614b5b7"

PASS = 0
FAIL = 0


def check(ok, label, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  PASS {label:<58s} {detail}")
    else:
        FAIL += 1
        print(f"  FAIL {label:<58s} {detail}")


def text(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def git(*args):
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()


def balanced(src):
    """Crude delimiter balance after stripping comments and string literals."""
    s = re.sub(r"/\*[\s\S]*?\*/", "", src)
    s = re.sub(r"//[^\n]*", "", s)
    s = re.sub(r'"""[\s\S]*?"""', '""', s)
    s = re.sub(r'"(?:\\.|[^"\\])*"', '""', s)
    s = re.sub(r"'(?:\\.|[^'\\])*'", "''", s)
    stack = []
    pairs = {")": "(", "]": "[", "}": "{"}
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack


print("=" * 78)
print("  YuanCore Compose theme branch verification")
print("=" * 78)

# --- provenance ------------------------------------------------------------
origin = git("remote", "get-url", "origin")
check(origin == "https://github.com/tiann/KernelSU.git",
      "origin is the official GitHub repository", origin)
check(git("rev-parse", "--verify", BASE).startswith("28db74f6"),
      "upstream baseline commit pinned", BASE[:12])
check(git("rev-parse", "--abbrev-ref", "HEAD") == "yuancore",
      "branch == yuancore", git("rev-parse", "--abbrev-ref", "HEAD"))

# --- theme layer files -----------------------------------------------------
files = ["YuanCoreTokens.kt", "YuanCoreColorScheme.kt", "YuanCoreTheme.kt",
         "YuanCoreOrb.kt", "YuanCoreHeroCard.kt"]
for f in files:
    p = YC / f
    check(p.is_file(), "theme layer: " + f)
    if p.is_file():
        src = text(p)
        check(src.startswith("package me.weishu.kernelsu.ui.theme.yuancore"),
              "  package declaration: " + f)
        check(balanced(src), "  delimiters balanced: " + f)

tokens = text(YC / "YuanCoreTokens.kt")
for sym in ["object YuanCorePalette", "val Indigo", "val Violet", "val Orchid",
            "val Teal", "val Ink", "val Paper", "val SeedArgb", "val Flow",
            "val YuanCoreShapes", "val YuanCoreNumeric", "object YuanCoreMotion"]:
    check(sym in tokens, "tokens define " + sym)
check("FontFamily.Monospace" in tokens, "numeric face is monospaced")
check("RoundedCornerShape(28.dp)" in tokens, "hero radius is 28dp")

scheme = text(YC / "YuanCoreColorScheme.kt")
check("fun ColorScheme.yuanCore(" in scheme, "ColorScheme.yuanCore extension")
check("copy(" in scheme and "surfaceTint" in scheme, "surfaces applied via copy")
check("primary =" not in scheme, "semantic primary left to the seed palette")

theme = text(YC / "YuanCoreTheme.kt")
check("staticCompositionLocalOf { false }" in theme, "theme defaults to OFF")
check("staticCompositionLocalOf { true }" in theme, "motion defaults to ON")
check("fun Typography.yuanCoreType()" in theme, "typography extension")

orb = text(YC / "YuanCoreOrb.kt")
for sym in ["rememberInfiniteTransition", "Canvas(", "rotate(", "drawArc(",
            "YuanCoreMotion.SPIN_MS", "LocalYuanCoreMotion"]:
    check(sym in orb, "orb uses " + sym.rstrip("( "))

hero = text(YC / "YuanCoreHeroCard.kt")
check("fun YuanCoreHeroCard(" in hero, "hero card composable")
check("isInDarkTheme()" in hero, "hero adapts to dark mode")
check("YuanCoreOrb(" in hero, "hero renders the orb")
check("ColorScheme" not in hero, "hero is shell-independent")

# --- wiring ----------------------------------------------------------------
t = text(M / "ui/theme/Theme.kt")
check("val yuanCoreEnabled: Boolean = false" in t, "AppSettings defaults to OFF")
check("repo.yuanCoreEnabled" in t, "ThemeController reads the setting")
check("CompositionLocalProvider(LocalYuanCoreEnabled provides" in t,
      "KernelSUTheme provides the composition local")
check(balanced(t), "Theme.kt delimiters balanced")

mt = text(M / "ui/theme/MaterialTheme.kt")
check("yuanCore -> YuanCorePalette.Seed" in mt, "Material seed is YuanCore")
check("it.yuanCore(darkTheme, amoledMode)" in mt, "Material surfaces overlaid")
check("else it" in mt, "OFF path keeps the upstream color scheme")
check("shapes = if (yuanCore) YuanCoreShapes else null" in mt,
      "Material shapes opt-in")
check("typography = if (yuanCore) Typography.yuanCoreType() else Typography" in mt,
      "OFF path keeps upstream Typography")
check(balanced(mt), "MaterialTheme.kt delimiters balanced")

mx = text(M / "ui/theme/MiuixTheme.kt")
check("appSettings.yuanCoreEnabled -> YuanCorePalette.Seed" in mx,
      "Miuix seed is YuanCore")
check(balanced(mx), "MiuixTheme.kt delimiters balanced")

repo_i = text(M / "data/repository/SettingsRepository.kt")
check("var yuanCoreEnabled: Boolean" in repo_i, "repository interface declares switch")
repo = text(M / "data/repository/SettingsRepositoryImpl.kt")
check('prefs.getBoolean("yuancore_theme", false)' in repo,
      "switch persisted, default OFF")
check('putBoolean("yuancore_theme", value)' in repo, "switch persisted on write")

state = text(M / "ui/screen/settings/SettingsUiState.kt")
check("val yuanCoreEnabled: Boolean = false" in state, "UI state defaults OFF")
check("val onSetYuanCoreEnabled: (Boolean) -> Unit" in state,
      "UI actions expose the setter")

vm = text(M / "ui/viewmodel/SettingsViewModel.kt")
check("val yuanCoreEnabled = repo.yuanCoreEnabled" in vm, "ViewModel loads switch")
check("yuanCoreEnabled = yuanCoreEnabled," in vm, "ViewModel publishes switch")
check("fun setYuanCoreEnabled(" in vm, "ViewModel exposes setter")
check(balanced(vm), "SettingsViewModel.kt delimiters balanced")

screen = text(M / "ui/screen/settings/SettingsScreen.kt")
check("onSetYuanCoreEnabled = viewModel::setYuanCoreEnabled" in screen,
      "SettingPager wires the action")

sm = text(M / "ui/screen/settings/SettingsMaterial.kt")
check("R.string.yuancore_theme" in sm and "SegmentedSwitchItem(" in sm,
      "Material settings shows the switch")
check("uiState.yuanCoreEnabled" in sm, "Material switch reads state")
check(balanced(sm), "SettingsMaterial.kt delimiters balanced")

smx = text(M / "ui/screen/settings/SettingsMiuix.kt")
check("R.string.yuancore_theme" in smx and "SwitchPreference(" in smx,
      "Miuix settings shows the switch")
check("uiState.yuanCoreEnabled" in smx, "Miuix switch reads state")
check(balanced(smx), "SettingsMiuix.kt delimiters balanced")

for name in ["HomeMaterial.kt", "HomeMiuix.kt"]:
    h = text(M / "ui/screen/home" / name)
    check("LocalYuanCoreEnabled.current" in h, name + " gates the hero card")
    check("YuanCoreHeroCard(" in h, name + " renders the hero card")
    check("import me.weishu.kernelsu.ui.theme.yuancore.YuanCoreHeroCard" in h,
          name + " imports the hero card")
    check("import me.weishu.kernelsu.ui.theme.yuancore.LocalYuanCoreEnabled" in h,
          name + " imports the composition local")
    # Whole-file delimiter scanning is unreliable on upstream Home screens
    # (string templates confuse the crude lexer). Check only the inserted
    # lines, which form a self-contained block.
    rel = "manager/app/src/main/java/me/weishu/kernelsu/ui/screen/home/" + name
    diff = git("diff", "-U0", BASE, "--", rel)
    added = "\n".join(l[1:] for l in diff.splitlines()
                      if l.startswith("+") and not l.startswith("+++"))
    check(balanced(added), name + " inserted block balanced")

# --- resources -------------------------------------------------------------
en = text(RES / "values/strings.xml")
zh = text(RES / "values-zh-rCN/strings.xml")
keys = ["yuancore_theme", "yuancore_theme_summary",
        "yuancore_trusted", "yuancore_untrusted"]
for k in keys:
    check(f'name="{k}"' in en, "en string: " + k)
    check(f'name="{k}"' in zh, "zh-rCN string: " + k)
check(">YuanCore theme<" in en, "default strings are English")
check("元核主题" in zh, "zh-rCN carries the translation")

for f in [RES / "values/strings.xml", RES / "values-zh-rCN/strings.xml"]:
    try:
        ET.parse(f)
        ok = True
    except Exception as e:
        ok = False
        print("   ", e)
    check(ok, "XML parses: " + str(f.relative_to(ROOT)))

refs = set()
for p in list(M.rglob("*.kt")) + list(RES.rglob("*.xml")):
    s = text(p)
    refs |= set(re.findall(r"R\.string\.(yuancore_[A-Za-z0-9_]+)", s))
    refs |= set(re.findall(r'@string/(yuancore_[A-Za-z0-9_]+)', s))
check(refs <= set(keys), "every yuancore string reference resolves",
      ", ".join(sorted(refs - set(keys))) or str(len(refs)) + " refs")

# --- hard boundaries -------------------------------------------------------
auth_markers = ("Natives", "jni", "ksud", "supercall", "allowlist",
                "SuperUser", "kernel/", "apk_sign", "throne_tracker")
changed_auth = [p for p in git("diff", "--name-only", BASE).splitlines()
                if any(m in p for m in auth_markers)]
check(not changed_auth, "authorization chain byte-identical to upstream",
      changed_auth[0] if changed_auth else "0 files")

identity = text(M.parents[5] / "build.gradle.kts")
check("me.weishu.kernelsu" in identity, "applicationId unchanged")
check("com.hunyuan" not in identity, "no custom package name")

all_changed = git("diff", "--name-only", BASE).splitlines()
untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
outside = [p for p in all_changed + untracked
           if not (p.startswith("manager/app/src/main/") or p.startswith("tools/"))]
check(not outside, "changes confined to app sources and tools",
      ", ".join(outside) or "0 files")

print("-" * 78)
print(f"  {PASS} passed, {FAIL} failed, {PASS + FAIL} checks")
print("=" * 78)
sys.exit(1 if FAIL else 0)
