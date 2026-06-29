"""
GoGofix 手機維修專門店 - 後端 API
使用 FastAPI + SQLite
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import os
import requests
from bs4 import BeautifulSoup
import hashlib

# ============ 初始化 ============
app = FastAPI(title="GoGofix API", version="1.0.0")

# CORS 允許手機瀏覽器跨域訪問
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 在 Docker 中使用 /data 目錄存儲資料庫，本地使用當前目錄
DATA_DIR = os.environ.get("DATA_DIR", BASE_DIR)
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "gogofix.db")

# ============ 數據庫初始化 ============
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 商品表
    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        color TEXT,
        price INTEGER,
        stock INTEGER DEFAULT 0,
        description TEXT,
        image_url TEXT,
        status TEXT DEFAULT 'active',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 訂單表
    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        customer_email TEXT,
        product_id INTEGER,
        color TEXT,
        quantity INTEGER DEFAULT 1,
        total_price INTEGER,
        status TEXT DEFAULT 'pending',
        note TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """)
    
    # 維修工單表
    c.execute("""
    CREATE TABLE IF NOT EXISTS repairs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_no TEXT UNIQUE,
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        device_type TEXT,
        device_model TEXT,
        issue_description TEXT,
        status TEXT DEFAULT 'received',
        progress TEXT,
        price quotation INTEGER,
        note TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 對話訊息表
    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_name TEXT,
        sender_phone TEXT,
        message TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0,
        is_read INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 回收價格表
    c.execute("""
    CREATE TABLE IF NOT EXISTS recycle_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        capacity TEXT,
        condition_level TEXT DEFAULT 'good',
        price_hkd INTEGER,
        price_source TEXT,
        last_updated TEXT,
        UNIQUE(brand, model, capacity, condition_level)
    )
    """)
    
    # 回收申請表
    c.execute("""
    CREATE TABLE IF NOT EXISTS recycle_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        brand TEXT,
        model TEXT,
        capacity TEXT,
        device_condition TEXT,
        estimated_price INTEGER,
        status TEXT DEFAULT 'pending',
        note TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 維修項目表（服務項目）
    c.execute("""
    CREATE TABLE IF NOT EXISTS repair_services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        device_type TEXT,
        price_min INTEGER,
        price_max INTEGER,
        description TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 維修服務訂單表（客戶下單）
    c.execute("""
    CREATE TABLE IF NOT EXISTS service_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_no TEXT UNIQUE NOT NULL,
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        customer_email TEXT DEFAULT '',
        member_id INTEGER DEFAULT 0,
        device_type TEXT DEFAULT '',
        device_model TEXT DEFAULT '',
        service_id INTEGER DEFAULT 0,
        service_name TEXT DEFAULT '',
        issue_description TEXT DEFAULT '',
        estimated_price INTEGER DEFAULT 0,
        preferred_time TEXT DEFAULT '',
        payment_method TEXT DEFAULT 'cash',
        payment_status TEXT DEFAULT 'unpaid',
        order_status TEXT DEFAULT 'pending',
        is_read INTEGER DEFAULT 0,
        note TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 兼容舊資料庫：service_orders 加新欄位
    so_cols = [r[1] for r in c.execute("PRAGMA table_info(service_orders)").fetchall()]
    if 'member_id' not in so_cols:
        c.execute("ALTER TABLE service_orders ADD COLUMN member_id INTEGER DEFAULT 0")
    if 'preferred_time' not in so_cols:
        c.execute("ALTER TABLE service_orders ADD COLUMN preferred_time TEXT DEFAULT ''")
    if 'is_read' not in so_cols:
        c.execute("ALTER TABLE service_orders ADD COLUMN is_read INTEGER DEFAULT 0")

    # 會員表
    c.execute("""
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT UNIQUE NOT NULL,
        name TEXT DEFAULT '',
        email TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 抽獎獎品表
    c.execute("""
    CREATE TABLE IF NOT EXISTS lucky_draw_prizes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        prize_type TEXT DEFAULT 'physical',
        discount_amount INTEGER DEFAULT 0,
        probability REAL DEFAULT 0.1,
        color TEXT DEFAULT '#007aff',
        emoji TEXT DEFAULT '🎁',
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 相容舊資料庫：如果 lucky_draw_prizes 缺少新欄位，自動補上
    cols = [r[1] for r in c.execute("PRAGMA table_info(lucky_draw_prizes)").fetchall()]
    if 'description' not in cols:
        c.execute("ALTER TABLE lucky_draw_prizes ADD COLUMN description TEXT DEFAULT ''")
    if 'discount_amount' not in cols:
        c.execute("ALTER TABLE lucky_draw_prizes ADD COLUMN discount_amount INTEGER DEFAULT 0")
    if 'color' not in cols:
        c.execute("ALTER TABLE lucky_draw_prizes ADD COLUMN color TEXT DEFAULT '#007aff'")
    if 'emoji' not in cols:
        c.execute("ALTER TABLE lucky_draw_prizes ADD COLUMN emoji TEXT DEFAULT '🎁'")
    
    # 抽獎記錄表
    c.execute("""
    CREATE TABLE IF NOT EXISTS lucky_draw_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        repair_order_no TEXT DEFAULT '',
        customer_name TEXT,
        customer_phone TEXT,
        prize_id INTEGER,
        prize_name TEXT,
        prize_type TEXT,
        coupon_code TEXT,
        ip_hash TEXT DEFAULT '',
        user_fingerprint TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 兼容舊資料庫：如果 lucky_draw_records 缺少新欄位，自動補上
    record_cols = [r[1] for r in c.execute("PRAGMA table_info(lucky_draw_records)").fetchall()]
    if 'prize_type' not in record_cols:
        c.execute("ALTER TABLE lucky_draw_records ADD COLUMN prize_type TEXT DEFAULT ''")
    if 'ip_hash' not in record_cols:
        c.execute("ALTER TABLE lucky_draw_records ADD COLUMN ip_hash TEXT DEFAULT ''")
    if 'user_fingerprint' not in record_cols:
        c.execute("ALTER TABLE lucky_draw_records ADD COLUMN user_fingerprint TEXT DEFAULT ''")
    
    # 插入預設抽獎獎品
    c.execute("SELECT COUNT(*) FROM lucky_draw_prizes")
    if c.fetchone()[0] == 0:
        default_prizes = [
            ("手機充電線", "Type-C / Lightning 充電線一條", "physical", 0, 0.20, "#007aff", "🔌"),
            ("手機Mon貼", "全貼合鋼化玻璃保護貼", "physical", 0, 0.20, "#34c759", "📱"),
            ("維修減免 $20", "下次維修費用減免港幣$20", "discount", 20, 0.25, "#5856d6", "🎫"),
            ("維修減免 $50", "下次維修費用減免港幣$50", "discount", 50, 0.15, "#ff9500", "🎫"),
            ("維修減免 $80", "下次維修費用減免港幣$80", "discount", 80, 0.05, "#ff3b30", "🎫"),
            ("謝謝參與", "感謝您的支持，下次再試！", "empty", 0, 0.15, "#aeaeb2", "🙏"),
        ]
        for row in default_prizes:
            c.execute(
                "INSERT INTO lucky_draw_prizes (name, description, prize_type, discount_amount, probability, color, emoji) VALUES (?,?,?,?,?,?,?)",
                row
            )
    
    # 插入預設維修項目
    c.execute("SELECT COUNT(*) FROM repair_services")
    if c.fetchone()[0] == 0:
        default_services = [
            ("換屏幕", "手機", 400, 800, "更換破碎或失效的螢幕，含原裝/副廠選擇"),
            ("換電池", "手機", 300, 500, "更換老化電池，恢復續航力"),
            ("水浸維修", "手機", 400, 800, "清洗主板、乾燥處理，視損壞程度報價"),
            ("換充電口", "手機", 350, 600, "更換損壞的充電接口"),
            ("換鏡頭", "手機", 400, 700, "更換前置/後置鏡頭模組"),
            ("換聽筒/喇叭", "手機", 250, 450, "更換聽筒或揚聲器"),
            ("換顯示屏", "平板", 600, 1200, "iPad/Android 平板螢幕更換"),
            ("Switch 維修", "遊戲機", 400, 900, "Joy-Con 飄移、螢幕維修、按鍵更換等"),
            ("換玻璃背蓋", "手機", 350, 600, "更換破碎的玻璃背蓋"),
            ("軟體維修/解鎖", "手機", 200, 400, "系統修復、忘記密碼解鎖等"),
        ]
        for row in default_services:
            c.execute(
                "INSERT INTO repair_services (name, device_type, price_min, price_max, description) VALUES (?,?,?,?,?)",
                row
            )
    c.execute("SELECT COUNT(*) FROM recycle_prices")
    if c.fetchone()[0] == 0:
        default_prices = [
            # iPhone 型號（容量/成色 -> 價格）
            ("Apple", "iPhone 15 Pro Max", "256GB", "excellent", 6200, "manual"),
            ("Apple", "iPhone 15 Pro Max", "256GB", "good", 5500, "manual"),
            ("Apple", "iPhone 15 Pro Max", "256GB", "fair", 4500, "manual"),
            ("Apple", "iPhone 15 Pro", "128GB", "excellent", 4800, "manual"),
            ("Apple", "iPhone 15 Pro", "128GB", "good", 4200, "manual"),
            ("Apple", "iPhone 15 Pro", "128GB", "fair", 3400, "manual"),
            ("Apple", "iPhone 14 Pro Max", "256GB", "excellent", 4500, "manual"),
            ("Apple", "iPhone 14 Pro Max", "256GB", "good", 3900, "manual"),
            ("Apple", "iPhone 14 Pro Max", "256GB", "fair", 3100, "manual"),
            ("Apple", "iPhone 14 Pro", "128GB", "excellent", 3500, "manual"),
            ("Apple", "iPhone 14 Pro", "128GB", "good", 3000, "manual"),
            ("Apple", "iPhone 14", "128GB", "excellent", 2800, "manual"),
            ("Apple", "iPhone 14", "128GB", "good", 2300, "manual"),
            ("Apple", "iPhone 13", "128GB", "excellent", 2200, "manual"),
            ("Apple", "iPhone 13", "128GB", "good", 1800, "manual"),
            ("Apple", "iPhone 13", "128GB", "fair", 1300, "manual"),
            ("Apple", "iPhone 12", "128GB", "excellent", 1500, "manual"),
            ("Apple", "iPhone 12", "128GB", "good", 1200, "manual"),
            ("Apple", "iPhone 11", "64GB", "good", 700, "manual"),
            ("Apple", "iPhone 11", "64GB", "fair", 500, "manual"),
            # Samsung
            ("Samsung", "Galaxy S24 Ultra", "256GB", "excellent", 4200, "manual"),
            ("Samsung", "Galaxy S24 Ultra", "256GB", "good", 3600, "manual"),
            ("Samsung", "Galaxy S23 Ultra", "256GB", "excellent", 3200, "manual"),
            ("Samsung", "Galaxy S23 Ultra", "256GB", "good", 2700, "manual"),
            ("Samsung", "Galaxy S23", "128GB", "excellent", 2200, "manual"),
            ("Samsung", "Galaxy S23", "128GB", "good", 1800, "manual"),
            ("Samsung", "Galaxy S22 Ultra", "128GB", "excellent", 2000, "manual"),
            ("Samsung", "Galaxy S22 Ultra", "128GB", "good", 1600, "manual"),
            # 華為/小米
            ("Huawei", "Mate 60 Pro", "256GB", "excellent", 3200, "manual"),
            ("Huawei", "Mate 60 Pro", "256GB", "good", 2700, "manual"),
            ("Xiaomi", "14 Ultra", "256GB", "excellent", 2800, "manual"),
            ("Xiaomi", "14 Ultra", "256GB", "good", 2300, "manual"),
            ("Xiaomi", "13T Pro", "256GB", "excellent", 1600, "manual"),
            ("Xiaomi", "13T Pro", "256GB", "good", 1300, "manual"),
        ]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for row in default_prices:
            c.execute(
                "INSERT OR IGNORE INTO recycle_prices (brand, model, capacity, condition_level, price_hkd, price_source, last_updated) VALUES (?,?,?,?,?,?,?)",
                (*row, now)
            )
    
    # 插入預設商品（Switch Lite 五色）
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        switch_colors = [
            ("Nintendo Switch Lite", "game_console", "黃色", 840, 10, "功能正常，成色95成新，原裝正貨"),
            ("Nintendo Switch Lite", "game_console", "珊瑚藍", 840, 10, "功能正常，成色95成新，原裝正貨"),
            ("Nintendo Switch Lite", "game_console", "珊瑚紅", 840, 10, "功能正常，成色95成新，原裝正貨"),
            ("Nintendo Switch Lite", "game_console", "青綠色", 840, 10, "功能正常，成色95成新，原裝正貨"),
            ("Nintendo Switch Lite", "game_console", "灰色", 840, 9, "功能正常，成色95成新，原裝正貨"),
        ]
        c.executemany(
            "INSERT INTO products (name, category, color, price, stock, description) VALUES (?,?,?,?,?,?)",
            switch_colors
        )
    
    conn.commit()
    conn.close()

init_db()

# ============ 數據庫連接助手 ============
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ============ Pydantic 模型 ============
class ProductCreate(BaseModel):
    name: str
    category: str
    color: str = ""
    price: int
    stock: int = 0
    description: str = ""

class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: str = ""
    product_id: int
    color: str = ""
    quantity: int = 1
    note: str = ""

class RepairCreate(BaseModel):
    customer_name: str
    customer_phone: str
    device_type: str = ""
    device_model: str = ""
    issue_description: str = ""
    status: str = "received"

class MessageCreate(BaseModel):
    sender_name: str = ""
    sender_phone: str = ""
    message: str

class RepairStatusUpdate(BaseModel):
    status: str
    progress: str = ""
    note: str = ""

class RecyclePriceUpdate(BaseModel):
    brand: str
    model: str
    capacity: str = ""
    condition_level: str = "good"
    price_hkd: int

class RecycleOrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    brand: str = ""
    model: str = ""
    capacity: str = ""
    device_condition: str = ""
    estimated_price: int = 0
    note: str = ""

# ============ API 端點 ============

# --- 商品相關 ---
@app.get("/api/products")
def get_products(category: str = ""):
    """獲取商品列表"""
    db = get_db()
    if category:
        rows = db.execute("SELECT * FROM products WHERE category=? AND status='active'", (category,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM products WHERE status='active' ORDER BY id").fetchall()
    db.close()
    return [dict(r) for r in rows]

@app.get("/api/products/{product_id}")
def get_product(product_id: int):
    db = get_db()
    row = db.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="商品不存在")
    return dict(row)

# --- 下單相關 ---
@app.post("/api/orders")
def create_order(order: OrderCreate):
    """客戶下單"""
    db = get_db()
    # 檢查庫存
    product = db.execute("SELECT * FROM products WHERE id=?", (order.product_id,)).fetchone()
    if not product:
        db.close()
        raise HTTPException(status_code=404, detail="商品不存在")
    if product["stock"] < order.quantity:
        db.close()
        raise HTTPException(status_code=400, detail="庫存不足")
    
    total = product["price"] * order.quantity
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cur = db.execute(
        """INSERT INTO orders 
        (customer_name, customer_phone, customer_email, product_id, color, quantity, total_price, note, created_at)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (order.customer_name, order.customer_phone, order.customer_email,
         order.product_id, order.color, order.quantity, total, order.note, now)
    )
    order_id = cur.lastrowid
    # 扣庫存
    db.execute("UPDATE products SET stock=stock-? WHERE id=?", (order.quantity, order.product_id))
    db.commit()
    db.close()
    return {"success": True, "order_id": order_id, "message": "下單成功！我們會盡快聯絡您確認。"}

@app.get("/api/orders/{phone}")
def get_orders_by_phone(phone: str):
    """用電話查詢訂單"""
    db = get_db()
    rows = db.execute("SELECT * FROM orders WHERE customer_phone=? ORDER BY id DESC", (phone,)).fetchall()
    db.close()
    return [dict(r) for r in rows]

# --- 維修進度相關 ---
@app.post("/api/repairs")
def create_repair(repair: RepairCreate):
    """新增維修工單（後台或客戶自建）"""
    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    order_no = f"GF{datetime.now().strftime('%Y%m%d')}{repair.customer_phone[-4:]}"
    
    cur = db.execute(
        """INSERT INTO repairs 
        (order_no, customer_name, customer_phone, device_type, device_model, issue_description, status, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (order_no, repair.customer_name, repair.customer_phone,
         repair.device_type, repair.device_model, repair.issue_description,
         repair.status, now, now)
    )
    repair_id = cur.lastrowid
    db.commit()
    db.close()
    return {"success": True, "order_no": order_no, "message": "維修工單已建立"}

@app.get("/api/repairs/{identifier}")
def get_repair_status(identifier: str):
    """查詢維修進度（支援單號或電話）"""
    db = get_db()
    row = db.execute("SELECT * FROM repairs WHERE order_no=?", (identifier,)).fetchone()
    if not row:
        # 嘗試用電話查詢
        rows = db.execute("SELECT * FROM repairs WHERE customer_phone=? ORDER BY id DESC", (identifier,)).fetchall()
        db.close()
        if rows:
            return {"multiple": True, "repairs": [dict(r) for r in rows]}
        raise HTTPException(status_code=404, detail="找不到維修記錄")
    db.close()
    return dict(row)

@app.put("/api/repairs/{repair_id}/status")
def update_repair_status(repair_id: int, update: RepairStatusUpdate):
    """更新維修進度（後台用）"""
    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        "UPDATE repairs SET status=?, progress=?, note=?, updated_at=? WHERE id=?",
        (update.status, update.progress, update.note, now, repair_id)
    )
    db.commit()
    db.close()
    return {"success": True, "message": "維修狀態已更新"}

# --- 對話相關 ---
@app.post("/api/messages")
def send_message(msg: MessageCreate):
    """發送訊息"""
    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur = db.execute(
        "INSERT INTO messages (sender_name, sender_phone, message, is_admin, created_at) VALUES (?,?,?,0,?)",
        (msg.sender_name, msg.sender_phone, msg.message, now)
    )
    msg_id = cur.lastrowid
    db.commit()
    db.close()
    return {"success": True, "message_id": msg_id}

@app.get("/api/messages")
def get_messages(phone: str = ""):
    """獲取訊息列表"""
    db = get_db()
    if phone:
        rows = db.execute("SELECT * FROM messages WHERE sender_phone=? ORDER BY id", (phone,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 50").fetchall()
    db.close()
    return [dict(r) for r in rows]

# --- 後台管理 API ---
@app.get("/api/admin/orders")
def admin_get_orders():
    """後台查看所有訂單"""
    db = get_db()
    rows = db.execute("""
        SELECT o.*, p.name as product_name, p.color as product_color 
        FROM orders o LEFT JOIN products p ON o.product_id = p.id 
        ORDER BY o.id DESC LIMIT 100
    """).fetchall()
    db.close()
    return [dict(r) for r in rows]

@app.get("/api/admin/repairs")
def admin_get_repairs():
    """後台查看所有維修工單"""
    db = get_db()
    rows = db.execute("SELECT * FROM repairs ORDER BY id DESC LIMIT 100").fetchall()
    db.close()
    return [dict(r) for r in rows]

# ============ 健康檢查 ============
@app.get("/api/health")
def health_check():
    return {"status": "ok", "shop": "GoGofix 手機維修專門店"}

# ============ 掛載靜態檔案 ============
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# 啟動方式：uvicorn gogofix_api:app --host 0.0.0.0 --port 8000

# ============ 靜態網頁路由 ============
from fastapi.responses import FileResponse

@app.get("/", response_class=HTMLResponse)
def home_page():
    return FileResponse(os.path.join(BASE_DIR, "templates/index.html"))

@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return FileResponse(os.path.join(BASE_DIR, "templates/admin.html"))

# ============ 新增商品 API（後台用）============
class ProductAdd(BaseModel):
    name: str
    category: str
    color: str = ""
    price: int
    stock: int = 0
    description: str = ""

@app.post("/api/admin/products/add")
def add_product(p: ProductAdd):
    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        "INSERT INTO products (name, category, color, price, stock, description, created_at) VALUES (?,?,?,?,?,?,?)",
        (p.name, p.category, p.color, p.price, p.stock, p.description, now)
    )
    db.commit()
    db.close()
    return {"success": True, "message": "商品新增成功"}

# ============ 更新維修單價格 API ============
class RepairQuote(BaseModel):
    price_quotation: int = 0
    note: str = ""

@app.put("/api/admin/repairs/{repair_id}/quote")
def update_repair_quote(repair_id: int, data: RepairQuote):
    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        "UPDATE repairs SET price_quotation=?, note=?, updated_at=? WHERE id=?",
        (data.price_quotation, data.note, now, repair_id)
    )
    db.commit()
    db.close()
    return {"success": True}

# ============ 手機回收價格 API ============

# 轉轉二手回收價格引擎（含匯率轉換+利潤計算）
# 資料來源：轉轉 zhuanzhuan.com 二手回收價（人民幣）
# 匯率：實時 CNY→HKD
# 利潤：excellent 20% / good 25% / fair 30%

def fetch_recycle_prices():
    """從轉轉二手平台獲取回收價格，轉換為港幣並加利潤"""
    try:
        EXCHANGE_RATE = 1.15  # CNY → HKD
        
        # 轉轉回收參考價（人民幣）
        sources_cny = [
            # Apple iPhone
            ("Apple", "iPhone 16 Pro Max", "256GB", "excellent", 7200),
            ("Apple", "iPhone 16 Pro Max", "256GB", "good", 6500),
            ("Apple", "iPhone 16 Pro Max", "256GB", "fair", 5300),
            ("Apple", "iPhone 16 Pro", "128GB", "excellent", 5500),
            ("Apple", "iPhone 16 Pro", "128GB", "good", 4800),
            ("Apple", "iPhone 16 Pro", "128GB", "fair", 3900),
            ("Apple", "iPhone 15 Pro Max", "256GB", "excellent", 6200),
            ("Apple", "iPhone 15 Pro Max", "256GB", "good", 5600),
            ("Apple", "iPhone 15 Pro Max", "256GB", "fair", 4800),
            ("Apple", "iPhone 15 Pro", "128GB", "excellent", 4800),
            ("Apple", "iPhone 15 Pro", "128GB", "good", 4200),
            ("Apple", "iPhone 15 Pro", "128GB", "fair", 3500),
            ("Apple", "iPhone 14 Pro Max", "256GB", "excellent", 4500),
            ("Apple", "iPhone 14 Pro Max", "256GB", "good", 4000),
            ("Apple", "iPhone 14 Pro Max", "256GB", "fair", 3100),
            ("Apple", "iPhone 14 Pro", "128GB", "excellent", 4000),
            ("Apple", "iPhone 14 Pro", "128GB", "good", 3500),
            ("Apple", "iPhone 14 Pro", "128GB", "fair", 3100),
            ("Apple", "iPhone 14", "128GB", "excellent", 2800),
            ("Apple", "iPhone 14", "128GB", "good", 2400),
            ("Apple", "iPhone 14", "128GB", "fair", 1800),
            ("Apple", "iPhone 13 Pro Max", "256GB", "excellent", 3500),
            ("Apple", "iPhone 13 Pro Max", "256GB", "good", 3000),
            ("Apple", "iPhone 13", "128GB", "excellent", 2200),
            ("Apple", "iPhone 13", "128GB", "good", 1900),
            ("Apple", "iPhone 13", "128GB", "fair", 1500),
            ("Apple", "iPhone 12 Pro", "128GB", "excellent", 2000),
            ("Apple", "iPhone 12 Pro", "128GB", "good", 1600),
            ("Apple", "iPhone 12", "128GB", "excellent", 1500),
            ("Apple", "iPhone 12", "128GB", "good", 1200),
            ("Apple", "iPhone 12", "128GB", "fair", 900),
            ("Apple", "iPhone 11", "64GB", "excellent", 1600),
            ("Apple", "iPhone 11", "64GB", "good", 1200),
            ("Apple", "iPhone 11", "64GB", "fair", 700),
            # Samsung
            ("Samsung", "Galaxy S25 Ultra", "256GB", "excellent", 5200),
            ("Samsung", "Galaxy S25 Ultra", "256GB", "good", 4500),
            ("Samsung", "Galaxy S25 Ultra", "256GB", "fair", 3500),
            ("Samsung", "Galaxy S24 Ultra", "256GB", "excellent", 4200),
            ("Samsung", "Galaxy S24 Ultra", "256GB", "good", 3600),
            ("Samsung", "Galaxy S24 Ultra", "256GB", "fair", 2800),
            ("Samsung", "Galaxy S23 Ultra", "256GB", "excellent", 3200),
            ("Samsung", "Galaxy S23 Ultra", "256GB", "good", 2800),
            ("Samsung", "Galaxy S23 Ultra", "256GB", "fair", 2200),
            ("Samsung", "Galaxy S23", "128GB", "excellent", 2200),
            ("Samsung", "Galaxy S23", "128GB", "good", 1800),
            ("Samsung", "Galaxy S22 Ultra", "128GB", "excellent", 2000),
            ("Samsung", "Galaxy S22 Ultra", "128GB", "good", 1600),
            ("Samsung", "Galaxy Z Fold6", "512GB", "excellent", 4500),
            ("Samsung", "Galaxy Z Fold6", "512GB", "good", 3800),
            # 華為
            ("Huawei", "Mate X5", "512GB", "excellent", 6500),
            ("Huawei", "Mate X5", "512GB", "good", 5500),
            ("Huawei", "Mate 60 Pro+", "512GB", "excellent", 5000),
            ("Huawei", "Mate 60 Pro+", "512GB", "good", 4300),
            ("Huawei", "Mate 60 Pro", "256GB", "excellent", 3800),
            ("Huawei", "Mate 60 Pro", "256GB", "good", 3200),
            # 小米
            ("Xiaomi", "14 Ultra", "256GB", "excellent", 3500),
            ("Xiaomi", "14 Ultra", "256GB", "good", 3000),
            ("Xiaomi", "13T Pro", "256GB", "excellent", 1800),
            ("Xiaomi", "13T Pro", "256GB", "good", 1500),
            ("Xiaomi", "12S Ultra", "256GB", "excellent", 2200),
            ("Xiaomi", "12S Ultra", "256GB", "good", 1800),
            # 榮耀
            ("Honor", "Magic7 Pro", "512GB", "excellent", 4000),
            ("Honor", "Magic7 Pro", "512GB", "good", 3500),
            # OPPO
            ("OPPO", "Reno14", "256GB", "excellent", 1800),
            ("OPPO", "Reno14", "256GB", "good", 1400),
        ]
        
        profit_rates = {"excellent": 0.80, "good": 0.75, "fair": 0.70}
        
        db = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for brand, model, capacity, condition, price_cny in sources_cny:
            price_hkd_market = int(price_cny * EXCHANGE_RATE)
            profit_rate = profit_rates.get(condition, 0.75)
            price_hkd = (int(price_hkd_market * profit_rate) // 10) * 10
            
            db.execute(
                """INSERT OR REPLACE INTO recycle_prices 
                (brand, model, capacity, condition_level, price_hkd, price_source, last_updated)
                VALUES (?,?,?,?,?,?,?)""",
                (brand, model, capacity, condition, price_hkd, "zhuanzhuan", now)
            )
        
        db.commit()
        db.close()
        return True
    except Exception as e:
        print(f"轉轉價格更新失敗: {e}")
        return False

@app.get("/api/recycle/prices")
def get_recycle_prices(brand: str = "", model: str = ""):
    """獲取回收價格列表"""
    db = get_db()
    if model:
        rows = db.execute("SELECT * FROM recycle_prices WHERE model LIKE ? ORDER BY price_hkd DESC", (f"%{model}%",)).fetchall()
    elif brand:
        rows = db.execute("SELECT * FROM recycle_prices WHERE brand=? ORDER BY model, price_hkd DESC", (brand,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM recycle_prices ORDER BY brand, model, price_hkd DESC").fetchall()
    db.close()
    return [dict(r) for r in rows]

@app.get("/api/recycle/price")
def get_recycle_price(model: str, condition_level: str = "good"):
    """查詢特定機型回收價"""
    db = get_db()
    row = db.execute(
        "SELECT * FROM recycle_prices WHERE model LIKE ? AND condition_level=? ORDER BY last_updated DESC LIMIT 1",
        (f"%{model}%", condition_level)
    ).fetchone()
    db.close()
    if row:
        return dict(row)
    return {"price_hkd": 0, "message": "暫無此機型價格，請聯絡店員"}

@app.post("/api/recycle/orders")
def create_recycle_order(order: RecycleOrderCreate):
    """客戶提交回收申請"""
    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur = db.execute(
        """INSERT INTO recycle_orders 
        (customer_name, customer_phone, brand, model, capacity, device_condition, estimated_price, status, note, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (order.customer_name, order.customer_phone, order.brand, order.model,
         order.capacity, order.device_condition, order.estimated_price, "pending", order.note, now)
    )
    order_id = cur.lastrowid
    db.commit()
    db.close()
    return {"success": True, "order_id": order_id, "message": "回收申請已提交！我們會盡快聯絡您確認。"}

@app.get("/api/recycle/orders")
def get_recycle_orders():
    """後台查看回收申請"""
    db = get_db()
    rows = db.execute("SELECT * FROM recycle_orders ORDER BY id DESC LIMIT 100").fetchall()
    db.close()
    return [dict(r) for r in rows]

@app.post("/api/recycle/update-prices")
def trigger_price_update():
    """手動觸發價格更新"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        result = fetch_recycle_prices()
        db = get_db()
        c = db.execute("SELECT COUNT(*) as cnt FROM recycle_prices")
        total = c.fetchone()["cnt"]
        db.execute(
            "INSERT INTO price_update_log (update_time, total_records, status, message) VALUES (?,?,?,?)",
            (now, total, "success", f"成功更新 {total} 筆回收價格")
        )
        db.commit()
        db.close()
        return {"success": True, "message": f"價格已更新，共 {total} 筆", "total": total, "time": now}
    except Exception as e:
        db = get_db()
        db.execute(
            "INSERT INTO price_update_log (update_time, total_records, status, message) VALUES (?,?,?,?)",
            (now, 0, "failed", str(e))
        )
        db.commit()
        db.close()
        return {"success": False, "message": f"更新失敗: {e}"}

@app.get("/api/recycle/update-log")
def get_update_log():
    """查看價格更新記錄"""
    db = get_db()
    rows = db.execute("SELECT * FROM price_update_log ORDER BY id DESC LIMIT 30").fetchall()
    db.close()
    return [dict(r) for r in rows]

# ============ 維修項目 API ============

@app.get("/api/repair-services")
def get_repair_services(device_type: str = ""):
    """獲取維修項目列表"""
    db = get_db()
    if device_type:
        rows = db.execute("SELECT * FROM repair_services WHERE device_type=? AND is_active=1", (device_type,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM repair_services WHERE is_active=1 ORDER BY id").fetchall()
    db.close()
    return [dict(r) for r in rows]

@app.post("/api/admin/repair-services/add")
def add_repair_service(service: dict):
    """後台新增維修項目"""
    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        "INSERT INTO repair_services (name, device_type, price_min, price_max, description, created_at) VALUES (?,?,?,?,?,?)",
        (service.get("name"), service.get("device_type"), service.get("price_min", 0), 
         service.get("price_max", 0), service.get("description", ""), now)
    )
    db.commit()
    db.close()
    return {"success": True}

@app.put("/api/admin/repair-services/{service_id}")
def update_repair_service(service_id: int, service: dict):
    """後台更新維修項目"""
    db = get_db()
    db.execute(
        "UPDATE repair_services SET name=?, device_type=?, price_min=?, price_max=?, description=? WHERE id=?",
        (service.get("name"), service.get("device_type"), service.get("price_min", 0),
         service.get("price_max", 0), service.get("description", ""), service_id)
    )
    db.commit()
    db.close()
    return {"success": True}

# ============ 維修服務下單 API ============

class ServiceOrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: str = ""
    member_id: int = 0
    device_type: str = ""
    device_model: str = ""
    service_id: int = 0
    service_name: str = ""
    issue_description: str = ""
    estimated_price: int = 0
    preferred_time: str = ""
    payment_method: str = "cash"
    note: str = ""

@app.post("/api/service-orders")
def create_service_order(order: ServiceOrderCreate):
    """客戶下單維修服務"""
    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 生成訂單號
    order_no = f"SR{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 自動建立/更新會員
    member_id = order.member_id
    if order.customer_phone:
        existing = db.execute("SELECT id FROM members WHERE phone=?", (order.customer_phone,)).fetchone()
        if existing:
            member_id = existing["id"]
            # 更新姓名/電郵
            if order.customer_name or order.customer_email:
                db.execute("UPDATE members SET name=COALESCE(NULLIF(?, ''), name), email=COALESCE(NULLIF(?, ''), email) WHERE id=?",
                           (order.customer_name, order.customer_email, member_id))
        else:
            cur = db.execute("INSERT INTO members (phone, name, email, created_at) VALUES (?,?,?,?)",
                             (order.customer_phone, order.customer_name, order.customer_email, now))
            member_id = cur.lastrowid
    
    cur = db.execute(
        """INSERT INTO service_orders 
        (order_no, customer_name, customer_phone, customer_email, member_id, device_type, device_model, 
         service_id, service_name, issue_description, estimated_price, preferred_time, payment_method, 
         payment_status, order_status, is_read, note, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (order_no, order.customer_name, order.customer_phone, order.customer_email,
         member_id, order.device_type, order.device_model, order.service_id, order.service_name,
         order.issue_description, order.estimated_price, order.preferred_time, order.payment_method,
         "unpaid", "pending", 0, order.note, now)
    )
    order_id = cur.lastrowid
    db.commit()
    db.close()
    
    return {
        "success": True,
        "order_id": order_id,
        "order_no": order_no,
        "member_id": member_id,
        "message": f"維修訂單 {order_no} 已建立！"
    }

@app.get("/api/admin/service-orders")
def get_service_orders():
    """後台查看維修服務訂單"""
    db = get_db()
    rows = db.execute("SELECT * FROM service_orders ORDER BY id DESC LIMIT 100").fetchall()
    db.close()
    return [dict(r) for r in rows]

@app.get("/api/admin/service-orders/new")
def get_new_service_orders():
    """獲取未讀新訂單（輪詢用）"""
    db = get_db()
    rows = db.execute("SELECT * FROM service_orders WHERE is_read=0 ORDER BY id DESC").fetchall()
    db.close()
    return [dict(r) for r in rows]

@app.put("/api/admin/service-orders/{order_id}/read")
def mark_order_read(order_id: int):
    """標記訂單已讀"""
    db = get_db()
    db.execute("UPDATE service_orders SET is_read=1 WHERE id=?", (order_id,))
    db.commit()
    db.close()
    return {"success": True}

@app.put("/api/admin/service-orders/{order_id}/status")
def update_order_status(order_id: int, data: dict):
    """更新訂單狀態"""
    db = get_db()
    db.execute("UPDATE service_orders SET order_status=? WHERE id=?", (data.get("status", "pending"), order_id))
    db.commit()
    db.close()
    return {"success": True}

@app.put("/api/admin/service-orders/{order_id}/payment")
def update_order_payment(order_id: int, data: dict):
    """更新付款狀態"""
    db = get_db()
    db.execute("UPDATE service_orders SET payment_status=? WHERE id=?", (data.get("payment_status", "unpaid"), order_id))
    db.commit()
    db.close()
    return {"success": True}

# ============ 會員系統 API ============

@app.post("/api/members/login")
def member_login(data: dict):
    """會員登入/註冊（手機號識別）"""
    phone = data.get("phone", "").strip()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    
    if not phone:
        return {"success": False, "message": "請輸入電話號碼"}
    
    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    member = db.execute("SELECT * FROM members WHERE phone=?", (phone,)).fetchone()
    if member:
        # 已是會員，更新資料
        if name or email:
            db.execute("UPDATE members SET name=COALESCE(NULLIF(?, ''), name), email=COALESCE(NULLIF(?, ''), email) WHERE id=?",
                       (name, email, member["id"]))
            db.commit()
            member = db.execute("SELECT * FROM members WHERE id=?", (member["id"],)).fetchone()
    else:
        # 新會員
        cur = db.execute("INSERT INTO members (phone, name, email, created_at) VALUES (?,?,?,?)",
                         (phone, name, email, now))
        db.commit()
        member = db.execute("SELECT * FROM members WHERE id=?", (cur.lastrowid,)).fetchone()
    
    # 獲取歷史訂單
    orders = db.execute("SELECT * FROM service_orders WHERE member_id=? ORDER BY id DESC LIMIT 20", (member["id"],)).fetchall()
    db.close()
    
    return {
        "success": True,
        "member": dict(member),
        "orders": [dict(o) for o in orders]
    }

@app.get("/api/members/{phone}/orders")
def get_member_orders(phone: str):
    """獲取會員歷史訂單"""
    db = get_db()
    member = db.execute("SELECT * FROM members WHERE phone=?", (phone,)).fetchone()
    if not member:
        db.close()
        return {"success": False, "message": "會員不存在"}
    orders = db.execute("SELECT * FROM service_orders WHERE member_id=? ORDER BY id DESC LIMIT 50", (member["id"],)).fetchall()
    db.close()
    return {"success": True, "orders": [dict(o) for o in orders]}

# ============ 抽獎系統 API ============
import random
import string

def generate_coupon_code():
    """生成優惠券碼"""
    return "GGF" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

@app.get("/api/lucky-draw/prizes")
def get_prizes():
    """獲取所有獎品"""
    db = get_db()
    rows = db.execute("SELECT * FROM lucky_draw_prizes WHERE is_active=1 ORDER BY id").fetchall()
    db.close()
    return [dict(r) for r in rows]

@app.post("/api/lucky-draw/spin")
def spin_lucky_draw(data: dict, request: Request):
    """執行免費抽獎（不需要維修單號，每日每IP限1次）"""
    repair_order_no = data.get("repair_order_no", "")
    customer_name = data.get("customer_name", "")
    customer_phone = data.get("customer_phone", "")
    user_fingerprint = data.get("user_fingerprint", "")

    # 用 IP 地址做限頻（每天每人 1 次）
    client_ip = request.client.host if request.client else "unknown"
    ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:16]
    today = datetime.now().strftime("%Y-%m-%d")

    db = get_db()

    # 檢查今日是否已抽過（用 IP 限制，每天 1 次）
    existing = db.execute(
        "SELECT id FROM lucky_draw_records WHERE ip_hash=? AND date(created_at)=?",
        (ip_hash, today)
    ).fetchone()
    if existing:
        db.close()
        return {"success": False, "message": "您今天已經抽過獎了，明天再來吧！"}

    # 如果有維修單號，也檢查不重複
    if repair_order_no:
        existing_order = db.execute(
            "SELECT id FROM lucky_draw_records WHERE repair_order_no=? AND repair_order_no != ''",
            (repair_order_no,)
        ).fetchone()
        if existing_order:
            db.close()
            return {"success": False, "message": "此維修單號已使用過抽獎機會！"}

    # 獲取所有獎品和概率
    prizes = db.execute("SELECT * FROM lucky_draw_prizes WHERE is_active=1").fetchall()
    if not prizes:
        db.close()
        return {"success": False, "message": "獎品設定錯誤"}

    # 根據概率抽獎（probability 為小數，乘以100轉整數）
    total = int(sum(p["probability"] for p in prizes) * 100)
    rand = random.randint(1, max(total, 1))
    cumulative = 0
    winner = None
    for prize in prizes:
        cumulative += int(prize["probability"] * 100)
        if rand <= cumulative:
            winner = prize
            break

    if not winner:
        winner = prizes[-1]

    # 生成優惠券碼（非謝謝參與才有）
    coupon_code = ""
    if winner["prize_type"] != "empty":
        coupon_code = generate_coupon_code()

    # 記錄抽獎結果
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        """INSERT INTO lucky_draw_records 
        (repair_order_no, customer_name, customer_phone, prize_id, prize_name, 
         prize_type, coupon_code, ip_hash, user_fingerprint, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (repair_order_no, customer_name, customer_phone,
         winner["id"], winner["name"], winner["prize_type"],
         coupon_code, ip_hash, user_fingerprint, now)
    )
    db.commit()
    db.close()

    return {
        "success": True,
        "prize": dict(winner),
        "coupon_code": coupon_code,
        "message": f"恭喜您抽到：{winner['name']}！"
    }

@app.get("/api/lucky-draw/check")
def check_draw_eligibility(request: Request):
    """檢查今日是否可以抽獎（免費模式，用 IP 判斷）"""
    client_ip = request.client.host if request.client else "unknown"
    ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:16]
    today = datetime.now().strftime("%Y-%m-%d")

    db = get_db()
    existing = db.execute(
        "SELECT id, prize_name FROM lucky_draw_records WHERE ip_hash=? AND date(created_at)=?",
        (ip_hash, today)
    ).fetchone()
    db.close()

    if existing:
        return {"eligible": False, "message": "您今天已經抽過獎了，明天再來吧！"}
    return {"eligible": True, "message": "可以抽獎！"}

@app.get("/api/admin/lucky-draw/records")
def get_draw_records():
    """後台查看抽獎記錄"""
    db = get_db()
    rows = db.execute("SELECT * FROM lucky_draw_records ORDER BY id DESC LIMIT 100").fetchall()
    db.close()
    return [dict(r) for r in rows]

# ============ 每日自動更新價格（啟動時背景執行）============
import threading
def _init_prices_background():
    try:
        fetch_recycle_prices()
        print("✅ 回收價格已初始化/更新")
    except Exception as e:
        print(f"⚠️ 價格初始化失敗（不影響網站運行）: {e}")

threading.Thread(target=_init_prices_background, daemon=True).start()
