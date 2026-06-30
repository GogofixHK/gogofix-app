#!/usr/bin/env python3.11
"""
為每種顏色下載對應的 Switch Lite 圖片，並分別上傳
"""
import requests
import sys
import time

BASE_URL = "https://gogofixhk.com"
ADMIN_PASSWORD = "gogofix2024"

print("🔐 登入管理員...")
resp = requests.post(f"{BASE_URL}/api/admin/login", json={"password": ADMIN_PASSWORD})
token = resp.json()["token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"✅ 已登入\n")

# 先用 API 清除所有圖片的 image_url（繞過同名同步邏輯）
# 改用直接 PUT 更新每個產品

# 各顏色對應的圖片 URL（多個備用來源）
color_sources = {
    "黃色": [
        "https://static.wikia.nocookie.net/nintendo/images/8/88/Switch_Lite_yellow.png/revision/latest?cb=20250403000254&path-prefix=en",
        "https://assets.nintendo.com/image/upload/f_auto/q_auto/dpr_2.0/c_scale,w_400/ncom/en_US/hardware/switch/lite/yellow-01",
    ],
    "珊瑚藍": [
        "https://static.wikia.nocookie.net/nintendo/images/1/13/Switch_Lite_Blue.png/revision/latest?cb=20250402233126&path-prefix=en",
        "https://assets.nintendo.com/image/upload/f_auto/q_auto/dpr_2.0/c_scale,w_400/ncom/en_US/hardware/switch/lite/blue-01",
    ],
    "珊瑚紅": [
        "https://static.wikia.nocookie.net/nintendo/images/5/5c/Switch_Lite_Coral.png/revision/latest?cb=20250403000019&path-prefix=en",
        "https://assets.nintendo.com/image/upload/f_auto/q_auto/dpr_2.0/c_scale,w_400/ncom/en_US/hardware/switch/lite/coral-01",
    ],
    "青綠色": [
        "https://static.wikia.nocookie.net/nintendo/images/6/6e/Switch_Lite_turquoise.png/revision/latest?cb=20190920194613&path-prefix=en",
        "https://assets.nintendo.com/image/upload/f_auto/q_auto/dpr_2.0/c_scale,w_400/ncom/en_US/hardware/switch/lite/turquoise-01",
    ],
    "灰色": [
        "https://static.wikia.nocookie.net/nintendo/images/f/f8/Switch_Lite_grey.png/revision/latest?cb=20190920195646&path-prefix=en",
        "https://assets.nintendo.com/image/upload/f_auto/q_auto/dpr_2.0/c_scale,w_400/ncom/en_US/hardware/switch/lite/gray-01",
    ],
}

# 獲取產品列表
products = requests.get(f"{BASE_URL}/api/products").json()

# 第一步：清除所有圖片的 image_url
print("🧹 清除舊圖片關聯...")
for p in products:
    pid = p["id"]
    resp = requests.put(
        f"{BASE_URL}/api/admin/products/{pid}",
        headers={**headers, "Content-Type": "application/json"},
        json={"color": "__UNCHANGED__", "description": "__UNCHANGED__", "name": "", "category": "", "price": 0, "stock": -1}
    )
print("✅ 已清除\n")

def download_image(urls, color_name):
    """嘗試多個 URL 下載"""
    for url in urls:
        try:
            print(f"    🔽 {url[:85]}...")
            resp = requests.get(url, timeout=20, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            })
            if resp.status_code == 200 and len(resp.content) > 5000:
                ct = resp.headers.get("Content-Type", "")
                ext = "png" if "png" in ct or "png" in url else "jpg"
                print(f"    ✅ {len(resp.content)} bytes ({ext})")
                return resp.content, ext
            else:
                print(f"    ⚠️  status={resp.status_code}, size={len(resp.content)}")
        except Exception as e:
            print(f"    ❌ {e}")
    return None, None

# 第二步：逐個下載並上傳
for p in products:
    color = p["color"]
    pid = p["id"]
    pname = p["name"]
    
    print(f"🎮 {pname} — {color} (ID: {pid})")
    
    urls = color_sources.get(color, [])
    if not urls:
        print(f"  ⚠️  無圖片來源")
        continue
    
    img_data, ext = download_image(urls, color)
    
    if img_data:
        files = {"file": (f"switch_lite_{color}_{pid}.{ext}", img_data, f"image/{'png' if ext=='png' else 'jpeg'}")}
        resp = requests.post(
            f"{BASE_URL}/api/admin/products/{pid}/upload-image",
            headers={"Authorization": f"Bearer {token}"},
            files=files
        )
        if resp.status_code == 200:
            data = resp.json()
            print(f"  🖼️  上傳成功 → {data.get('image_url', '')}")
        else:
            print(f"  ❌ 上傳失敗: {resp.status_code}")
    else:
        print(f"  ❌ 無法下載")
    
    # 短暫延遲避免 API 限制
    time.sleep(0.5)

print(f"\n{'='*50}")
print("✅ 全部完成！請刷新網站查看。")
