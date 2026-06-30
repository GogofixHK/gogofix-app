# GoGofix 手機維修專門店 — 項目狀態文檔

> 最後更新：2026/07/01 02:28

---

## 🌐 基本資訊

| 項目 | 值 |
|------|-----|
| 網站地址 | https://gogofixhk.com |
| GitHub 倉庫 | GogofixHK/gogofix-app |
| Railway Service ID | c04ea24d-a110-432b-b8f5-5c914ffc1c3e |
| Railway Project ID | 74324db8-dd61-4967-b1ab-a04e288d839c |
| Railway Environment ID | 57928521-75e8-42b5-947c-1087204e5f50 |
| Railway Token | c4a36115-5a78-443a-ad06-673eb2dd2b4d |
| 管理員密碼 | gogofix2024 |
| 店鋪地址 | 香港九龍深水埗福華街123號 |
| 營業時間 | 12:30 – 20:30（每日） |
| 聯絡電話 | 52382777 |
| WhatsApp | wa.me/85252382777 |

---

## 🛠 技術架構

- **後端**：FastAPI + SQLite + Uvicorn（Python）
- **前端**：單頁 HTML + 原生 JS（Léselle 風格極簡主題）
- **部署**：Railway（GitHub 自動部署，Dockerfile）
- **設計風格**：純白背景 `#ffffff`、深黑主色 `#1a1a1a`、超薄邊框、近扁平設計
- **所有 emoji 已移除**，統一用 SVG 圖標

### 核心文件

| 文件 | 用途 |
|------|------|
| `gogofix_api.py` | 主後端（FastAPI），包含所有 API 端點 + `init_db()` seed data |
| `templates/index.html` | 主前端（~3400 行），所有頁面 + JS 邏輯 |
| `templates/admin.html` | 管理後台頁面 |
| `seed_product_data.py` | 產品圖片上傳腳本（**每次部署後必須運行**） |
| `requirements.txt` | Python 依賴（含 python-multipart） |
| `Dockerfile` | Railway 部署配置 |
| `start.sh` | 啟動命令 `uvicorn gogofix_api:app` |

---

## ✅ 已完成功能

### 首頁
- 聯繫二維碼 hero 圖（微信 + WhatsApp + 電話）
- 6 個功能入口卡片（預約維修 / 商品商店 / 手機回收 / 維修價目 / WhatsApp）
- 滑動廣告已移除

### 商店
- 7 件商品：5 款 Switch Lite（HK$840）+ 2 款鋼化膜
- 每款 Switch Lite 顏色獨立商品 + 獨立圖片
- 產品詳情彈窗（大圖 + 描述 + 價格）
- 搜尋欄 + 分類篩選

### 維修預約系統
- **預約時間限制**：12:30 – 20:30（JS 驗證）
- **零件選擇系統**：`repair_part_options` 表，每個服務 2-4 個零件選項
- **定價公式**：零件成本 + HK$300 服務費
- **零件來源**：Refox / Rewa
- **屏幕選項**：Incell LCD / Hard OLED / Soft OLED / 原裝拆機屏
- **Switch 維修**：Joy-Con $150 / 主板 $650 / 屏幕更換 $680
- **線上支付**：FPS / Alipay / Octopus QR 碼
- **會員系統**：電話 + 密碼註冊/登入，localStorage 自動登入
- **訂單追蹤**：進度條顯示

### 回收系統
- **全系列回收價格**：iPhone 11–16 / iPad 全系列 / Samsung / Huawei / Xiaomi
- **價格邏輯**：容量越大價格越高，excellent > good > fair 遞減
- **型號搜尋框**：即時過濾型號
- **廣告圖**：GOGOFIX 二手回收 高價收機（`static/img/recycle_ad.png`）
- **價格參考說明**：黃色提示框，標明最終價以現場檢測為準
- **iPad 品牌獨立**：品牌選項中「iPad」與「Apple」分開

### 管理後台
- Bearer token 認證（`require_admin` 中間件）
- 訂單管理 / 商品管理 / 維修管理 / 回收申請管理
- 商品圖片上傳 API
- 即時訂單通知

### 抽獎功能
- ⏸️ **已隱藏**（HTML 註釋），JS 函數保留
- 待方案完善後啟用

---

## 📊 產品庫存

| ID | 產品 | 顏色/款式 | 價格 | 庫存 | 圖片 |
|----|------|-----------|------|------|------|
| 1 | Switch Lite | 黃色 | HK$840 | 10 | ✅ |
| 2 | Switch Lite | 珊瑚藍 | HK$840 | 10 | ✅ |
| 3 | Switch Lite | 珊瑚紅 | HK$840 | 10 | ✅ |
| 4 | Switch Lite | 青綠色 | HK$840 | 10 | ✅ |
| 5 | Switch Lite | 灰色 | HK$840 | 9 | ✅ |
| 6 | 手機鋼化膜 | 高清款 | HK$60 | 100 | ✅ |
| 7 | 手機鋼化膜 | 防窺款 | HK$90 | 100 | ✅ |

---

## 🔧 維修服務定價

| 服務 | 價格範圍 | 零件選項 |
|------|----------|----------|
| 換屏幕 | $480–$1150 | Incell LCD / Hard OLED / Soft OLED / 原裝拆機屏 |
| 換電池 | $380–$550 | 副廠電池 / 原廠電池 |
| 水浸維修 | $500–$850 | 視損壞程度報價 |
| 換充電口 | $360–$450 | 副廠 / 原廠 |
| 換鏡頭 | $420–$650 | 副廠 / 原廠 |
| 換聽筒/喇叭 | $350–$430 | 副廠 / 原廠 |
| 換玻璃背蓋 | $380–$520 | 副廠 / 原廠 |
| 軟體維修/解鎖 | $250–$450 | 純服務費 |
| 換顯示屏（平板） | $580–$1050 | 副廠 / 原廠 |
| Switch 維修 | $150–$680 | Joy-Con $150 / 屏幕更換 $680 / 主板 $650 |

---

## ⚠️ 已知問題 & 待辦

| # | 項目 | 優先級 | 備註 |
|---|------|--------|------|
| 1 | Railway 每次部署重置 SQLite DB | 🔴 高 | 產品圖片需運行 `seed_product_data.py` 重新上傳 |
| 2 | 設定 Railway Volume 掛載 `/data` | 🟡 中 | 解決 DB 持久化問題 |
| 3 | 定時更新回收價格 | 🟡 中 | 腳本已備 `gogofix_cron.txt`，每日 3 次 |
| 4 | 接入 AlipayHK 線上支付 API | 🟢 低 | 需 PID/keys |
| 5 | 鋼化膜產品圖片為佔位圖 | 🟢 低 | 可更換為實拍圖 |
| 6 | 抽獎功能待重新設計 | 🟢 低 | 已隱藏，JS 保留 |

---

## 📝 重要注意事項

1. **每次 Railway 部署後**，必須運行 `python3 seed_product_data.py` 重新上傳產品圖片
2. **管理員登入**：POST `/api/admin/login`，body `{"username":"admin","password":"gogofix2024"}`，返回 token
3. **產品上架 API**：POST `/api/admin/products/add`（需 Bearer token）
4. **圖片上傳 API**：POST `/api/admin/products/{id}/upload-image`（multipart/form-data）
5. **品牌分類**：iPad 的品牌值為 `iPad`（非 `Apple`），iPhone 為 `Apple`
6. **`gogofix_api.py` 的 seed data 包含鋼化膜產品**，但 DB 重置後 ID 會變

---

## 🔄 Git 提交歷史（近期）

```
0b91713 feat: 上架手機鋼化保護膜（高清款 / 防窺款）
4d8b6f1 feat: 五大改進 - 回收搜尋框+支付跳轉+維修價目入口+密碼提示+商店副標
ffdbbcd fix: 首頁hero圖片比例優化 + 頁尾營業時間改12:30
ee456b2 fix: 回收價格全面校正(容量越大價越高) + 維修預約限制12:30-20:30
4279ce3 fix: 移除首頁滑動廣告區塊
ffce9f4 fix: 首頁聯繫圖片去黑邊全寬顯示
4246aad feat: 首頁hero替換為聯繫二維碼圖片(微信+WhatsApp+電話)
24bc37f feat: 回收頁面加廣告圖+價格參考說明
fc58aa8 feat: 回收頁面新增iPad全系列回收價格
4279ce3 fix: 移除首頁滑動廣告區塊
```
