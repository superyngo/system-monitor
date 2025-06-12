#!/usr/bin/env python3
"""
版本發布工具
用於自動更新版本號並建立 Git tag
"""

import re
import subprocess
import sys
from pathlib import Path


def get_current_version():
    """從 pyproject.toml 讀取當前版本"""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ 找不到 pyproject.toml 檔案")
        return None

    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if match:
        return match.group(1)
    return None


def update_version(new_version):
    """更新 pyproject.toml 中的版本號"""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text(encoding="utf-8")

    # 更新版本號
    new_content = re.sub(
        r'version\s*=\s*"[^"]+"', f'version = "{new_version}"', content
    )

    pyproject_path.write_text(new_content, encoding="utf-8")
    print(f"✅ 已更新版本號為 {new_version}")


def run_command(cmd):
    """執行命令並返回結果"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            print(f"❌ 命令執行失敗: {cmd}")
            print(f"錯誤: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ 執行命令時發生錯誤: {e}")
        return False


def create_release(version, message=None):
    """建立 Git tag 和推送"""
    tag_name = f"v{version}"  # 檢查是否有未提交的變更
    result = subprocess.run(
        "git status --porcelain",
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.stdout.strip():
        print("📝 發現未提交的變更，正在提交...")
        if not run_command("git add ."):
            return False

        commit_msg = message or f"Release version {version}"
        if not run_command(f'git commit -m "{commit_msg}"'):
            return False

    # 建立 tag
    tag_msg = f"Release {tag_name}"
    if not run_command(f'git tag -a {tag_name} -m "{tag_msg}"'):
        return False

    print(f"✅ 已建立 tag: {tag_name}")

    # 推送到遠端
    if not run_command("git push origin main"):
        return False

    if not run_command(f"git push origin {tag_name}"):
        return False

    print(f"🚀 已推送 tag {tag_name} 到遠端，GitHub Actions 將自動開始建置和發布！")
    return True


def main():
    """主函數"""
    if len(sys.argv) < 2:
        print("使用方式:")
        print("  python release.py <new_version> [commit_message]")
        print("  例如: python release.py 0.2.0 'Add new monitoring features'")
        print()

        current = get_current_version()
        if current:
            print(f"目前版本: {current}")
        return

    new_version = sys.argv[1]
    commit_message = sys.argv[2] if len(sys.argv) > 2 else None

    # 驗證版本格式
    if not re.match(r"^\d+\.\d+\.\d+$", new_version):
        print("❌ 版本號格式錯誤，請使用 x.y.z 格式（例如: 1.0.0）")
        return

    current_version = get_current_version()
    if current_version:
        print(f"目前版本: {current_version}")
        print(f"新版本: {new_version}")

        confirm = input("確定要發布此版本嗎？(y/N): ")
        if confirm.lower() != "y":
            print("已取消")
            return

    # 更新版本號
    update_version(new_version)

    # 建立發布
    if create_release(new_version, commit_message):
        print("🎉 發布完成！")
        print("請到 GitHub 查看 Actions 的建置進度。")
    else:
        print("❌ 發布失敗")


if __name__ == "__main__":
    main()
