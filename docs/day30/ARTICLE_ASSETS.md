# Day30 真實畫面素材

所有新圖來自實際 Streamlit app；不使用示意圖、生成 UI、合成動畫或改寫數值。
`tests/manual_day30.py` 只觀察正式入口、阻擋 provider，沒有注入 fixture。
Cloud 驗收另記於 DAY30_EVIDENCE；本機圖不可標成 Cloud。

| 檔案 | 用途 |
|---|---|
| [01-landing.jpg](01-landing.jpg) | 免登入、兩個真正可用的準備示例入口 |
| [02-harmonic.jpg](02-harmonic.jpg) | 真實波形、單位、來源參考與控制 |
| [03-harmonic-updated.jpg](03-harmonic-updated.jpg) | 實際操作後波形與衍生值 |
| [04-projectile-source.jpg](04-projectile-source.jpg) | 原始 Figure 5.3 與 vx0 的來源支持 |
| [05-projectile-drag.jpg](05-projectile-drag.jpg) | 真實 pointer release 後向量／軌跡／數值 |
| [06-source-roundtrip.jpg](06-source-roundtrip.jpg) | 返回原頁並保留探索值 |

建議 README hero 使用 harmonic 操作後圖，文章再以來源 → 拖曳 → 返回的三張
補足證據。圖保持原截圖，不改數字／框／曲線，不把舊圖重新命名成新實驗。
桌面與窄版檢查尺寸、實際操作數值見 acceptance；截圖可視範圍不等於效能量測。

教材圖像：MIT OpenCourseWare / Peter Dourmashkin，8.01SC Chapters 5 / 23，
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)。來源內容未改；
產品 UI、估計框與模型探索是附加內容，不暗示 MIT 背書。完整來源連結與條件見
[THIRD_PARTY_NOTICES](../../THIRD_PARTY_NOTICES.md)。保持非商業展示與適用相同方式分享條件。

沒有產生 GIF／MP4；可選的錄影不阻擋交付。若日後錄製，必須錄下真實拖曳與
release 等待，不能用手作幀模擬反應，也不能暴露帳號、secrets 或 private corpus。

本機素材根目錄：`D:\Projects\visual-learning-lab\docs\day30`。上表六個檔名就是各張截圖的本機檔名。

## 2026-10-20 實際 Cloud 畫面（改為 Public 前）

新增素材位於 `D:\Projects\visual-learning-lab\docs\day30\cloud-20261020`：
[入口](cloud-20261020/00-landing.jpg)、[原始波形](cloud-20261020/01-harmonic-before.jpg)、
[更新後波形](cloud-20261020/02-harmonic-updated.jpg)、[來源](cloud-20261020/03-projectile-source.jpg)、
[拖曳前](cloud-20261020/04-projectile-before.jpg)、[拖曳提交後](cloud-20261020/05-projectile-drag.jpg)、
[完整軌跡](cloud-20261020/06-projectile-trajectory.jpg)、[付費關閉／未登入](cloud-20261020/07-paid-off-anonymous.jpg)、
[來源往返](cloud-20261020/08-source-roundtrip.jpg)、[未公開的分享狀態](cloud-20261020/09-sharing-private.jpg)。

這些來自 owner 可存取的 Cloud 與新的 app session，app 內未 Google 登入。
Cloud public toggle 關閉，不能標成公開匿名驗收成功。見[本次記錄](cloud-20261020/ACCEPTANCE.md)。

## 2026-10-20 公開匿名驗收畫面

Owner 改為 Public 後，先登出 Cloud、關閉舊分頁，再開新 app session。以下均為
實際已登出訪客畫面，與前面的 owner-session 證據分開，沒有將舊圖改名成新驗收。

素材根目錄：`D:\Projects\visual-learning-lab\docs\day30\cloud-public-20261020`。

| 檔案 | 用途 |
|---|---|
| [00-cloud-signed-out.jpg](cloud-public-20261020/00-cloud-signed-out.jpg) | Cloud 顯示 Continue to sign-in，沒有帳號或私人資料 |
| [01-public-landing.jpg](cloud-public-20261020/01-public-landing.jpg) | 匿名可進入，訪客介面沒有 Manage app |
| [02-anonymous-paid-off.jpg](cloud-public-20261020/02-anonymous-paid-off.jpg) | Google 未登入、新 AI 生成停用 |
| [03-harmonic-before.jpg](cloud-public-20261020/03-harmonic-before.jpg) | 調參前真實波形 |
| [04-harmonic-updated.jpg](cloud-public-20261020/04-harmonic-updated.jpg) | A/T/phi 更新後波形、指標與滑桿；新版 README hero |
| [05-projectile-source.jpg](cloud-public-20261020/05-projectile-source.jpg) | Figure 5.3 原始圖與編譯初值 |
| [06-projectile-before.jpg](cloud-public-20261020/06-projectile-before.jpg) | 20 m/s、45 度的端點 |
| [07-projectile-drag.jpg](cloud-public-20261020/07-projectile-drag.jpg) | 真實拖曳 release 後正式值61.066 /49.656 |
| [08-projectile-trajectory.jpg](cloud-public-20261020/08-projectile-trajectory.jpg) | 完整軌跡及指標 |
| [09-source-roundtrip.jpg](cloud-public-20261020/09-source-roundtrip.jpg) | 原圖不變，保留探索值 |

[驗收方法、限制與 JSON](cloud-public-20261020/ACCEPTANCE.md)。這是登出後新 session，
不是獨立無痕 profile；不宣稱刪除了瀏覽器所有 cookies。既有 MIT 教材授權條件仍適用。
