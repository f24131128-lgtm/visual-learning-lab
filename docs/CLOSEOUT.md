# 最後收尾：網站、GitHub 與自己的 PDF

2026-11-13，Asia/Taipei。目標是能上傳自己的 PDF 並完成 AI 分析，不以示例或
只有 PDF 預覽冒充完成。沒有新增另一套解析器或 AI 引擎。

## 已核對

- 公開網站原本因閒置休眠；已透過正常 Wake 按鈕喚醒，首頁正常顯示。
- Owner 自行完成 Google 登入，正式網站顯示「Google 登入已驗證」。
- 同一畫面顯示「持久帳本尚未驗證」，付費 AI、PDF 上傳與開始理解仍停用。
- 本機只讀 preflight：mode 空白、public configuration 未配置；這不是雲端 secrets 的查核結果。
- 本機已有使用指南、個人啟動器、安全回報、貢獻指南及離線 CI；未為文件變更重跑整套測試。
- 既有個人啟動器的5項聚焦測試通過（10.870秒，mocked subprocess／client，未呼叫付費 API）；不代表雲端 PDF AI 已通過。
- GitHub fetch 兩次均因 `Could not resolve host: github.com` 失敗；不能將本機成果說成已推送。

[正式畫面](closeout-20261113/cloud-gate.jpg) · [受控狀態紀錄](closeout-20261113/status.json)

## 仍須完成才可宣稱收工

1. Owner 登入 Streamlit Cloud 管理平台。網站 Google 登入與部署平台登入是不同 session。
2. 讀實際 Cloud 日誌的受控原因，確認既有專用 Project 與持久帳本配置；不把金鑰、連線字串或 OAuth cookie 貼進聊天／Git／截圖。
3. 價格政策 `PRICE_VALID_UNTIL=2026-11-01` 已過期。重新審查並實作相容的政策更新；日期是 policy fingerprint 的一部分，不能僅延後日期或重設資料庫來取得新額度。
4. 保留 USD10 終身上限、既有使用量與 pending/uncertain 紀錄。通過帳本／登入／價格驗收後，才發布 `limited-public`；公開網站不可使用 `private`。
5. 以一份不含私人資料、2頁／2MiB以內的教材，實際走登入→上傳→AI分析→Source，驗證額度及錯誤隔離。成功前不宣稱公開 PDF AI 可用。
6. 網路恢復後重新核對遠端 main，只提交已檢查檔案並正常 fast-forward push。

## 本次價格文件核對

已讀官方 [Standard pricing data](https://developers.openai.com/api/docs/pricing.md)
與 [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol)。Standard
長 context 表列 input $4/M、output $15/M，30m cache write $5/M、12h write $10/M；
地區處理另有10%加成。現有保守計費 $5.50/M input、$16.50/M output 不能直接宣稱
涵蓋所有 cache retention。因此本輪沒有僅延長日期或啟用付費。

模型仍為既有 gpt-6.1-sol；沒有自行切換模型、調高預算或呼叫付費 API。
目前證據不足以證明 Cloud 帳本的具體失敗原因，需以管理日誌核對，不能由本機配置推定。

## 個人使用的既有途徑

本機可用 `python tools/run_local.py`，以隱藏輸入提供自己的 API key，之後上傳 PDF
並明確啟動 AI。這會使用自己的 API 額度，並非免費離線分析；請勿把私人模式對外公開。
[使用指南](USER_GUIDE.md)。沒有新增依賴。
