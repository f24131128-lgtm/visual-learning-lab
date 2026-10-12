# DAY 28 — AI-SIMULATED RED TEAM

2026-10-12（Asia/Taipei）。Day28 接續 PREP；沒有重建研究封包。**真人參與者 0，真人理解／學習成效結果 0。** 本次是同一 AI agent 的五種瀏覽器操作策略，不是五位真人或五個独立受試者。

完整操作、截圖、五項 UX 問題與 before/after 見
[AI_SIMULATED_EVIDENCE.md](day28/AI_SIMULATED_EVIDENCE.md)。原始紀錄與修復後工程驗證分開保存，未混入 Study A/B。

| 情境 | 保存的真實結果 |
|---|---|
| AI01 非程式大學生 | A 3→2.90、返回 Source 成功；需自行找 Explore 下方控制。 |
| AI02 懂公式、不熟 AI | T→3.20，ω→約 1.9635、返回 Source 成功。 |
| AI03 容易放棄 | 點 Spatial build 被 offline guard 拒絕；offline 入口問題。 |
| AI04 懷疑價值 | 查來源頁；主 Atlas 選單只有 1–3，查證摘要 7–8 頁卡住，PARTIAL。 |
| AI05 自备 PDF | 公開 PDF 代理上傳成功；開始分析後只保存 loading，完成／品質 NOT TESTED。 |

主要 UX 問題：①實際控制埋在 formal 流程後（VERIFIED）；②offline 的失敗生成 CTA（VERIFIED）；③分析頁數與 Atlas 檢視範圍不直觀（VERIFIED）；④prepared lane 中文 UI／英文生成內容（VERIFIED，真人影響未測）；⑤自備 PDF 等待可能造成不確定／放棄（HYPOTHESIS，未測延遲或完成）。

最嚴重的產品缺點是 **來源→概念→可操作表示的連結仍稀疏**。滑桿能動並不證明教材 grounding、跨素材泛化或學習價值；使用者仍需要自己完成對照。

## 兩項小修復

- Source 加入按 exact semantic/material/spec/page ownership 篩出的概念控制入口；僅唯一可調 demo 可連結。Explore 把該 demo 的 controls 展開放前面，保留原圖、流程、inspectors、Graphviz、練習與返回 Source。未建立拖曳 inverse、假 handle 或來源公式語意。
- 新的獨立 offline red-team 入口把 prepared／Own PDF 說明移到操作前，停用新 AI 入口，保留底層拒絕 guard。原 frozen human 入口不改，正常 production API／validator 不改。正式入口尚無公開 prepared onboarding；此 lane 的修正不能冒稱已部署正式示例功能。

修復後真瀏覽器：Source→選 visible 概念→controls→A 3→2.90→Source→重新開 controls 仍 2.90；來源事實 A=3，PDF 原頁可見，**new AI/upload attempts: 0**。AppTest 同時檢查 PDF bytes、source_context、analysis equality。無 owner 的頁 1 公式仍不產生控制 link。

Focused 最終 **7/7 PASS，13.106 s**。兩次失敗修復 log 保留；完整 relevant suite 只啟動一次，**500/500 PASS，303.017 s，0 failures/errors/skips**，見 [DAY28_CHECKPOINT.md](DAY28_CHECKPOINT.md)。既有 Day27 489／PREP 493 只是歷史數字，沒有當成這次測試結果。

狀態：**AI-SIMULATED RED TEAM DONE**；真人研究未完成。`git diff --check` 通過；無新依賴，無 paid API／Git 提交，Day29 未開始。

## iThome 建議四張（真實截圖）

1. [修復前 Source 卡點](day28-ai-red-team/evidence/AI01-source-dead-end.jpg)：說明看得到原文，仍找不到操作。
2. [修復後 Source 控制入口](day28-ai-red-team/evidence/after-source-control-link.jpg)：概念 ownership、來源頁與誠實的無拖曳說明。
3. [真實滑桿 A=2.90](day28-ai-red-team/evidence/after-controls-change.jpg)：可用的本機參數操作。
4. [offline / Own PDF 清楚區分](day28-ai-red-team/evidence/after-offline-home.jpg)：預先生成標示與停用分析入口。

補充：[原頁返回驗證](day28-ai-red-team/evidence/after-return-source-page.jpg)、[修復前 offline failure](day28-ai-red-team/evidence/AI03-build-failure.jpg)。教材：MIT OCW / Peter Dourmashkin，Chapter 23，CC BY-NC-SA 4.0，內容未改，估計框與 UI 為產品加註。

修改 production：`app.py`、`interactive_lab.py`、`i18n.py`、`workspace/ui.py`；新增 `workspace/control_navigation.py`。新增 red-team entrypoint/tests、三份 Day28 完成文件、baseline seal、操作／截圖／測試 logs；reuse ledger 只追加此次 public API 比較。**無新增 dependency**。題目／rubric／frozen files／既有 baseline screenshots 保持 exact bytes。

正式 app：`python -m streamlit run app.py`。
修復後 offline preview：`python -X utf8 -B -m streamlit run tests/manual_day28_red_team.py --server.address 127.0.0.1 --server.port 8532 --server.headless true --browser.gatherUsageStats false`。

沒有新付費 API、沒有 commit/push/checkout/reset、沒有 Day29。真人 Study A/B 仍待原本 human review；AI 模擬不能取代它。
