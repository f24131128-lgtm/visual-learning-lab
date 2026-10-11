# POST_FIX — human-approved A-axis review

The human reviewer approved the following POST_FIX semantic/source results on 2026-10-11. These are human decisions, not model-generated scores. The frozen baseline remains PASS 4 / PARTIAL 4 / FAIL 2 and has not been rescored or overwritten. This replay is not an untouched holdout.

| Case | Frozen baseline A-axis | Approved POST_FIX A-axis | Basis |
|---|---|---|---|
| Circular motion | PARTIAL | PARTIAL | Carried forward unchanged; no new live semantic review in this five-case replay. |
| SHM | PASS | PASS | Explicit human POST_FIX review. |
| RC | PARTIAL | PARTIAL | Explicit human POST_FIX review. |
| Signals | PASS | PASS | Explicit human POST_FIX review. |
| Regression | FAIL | PASS | Explicit human POST_FIX review. |
| Probability | FAIL | PARTIAL | Explicit human POST_FIX review. |
| Search algorithm | PARTIAL | PARTIAL | Carried forward unchanged; no new live semantic review in this five-case replay. |
| Big-O | PARTIAL | PARTIAL | Carried forward unchanged; offline annotation is separate from new model generation. |
| NASA spectrum table | PASS | PASS | Carried forward unchanged; no new live semantic review in this five-case replay. |
| Debugging | PASS | PASS | Carried forward unchanged; offline canary evidence is separate from new model generation. |

Approved overall POST_FIX A-axis: **PASS 5 / 10, PARTIAL 5 / 10, FAIL 0 / 10**. All ten cases remain in the denominator. The five carried-forward assignments are not represented as five additional live generations or new semantic reviews.

## Human-approved reasons

- Regression: source-fixed empirical R 與 hypothetical exploration 已分離；Lab 拒絕但 static/formal fallback 不再誤導來源事實。
- Probability: source facts 與 hypothetical exploration 已分離，但 finite event membership / probability_sets runtime 尚未完整建立。
- RC: source charging/discharging facts 與 hypothetical controls 已分離；但 Main 對來源「符號筆誤」的說法尚未人工核對，因此維持 PARTIAL。
- SHM: 來源 facts、hypothetical exploration 與 derived quantities 分離，無 damping/forcing invention，維持 PASS。
- Signals: 互動能力退化，但 source semantics 保持正確並誠實 static fallback，A-axis 維持 PASS；engineering capability loss 另外記錄。

These reasons follow the human instruction and the existing [review packet](post-fix-semantic-review.md). No additional semantic score is inferred from schema, compilation, validation, tests, or ownership links.

## Separate engineering limitations

- Regression: its Lab proposal was rejected because each fitted curve exceeds the existing five-numeric-name expression bound. The actual result is static/formal; there is no installed correlation exploration runtime.
- Probability: the structural planner was accepted, but probability_sets compilation was rejected by the learning-goal length rule. The accepted Numeric Lab supplies hypothetical overlap exploration, not a completed finite-event membership runtime.
- RC: the planner was rejected; the independently validated Numeric Lab and formal views remain available. The human review leaves the source-sign-error claim unresolved.
- SHM: the accepted Lab explores amplitude, period and phase. The planner reason describes k/m/initial-condition controls that are not the actual Lab controls.
- Signals: the new Lab proposal was rejected because the summed waveform uses seven numeric names. The prior interactive waveform capability is absent in this attempt; formal/static fallback remains available. This engineering capability loss does not change the human-approved A-axis PASS.

Candidate C remains unresolved. No planner ranking, representation family, renderer, or feature change is authorized by this review. No new model calls, commit, or push are part of acceptance completion. Original POST_FIX manifests, review packet, test history, and frozen baseline artifacts remain historical evidence; the new approval and final validation records are separate additions under this directory.
