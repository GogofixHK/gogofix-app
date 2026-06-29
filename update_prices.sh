#!/bin/bash
# ==========================================
# GoGofix 回收價格定時更新腳本
# 每天 9:00 / 13:00 / 20:00 自動執行
# ==========================================

LOG_FILE="/workspace/gogofix_app/price_update_cron.log"
API_URL="http://localhost:8000/api/recycle/update-prices"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 開始更新回收價格..." >> "$LOG_FILE"

# 呼叫 API 觸發更新
RESULT=$(curl -s -X POST "$API_URL" 2>&1)

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 結果: $RESULT" >> "$LOG_FILE"

echo "---" >> "$LOG_FILE"
