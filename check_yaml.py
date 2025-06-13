#!/usr/bin/env python3
"""
YAML 語法檢查工具
"""

import yaml
import sys


def check_yaml_syntax(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析 YAML
        data = yaml.safe_load(content)
        print(f"✅ {file_path} YAML 語法正確")

        # 檢查基本結構
        if "name" in data:
            print(f"   工作流程名稱: {data['name']}")

        if "on" in data:
            print(
                f"   觸發條件: {list(data['on'].keys()) if isinstance(data['on'], dict) else data['on']}"
            )

        if "jobs" in data:
            print(f"   工作任務: {list(data['jobs'].keys())}")

        return True

    except yaml.YAMLError as e:
        print(f"❌ {file_path} YAML 語法錯誤:")
        print(f"   {e}")
        return False
    except Exception as e:
        print(f"❌ 檢查 {file_path} 時發生錯誤:")
        print(f"   {e}")
        return False


if __name__ == "__main__":
    file_path = ".github/workflows/test_release.yml"
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    success = check_yaml_syntax(file_path)
    sys.exit(0 if success else 1)
