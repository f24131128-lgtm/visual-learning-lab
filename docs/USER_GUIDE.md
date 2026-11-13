# 開始使用 Visual Learning Lab

## 先試作品

從 README 的正式網站進入，選「簡諧運動」或「拋體運動」。示例不需金鑰。
波形用滑桿；拋體只拖有支援的端點，放開後確認正式數值。來源保持原貌。
Learn 看課程、Source 核對原文、Explore 操作、Practice 檢查理解。

## 用自己的 PDF／筆記（本機）

Python 3.12，在 repository root 執行：

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python tools/run_local.py
```

終端機會隱藏輸入 API key，不會寫入檔案。也支援既有 OPENAI_API_KEY 環境變數。
開啟印出的 localhost 網址，展開「帶入自己的教材」，選一份 PDF 或貼上文字，
按「開始理解」。明確 AI 動作才送出教材並產生費用；操作已生成的圖形和導覽不呼叫 AI。
金鑰的模型存取權、餘額及服務可用性須由自己的帳號提供。這不是離線 AI。
請勿公開轉發此私人伺服器。結束時 Ctrl+C；session 不保證跨重新啟動保留。

只想本機看示例：`python tools/run_local.py --demo`。
改連接埠：`python tools/run_local.py --port 8502`。

## 常見狀況

- 公開網站不能上傳：公開 AI 尚受獨立發布門檻限制。個人使用走上述本機流程。
- PDF 沒有文字：目前沒有 OCR；先使用文字型 PDF 或貼上文字。
- 沒有可拖端點：該表示沒有通過安全逆映射，使用既有滑桿或其他學習表示。
- AI 回傳 401：使用 `python tools/run_local.py --prompt-key` 隱藏輸入新的 key，覆蓋舊環境金鑰。
- 其他 AI 請求失敗：檢查金鑰權限、餘額和網路；不要把 key 貼到 issue。
- 網頁重載回首頁：狀態保存在 session，不是永久筆記庫。

## 對外公開自己的教材分析

私人啟動器不是公開部署方案。沿用 docs/public-release/DEPLOYMENT.md 的登入、
持久帳本、價格審查與發布驗收。現有價格政策到 2026-11-01，需重新驗證，
不能只把日期延後。此輪不宣稱雲端付費分析已開放。
