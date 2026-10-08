import json
import subprocess
import os

JSON_FILE = 'systems.json'

def load_data():
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_data(data):
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def git_sync(commit_msg):
    auto_push = input("\n是否立即 Commit 並 Git Push 到 GitHub？(y/n): ").strip().lower()
    if auto_push == 'y':
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("\n🎉 已成功同步至 GitHub！")
        except Exception as e:
            print(f"\n❌ Git 推送失敗: {e}")

def add_project(data):
    print("\n--- ➕ 新增技術實作 ---")
    title = input("1. 專案標題: ").strip()
    badge = input("2. 技術標籤/Badge (例如: C++17 / OpenCV): ").strip()
    desc = input("3. 專案詳細說明: ").strip()
    tags_str = input("4. 關鍵字 Tag (以逗點隔開): ").strip()
    github_url = input("5. GitHub 連結 (無可直接 Enter): ").strip()
    post_url = input("6. 展示貼文/影片連結 (無可直接 Enter): ").strip()

    tags = [t.strip() for t in tags_str.split(',') if t.strip()]
    links = []
    if github_url:
        links.append({"name": "💻 GitHub 專案庫", "url": github_url})
    if post_url:
        links.append({"name": "📹 實作展示 / 貼文", "url": post_url})

    new_item = {
        "id": len(data) + 1,
        "badge": badge,
        "title": title,
        "description": desc,
        "tags": tags,
        "links": links
    }

    data.insert(0, new_item)  # 置頂放在最前
    save_data(data)
    print(f"\n✅ 已成功加入：{title}")
    git_sync(f"feat: 新增專案 {title}")

def delete_project(data):
    if not data:
        print("\n⚠️ 目前 systems.json 內沒有任何專案資料。")
        return

    print("\n--- 🗑️ 目前專案清單 ---")
    for idx, item in enumerate(data):
        print(f"[{idx + 1}] {item.get('title')} ({item.get('badge')})")

    choice = input("\n請輸入要刪除的編號 (輸入 0 取消): ").strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(data):
            removed_item = data.pop(idx)
            save_data(data)
            print(f"\n🗑️ 已成功刪除：{removed_item.get('title')}")
            git_sync(f"fix: 刪除專案 {removed_item.get('title')}")
        elif idx == -1:
            print("\n已取消刪除。")
        else:
            print("\n⚠️ 編號超出範圍。")

def main():
    while True:
        data = load_data()
        print("\n==============================")
        print(" 🛠️  systems.json 文章管理工具")
        print("==============================")
        print("1. 新增專案卡片")
        print("2. 檢視與刪除誤填專案")
        print("3. 離開程式")
        
        choice = input("\n請選擇操作 (1/2/3): ").strip()
        
        if choice == '1':
            add_project(data)
        elif choice == '2':
            delete_project(data)
        elif choice == '3':
            print("\n結束程式。")
            break
        else:
            print("\n⚠️ 無效選擇，請重新輸入。")

if __name__ == '__main__':
    main()