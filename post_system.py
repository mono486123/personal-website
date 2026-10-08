import json
import subprocess
import os

JSON_FILE = 'systems.json'

def main():
    print("=== 🚀 個人數位花園 - 新增技術實作文章 ===")
    
    # 讀取現有 JSON
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []

    # 讓使用者輸入資訊
    title = input("1. 專案標題 (例如: DMS 駕駛監控系統): ").strip()
    badge = input("2. 技術標籤/Badge (例如: C++17 / OpenCV): ").strip()
    desc = input("3. 專案詳細說明: ").strip()
    tags_str = input("4. 關鍵字 Tag (以逗號隔開, 例如: C++,OpenCV): ").strip()
    github_url = input("5. GitHub 連結 (留空可跳過): ").strip()
    post_url = input("6. 展示貼文/影片連結 (留空可跳過): ").strip()

    # 處理標籤與連結
    tags = [t.strip() for t in tags_str.split(',') if t.strip()]
    links = []
    if github_url:
        links.append({"name": "💻 GitHub 專案庫", "url": github_url})
    if post_url:
        links.append({"name": "📹 實作展示 / 貼文", "url": post_url})

    # 建立新卡片資料
    new_item = {
        "id": len(data) + 1,
        "badge": badge,
        "title": title,
        "description": desc,
        "tags": tags,
        "links": links
    }

    # 自動【置頂】插入最前面（遞增最新在前）
    data.insert(0, new_item)

    # 寫回 JSON
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n✅ systems.json 已成功更新！")

    # 是否自動 Git Push
    auto_push = input("\n是否立即自動 Commit 並 Git Push 到 GitHub？(y/n): ").strip().lower()
    if auto_push == 'y':
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", f"feat: 新增專案 {title}"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("\n🎉 已成功發布至 GitHub！")
        except Exception as e:
            print(f"\n❌ Git 推送過程發生錯誤: {e}")

if __name__ == '__main__':
    main()