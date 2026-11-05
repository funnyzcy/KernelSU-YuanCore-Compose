# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 YuanCore contributors
"""Hygiene check before publishing this fork to a public Git remote.

Run:  python tools/yuancore_prepublish_check.py

Verifies licence/attribution files, that no signing material or prebuilt
official binaries can be committed, that new sources carry SPDX headers, and
that the root-authorisation chain still matches the upstream baseline.
Advisory notes (remote layout, shallow clone, dirty worktree) are printed but
do not fail the check.
"""
import io
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = "28db74f6f4692e97006ce9ebd8b19b9cc614b5b7"
YC = ROOT / "manager/app/src/main/java/me/weishu/kernelsu/ui/theme/yuancore"

PASS = 0
FAIL = 0


def check(ok, label, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  PASS {label:<56s} {detail}")
    else:
        FAIL += 1
        print(f"  FAIL {label:<56s} {detail}")


def note(msg):
    print(f"  NOTE {msg}")


def text(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def git(*args):
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()


print("=" * 76)
print("  YuanCore pre-publication hygiene check")
print("=" * 76)

# --- licences and attribution ----------------------------------------------
root_lic = text(ROOT / "LICENSE")
kernel_lic = text(ROOT / "kernel" / "LICENSE")
check("Version 3" in root_lic and "GNU GENERAL PUBLIC LICENSE" in root_lic,
      "root LICENSE is upstream GPLv3")
check("Version 2" in kernel_lic and "GNU GENERAL PUBLIC LICENSE" in kernel_lic,
      "kernel/LICENSE is upstream GPLv2")
check((ROOT / "NOTICE").is_file(), "NOTICE present")
notice = text(ROOT / "NOTICE") if (ROOT / "NOTICE").is_file() else ""
check("UNOFFICIAL" in notice, "NOTICE declares unofficial status")
check(BASE[:12] in notice, "NOTICE pins the upstream baseline commit")
check("kernel/LICENSE" in notice and "LICENSE" in notice,
      "NOTICE documents the dual-licence structure")
readme = text(ROOT / "README-YuanCore.md") if (ROOT / "README-YuanCore.md").is_file() else ""
check("UNOFFICIAL" in readme, "README declares unofficial status")
check("GPLv3" in readme and "GPLv2" in readme, "README explains both licences")
check("keystore" in readme.lower() and "Corresponding Source" in readme,
      "README covers secrets and GPL source obligation")

# --- ignore rules -----------------------------------------------------------
ignore = text(ROOT / ".gitignore")
for pattern in ["*.keystore", "*.jks", "*.p12", "*.env", "sign.properties",
                "*.apk", "*.dex", "*.so", "repack-config.json"]:
    check(pattern in ignore, ".gitignore excludes " + pattern)

# --- files that would be published -----------------------------------------
tracked = set(git("ls-files").splitlines())
untracked = set(git("ls-files", "--others", "--exclude-standard").splitlines())
candidates = sorted(tracked | untracked)

SECRET_SUFFIX = (".keystore", ".jks", ".p12", ".pk8", ".pem", ".key",
                 ".apk", ".apks", ".aab", ".dex", ".so")
bad_binary = [p for p in candidates if p.lower().endswith(SECRET_SUFFIX)]
check(not bad_binary, "no keys / APKs / extracted binaries staged",
      bad_binary[0] if bad_binary else "0 files")

BAD_NAMES = re.compile(
    r"(^|/)(sign\.properties|keystore\.properties|local\.properties|"
    r"repack-config\.json|\.env|yuancore\.env|.*\.keystore)$", re.I)
bad_names = [p for p in candidates if BAD_NAMES.search(p)]
check(not bad_names, "no signing/env config among publishable files",
      bad_names[0] if bad_names else "0 files")

SCAN_EXT = (".kt", ".kts", ".py", ".sh", ".ps1", ".md", ".xml", ".json",
            ".properties", ".toml", ".yml", ".yaml", ".c", ".h", ".rs", ".txt")
# Assembled at runtime so this file does not contain a literal marker and trip
# its own scan (the scan still covers this file).
PRIVATE_MARKERS = tuple(
    "-----BEGIN " + label + "PRIVATE KEY-----"
    for label in ("RSA ", "", "EC ", "OPENSSH ")
)
PW_ASSIGN = re.compile(
    r"^\s*(?:KEYSTORE_PASSWORD|KEY_PASSWORD|STOREPASS|KEYPASS|"
    r"STORE_PASSWORD|PASSWORD)\s*[:=]\s*(\S+)", re.I | re.M)


def plaintext_secret(value):
    """Only a literal-looking value is a leak; $VAR / ${{ secrets.* }} /
    $(cmd) references in upstream CI are not."""
    v = value.strip().strip("'\"")
    if not v or v.startswith("#"):
        return False
    return not any(c in v for c in "$`({")


leaks = []
for rel in candidates:
    if ".example." in rel or rel.lower().endswith(SECRET_SUFFIX):
        continue
    f = ROOT / rel
    if not f.is_file() or not rel.lower().endswith(SCAN_EXT):
        continue
    try:
        s = text(f)
    except OSError:
        continue
    if any(m in s for m in PRIVATE_MARKERS):
        leaks.append(rel + " (private key block)")
    elif any(plaintext_secret(m.group(1)) for m in PW_ASSIGN.finditer(s)):
        leaks.append(rel + " (non-empty password)")
check(not leaks, "no embedded private keys / passwords in text files",
      leaks[0] if leaks else "0 findings")

# --- new sources carry licence headers -------------------------------------
kt_files = sorted(YC.glob("*.kt"))
check(len(kt_files) >= 5, "YuanCore Compose layer file count", str(len(kt_files)))
for f in kt_files:
    first = text(f).splitlines()[0] if f.stat().st_size else ""
    check(first.startswith("// SPDX-License-Identifier: GPL-3.0-or-later"),
          "SPDX header: " + f.name)

# --- hard boundary ----------------------------------------------------------
AUTH = ("Natives", "jni", "ksud", "supercall", "allowlist",
        "SuperUser", "kernel/", "apk_sign", "throne_tracker")
changed = [p for p in git("diff", "--name-only", BASE).splitlines()
           if any(m in p for m in AUTH)]
check(not changed, "authorisation chain matches upstream baseline",
      changed[0] if changed else "0 files")

identity = text(ROOT / "manager/app/build.gradle.kts")
check("me.weishu.kernelsu" in identity and "com.hunyuan" not in identity,
      "applicationId stays upstream original")

# --- advisory ---------------------------------------------------------------
origins = git("remote", "get-url", "origin")
if "tiann/KernelSU" in origins:
    note("origin still points at upstream; run yuancore_publish.sh or set-url first")
shallow = (ROOT / ".git/shallow").is_file()
if shallow:
    note("shallow clone: keep the upstream remote and pinned SHA in NOTICE")
dirty = git("status", "--porcelain")
if dirty:
    note(f"worktree has {len(dirty.splitlines())} uncommitted entries; commit them before pushing")

print("-" * 76)
print(f"  {PASS} passed, {FAIL} failed, {PASS + FAIL} checks")
print("=" * 76)
print("  This is a hygiene check, not legal advice.")
sys.exit(1 if FAIL else 0)
