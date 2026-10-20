# 公開匿名 Cloud 驗收 — 2026-10-20

**公開匿名入口、Harmonic 與 Projectile 的實際互動均通過。**
Owner 已將分享改成 Public；本次沒有修改分享權限或再 reboot。

## 如何確認未登入

工具沒有獨立無痕 profile／清除 cookie API，因此使用正常 Cloud Sign out，確認
管理首頁顯示 Continue to sign-in，關閉先前兩個 app 分頁，再開全新的 Streamlit
session。網站直接載入，只有 Fork／Hosted with Streamlit 訪客介面，沒有 Manage
app。app 的 Google 登入也未使用。互動結束後重新載入 Cloud 管理首頁仍顯示登入
入口。這是有實際登出證據的匿名訪客測試，不宣稱是獨立無痕 profile 或刪除了所有
無關 cookies。

## 實際操作與結果

| 檢查 | 結果 |
|---|---|
| 一般訪客直接進入 | PASS；無 Cloud／Google 登入，無 API key 輸入 |
| Harmonic | PASS；真實分次操作 A=3→5、T=pi→6、phi=pi/4→-pi，SVG 曲線更新 |
| Harmonic 指標 | 水平位移3，角頻率1.0472；來源單位未指定，未冒稱秒或公尺 |
| Projectile 來源 | 第4頁 Figure5.3，明確選擇 Initial horizontal velocity |
| 真實拖曳 | (370,448)→(415,390)，release 後等待正式表格與非 pending 狀態 |
| 正式速度／角度 | 20→61.066 m/s；45→49.656 度 |
| 正式衍生值 | vx0=39.5327 m/s，高點112.52 m，高點時間4.7492 s，落地9.5412 s |
| 路徑 | 同一 session 的空間／height-time polyline 與拖曳前均不同 |
| 返回來源／再探索 | 正式 displayed metrics 完全相同，沒有重設參數 |
| 原頁不變 | 前後 PNG SHA-256 完全相同，見下方 |
| 付費 AI | 伺服器 UI 顯示停用，Analyze disabled；無生成動作，agent 付費呼叫0 |
| 設定／程式 | 無 runtime、功能、依賴、Secrets、Neon、OAuth、USD10 或 VLL_LIVE_AI 修改 |
| 測試 | 本次未啟動 unittest／full suite；既有110/562結果保留原日期 |

原頁 PNG SHA-256：`39951cfb15f3ea501012863a8849891ecd5579c8dd3ac6f6693a55f7de20d524`。
本次保存的是 viewer 的原始頁面影像前後比對；完整 PDF 仍由固定封裝 manifest 驗證。
較早 owner-session 的 raster hash 不同，不將跨 session hash 相等列為本次證據。

付費零呼叫依據：實際停用 UI、既有固定載入／local reducer 程式路徑及已提交的
request-boundary regression。沒有讀取或修改 Cloud secrets、帳單或 Neon ledger；
這不是獨立 provider billing 稽核。兩份瀏覽器 console 均未捕捉 warning/error。

受測 runtime 是 `b66f07002349f905981d9d831f539a76df3f0c02`。其後發布提交僅含
文件與證據，沒有 Python／JS／依賴或封裝教材變更。Cloud UI 無程序 Git SHA，
遠端 main 與先前 fresh clone/pull 記錄互相佐證，不宣稱取得伺服器 git rev-parse。

## 真實截圖

- [Cloud 已登出](00-cloud-signed-out.jpg)、[匿名入口](01-public-landing.jpg)、[AI 停用](02-anonymous-paid-off.jpg)
- [波形操作前](03-harmonic-before.jpg) → [操作後](04-harmonic-updated.jpg)
- [原始來源](05-projectile-source.jpg) → [拖曳前](06-projectile-before.jpg) → [正式提交後](07-projectile-drag.jpg)
- [完整軌跡](08-projectile-trajectory.jpg) → [返回 PDF](09-source-roundtrip.jpg)
- [機器可讀證據](acceptance.json)

本機路徑：`D:\Projects\visual-learning-lab\docs\day30\cloud-public-20261020`。
所有截圖來自實際公開 Cloud，未修圖／注入 fixture／改寫數值。教材：MIT OCW /
Peter Dourmashkin，CC BY-NC-SA4.0，既有[來源與第三方聲明](../../../THIRD_PARTY_NOTICES.md)仍適用。
較早私有階段的[觀察](../cloud-20261020/ACCEPTANCE.md)保留原樣與時間界線。

## 發布檢查

此文件提交範圍共31個檔案：20張真實 JPEG、5份 JSON 與6份 Markdown。
已檢查暫存區的 whitespace、JSON 可解析性、111個本機連結，以及 JPEG 檔案界線；
文字的憑證／私人 email 掃描未出現候選，截圖已檢視。未暫存日誌、bytecode、
runtime、secrets 或私人 corpus。既有未追蹤工作保留，沒有清理或覆蓋它們。
未新增依賴，未為文件更新重跑測試。正常 fast-forward push，不使用 force。
