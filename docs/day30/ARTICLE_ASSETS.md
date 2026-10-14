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
