# Cloud 實際驗收 — 2026-10-20

這是 owner 尚未改為 Public 時的歷史觀察。後續已完成[登出後公開匿名驗收](../cloud-public-20261020/ACCEPTANCE.md)；以下數字與截圖保留原始階段，不改寫成後來的結果。

**兩份示例的 Cloud 互動功能通過；公開匿名驗收未通過。**
Cloud 分享面板的 Make this app public 在載入完成後仍未勾選，沒有修改它。

| 項目 | 實際結果 |
|---|---|
| 授權重啟 | 執行一次；09:20:45 起重新 clone main，09:21:00.459 啟動，Asia/Taipei |
| main | `b66f07002349f905981d9d831f539a76df3f0c02`；遠端 SHA 與新 clone/pull main 互相佐證，Cloud UI 無程序 SHA |
| ImportError | 本日重啟前已未再現；重啟後兩示例可載入，真實 logs 無新 ImportError/uncaught traceback |
| Cloud runtime | Python 3.12.15 / Streamlit 1.66.0；Cloud 自動替換 pyarrow 26 為 24，未手動修改依賴 |
| 簡諧 | 真實滑桿分次提交 A=5、T=6、φ=−π；SVG 重繪，位移=3、角頻率=1.0472 |
| 拋體 | 真實 pointer drag (370,298)→(415,240)，release 後等正式表格回覆 |
| 拋體正式值 | v0=60.895 m/s，角度=49.519°，vx0=39.5327 m/s，高點=111.46 m，落地=9.4956 s |
| 軌跡 | 空間與 height/time SVG polyline 均不同於另一個預設 session；完整軌跡截圖已保存 |
| 往返 | 返回第4頁、重新探索後的 displayed metrics 完全相同；原頁 PNG 與獨立未探索 session SHA 相同 |
| app Google 登入 | 全程未登入；驗證 Google 登入按鈕仍可見，分析按鈕 disabled |
| 公開匿名 | **未通過**；Cloud owner cookie 仍在，public checkbox=false，沒有真正 cookie 隔離的無痕驗收 |
| 付費 AI | UI 明示伺服器關閉；固定載入／local reducer 無生成動作，沒有執行付費呼叫；不是 billing/Neon 稽核 |
| 設定變更 | Secrets / Neon / Google OAuth / USD10 / VLL_LIVE_AI / 分享權限均未修改 |
| 程式修改 | 無；本次只新增驗收證據並修正文件的舊部署狀態 |

初次拖曳因 focus 導致頁面位置變動而未命中，值仍為20/45。重新依穩定截圖定位後
才完成拖曳。預覽曾顯示不同的高點／時間，正式回覆後才記錄111.46與9.4956，
沒有把 tentative preview 當成 committed state。

原頁 PNG SHA-256：`222f7857f26d5e74bf1e6a0bcf988ed32a06b948f4d0cb3344e54a025c44455d`。
本次比對的是 Cloud viewer 的原始頁面影像；完整 PDF 的 hash 仍由封裝 manifest 驗證。

如需公開：由 owner 自行 Share → Invite → 開啟 Make this app public，再以不含
Cloud／Google 登入的新無痕瀏覽器驗收。這項權限更動不在本次一次 reboot 的授權內。

## 真實截圖與機器可讀證據

- [簡諧原始](01-harmonic-before.jpg) → [三參數更新後](02-harmonic-updated.jpg)
- [原始 PDF](03-projectile-source.jpg) → [端點拖曳前](04-projectile-before.jpg) → [提交後](05-projectile-drag.jpg)
- [完整軌跡與數值](06-projectile-trajectory.jpg) → [返回原始來源](08-source-roundtrip.jpg)
- [app 未登入且 AI 關閉](07-paid-off-anonymous.jpg)、[Cloud public 關閉](09-sharing-private.jpg)
- [精確驗收記錄](acceptance.json)、[波形 DOM](harmonic-dom-evidence.json)、[拋體 DOM](projectile-dom-evidence.json)

本機絕對路徑：`D:\Projects\visual-learning-lab\docs\day30\cloud-20261020`。
所有畫面均為實際 Cloud，未修圖、未注入 fixture、未更改數字或製造拖曳幀。
教材：MIT OCW / Peter Dourmashkin，CC BY-NC-SA 4.0；詳見既有 THIRD_PARTY_NOTICES。

正式 runtime 無變更，沒有重跑多分鐘 full suite。既有最終 focused 110/110、full
562/562 是2026-10-15的證據，不冒充今日新跑的全套測試。
今日額外啟動 test_day30 補測，但數分鐘仍無 completed unittest result，已只中止
該自有程序；不能列為通過，log 保留於本機。Cloud 功能結果來自上面的真實操作。

本次文件與證據只存於工作區，未推送，避免改變指定的 main `b66f070` 或觸發
另一輪 Cloud 更新。最後程式與依賴均未改動。
