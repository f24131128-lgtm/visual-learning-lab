# 最後收尾：網站、GitHub 與自己的 PDF

2026-11-14，Asia/Taipei。公開網站正常，Owner 的 Google 登入已驗證。
自己的 PDF AI 分析仍待帳本初始化與真實付費請求驗收，目前不能宣稱已開放。

- GitHub main 已正常 fast-forward 到 `f6c4b9df69b39c8620a3a682ea1ce99b353cc01b`，先前 DNS 阻礙已排除。
- 已用 Cloud DSN 的非機密主機名稱核對既有 Neon production 分支；該分支只有 `neondb`，兩張帳本表均不存在。沒有重設資料庫或預算。
- Owner 已將價格審核日期更新為 `2026-11-14`，付費開關保持空白。
- 價格政策更新固定 `prompt_cache_options.ttl=30m`，審核有效至 `2026-12-01` UTC。保留 USD 10 終身上限、USD 7 預留、每人2次分析／6次後續生成及既有失敗保留規則。
- 兩份免登入 Prepared Demo 的公開互動驗收見 [2026-10-20 紀錄](day30/cloud-public-20261020/ACCEPTANCE.md)。這不代替新 PDF 分析驗收。

## 本次驗證

公開付費安全38項聚焦測試通過（51.414秒）；補充的 SDK 實際序列化與舊審核日期拒絕測試2項通過。全部使用模擬傳輸，沒有付費請求。

完整離線回歸567項中，唯一失敗為修改封存測試檔觸發原有完整性檢查。該檔已原樣還原，受影響的7項 red-team 測試重新通過（9.818秒），沒有改預期雜湊。[完整執行紀錄](closeout-20261114/full-results.json)保留該次失敗，不冒稱全綠。

GitHub CI 的真實失敗指出乾淨 checkout 缺少舊研究輸入。已封裝必要的兩份歷史回應與三份封存報告，共26,243 bytes；只供離線測試。PDF重用現有相同檔案，不重複封裝。準備工具逐檔驗證原始 SHA-256，僅復原可逆的 checkout 換行差異，內容異動仍拒絕。3項新測試通過；從乾淨 `git archive HEAD` 成功復原14個必要輸入／位元組格式，再執行為0次寫入。原封存程式、manifest及預期雜湊不變。

## 價格依據與剩餘發布步驟

已讀官方 [價格表](https://developers.openai.com/api/docs/pricing.md)、[模型界線](https://developers.openai.com/api/docs/models/gpt-6.1-sol)及[快取政策](https://developers.openai.com/api/docs/guides/prompt-caching)。長 context 的30分鐘 cache write為 $5/M，output為 $15/M，加地區10%後使用既有 $5.50/M input與 $16.50/M output保守計費。伺服器固定30分鐘TTL並拒絕呼叫端覆寫，不能放任12小時寫入費率。

`1,050,000 × $5.50 / 1M + 16,000 × $16.50 / 1M = $6.039 < $7`。

仍需：部署新程式後取得實際 Cloud policy checksum，在已核對且兩表不存在的資料庫首次初始化，保持既有 USD10 上限；驗證 Cloud 帳本後，才將模式改為 `limited-public` 並以不含私人資料的小 PDF 實測。公開站不可使用 `private`，不得清空／重建已有帳本來解鎖額度。

沒有新增依賴。本機執行 `python tools/run_local.py`；一般 Streamlit 入口為 `streamlit run app.py`。[使用指南](USER_GUIDE.md)。

[11月13日畫面](closeout-20261113/cloud-gate.jpg)與[當日狀態](closeout-20261113/status.json)保留為歷史證據。
