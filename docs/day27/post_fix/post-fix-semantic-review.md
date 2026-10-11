# POST_FIX — human semantic/source review

This replay is not an untouched holdout. The frozen baseline A-axis assignments remain PASS 4 / PARTIAL 4 / FAIL 2. No post-fix A verdict is assigned. Schema, validator and browser checks are engineering evidence only.

Raw proposals, accepted runtime declarations and explicit offline annotations are separate below. A rejected proposal is not presented as a working control. Evaluation page numbers are renumbered subset pages; physical pages are mapped explicitly.

Candidate C ranking is unchanged. A different planner result in one new generation does not establish a general selection repair.

## regression — OpenIntro Statistics 4e screen-reader edition: Least Squares Regression

Frozen baseline human A: **FAIL** (unchanged). [Source](https://www.openintro.org/go/?id=os4_for_screen_reader).

Source evidence (frozen concise paraphrases; physical PDF pages):
- p.355: The gift-aid example uses a sample of fifty freshmen and compares fitted lines on the observed scatterplot. Formula/concept: Least-squares fitting of gift aid versus family income. Condition: The sample and plotted empirical points are source facts.
- p.358: The fitted slope uses standard deviations and correlation, and the fitted line passes through the sample means. Formula/concept: b1 = (s_y/s_x) R. Condition: Means 101780/19940; SDs 63200/5460; R = -0.499.
- p.359: The source reports the fitted line and interprets its estimated coefficients. Formula/concept: Rounded worked line: aid_hat = 24327 - 0.0431*income (dollars); software summary intercept 24319.3. Condition: Fitted estimates are fixed results; prediction input can vary within the observed range.
- p.360: Prediction is an estimate subject to cohort and model limitations. Formula/concept: Prediction limitations. Condition: Do not infer a causal or guaranteed financial-aid rule.

Evaluation → physical mapping: `{"1": 355, "2": 356, "3": 357, "4": 358, "5": 359, "6": 360}`.

Baseline planner/runtime: `dynamic` / `existing validated numeric lab`. Baseline Lab parameter declarations:
- correlation_and_line: corr=-0.499 [-0.6, 0.6]

New main analysis: Least squares regression fits a line by minimizing the sum of squared residuals. The section explains how to check whether a linear model is appropriate, calculate its slope and intercept from summary statistics, and interpret predictions responsibly. In the Elmhurst example, higher family income is associated with lower gift aid, but the observational data do not establish causation.

New planner/engineering observations:

| Observation | Actual result |
|---|---|
| Planner | accepted |
| Family | static |
| Compiler | NOT_APPLICABLE |
| Compiler rejection | None |
| Lab demos rejected | 1 |
| Atlas validator | accepted |
| Pipeline exceptions | [] |

Planner reason (model text): Use a structured derivation linking the summary statistics to b₁ = (sᵧ/sₓ)R, the mean-point constraint ŷ − ȳ = b₁(x − x̄), b₀ = ȳ − b₁x̄, and the final prediction equation. This makes clear why the fitted line passes through (x̄, ȳ). Comparing parameter values would offer useful insight, but the numeric lab is not ready. The available process mechanics cannot perform the required arithmetic, so a静

### Proposed Lab `regression_pivot` — runtime rejected

Observe how R changes the slope and intercept while every constructed line passes through (x̄, ȳ).

Formula display: `b₁ = (sᵧ/sₓ)R; b₀ = ȳ − b₁x̄; ŷ = ȳ + (sᵧ/sₓ)R(x − x̄). Income and aid are in dollars. The baseline is reconstructed from the reported rounded summaries, not the full-precision software fit. Changing R is hypothetical, not a reanalysis of the original students.`.

Independent/runtime axis: `{   "id": "income_axis",   "label": "Family income (USD; selected display range)",   "min": 0,   "max": 250000,   "points": 400,   "semantic_role": "independent_variable",   "provenance": "source_variable" }`.

Source facts declared by the model (source fidelity is for the reviewer):

| ID | Value | Pages (evaluation → physical) | Evidence declared |
|---|---|---|---|
| income_mean | 101780 USD | 4→358 | Figure 8.13 reports x̄ = $101,780. |
| aid_mean | 19940 USD | 4→358 | Figure 8.13 reports ȳ = $19,940. |
| income_sd | 63200 USD | 4→358 | Figure 8.13 reports sₓ = $63,200. |
| aid_sd | 5460 USD | 4→358 | Figure 8.13 reports sᵧ = $5,460. |
| reported_correlation | -0.499 dimensionless | 1→355, 4→358 | The footnote and summary table report R = −0.499. |

Controls/read-only parameters:

| ID | Provenance | Source baseline ref | Min / initial / max | Exposed | Semantic refs |
|---|---|---|---|---|---|
| explore_correlation | hypothetical_exploration | reported_correlation | -1 / -0.499 / 1 | True | ['summary_inputs'] |

Parameter evidence `explore_correlation`: The source gives b₁ = (sᵧ/sₓ)R. This control explores hypothetical correlations while retaining the reported summary statistics; it does not change the immutable observed correlation.

Series/metrics (declared derived expressions and ownership):

- series.baseline_aid_curve: `aid_mean + (aid_sd / income_sd) * reported_correlation * (income_axis - income_mean)`; provenance `derived`; refs `['fitted_prediction']`.
- series.explored_aid_curve: `aid_mean + (aid_sd / income_sd) * explore_correlation * (income_axis - income_mean)`; provenance `derived`; refs `['fitted_prediction']`.
- derived_metrics.explored_slope: `(aid_sd / income_sd) * explore_correlation`; provenance `derived`; refs `['calculate_slope']`.
- derived_metrics.explored_intercept: `aid_mean - (aid_sd / income_sd) * explore_correlation * income_mean`; provenance `derived`; refs `['calculate_intercept']`.

Actual Lab rejection: `Invalid declared variables.`. Source facts and controls in this proposal were not installed in the runtime.
- Expression `baseline_aid_curve` references 6 numeric names: `['aid_mean', 'aid_sd', 'income_axis', 'income_mean', 'income_sd', 'reported_correlation']`. Existing safe_math per-expression limit: 5.
- Expression `explored_aid_curve` references 6 numeric names: `['aid_mean', 'aid_sd', 'explore_correlation', 'income_axis', 'income_mean', 'income_sd']`. Existing safe_math per-expression limit: 5.

Source → representation observations:
```json
{
  "semantic_id": "calculate_intercept",
  "region_id": "p5-intercept-step",
  "representation_ids": [
    "calculate_intercept"
  ],
  "ownership": {
    "semantic_id": "calculate_intercept",
    "source_region_ids": [
      "p5-summary-method",
      "p5-intercept-step"
    ],
    "source_pages": [
      5
    ],
    "support": [
      {
        "region_id": "p5-summary-method",
        "page": 5,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p5-intercept-step",
        "page": 5,
        "kind": "estimated_region",
        "confidence": "high"
      }
    ],
    "representation_ids": [
      "calculate_intercept"
    ],
    "manipulation_target_ids": [],
    "formal_parameter_ids": [],
    "manipulable": false,
    "reason_not_manipulable": "No validated direct manipulation is available; use the formal view and existing controls."
  },
  "direct_manipulation": {
    "available": false,
    "targets": [],
    "absence_is_not_automatic_failure": true
  },
  "source_roundtrip": true,
  "source_pdf_unchanged": true,
  "atlas_immutable": true,
  "post_compilation_api_delta": 0
}
```

Objective review flags:
- New generated semantic IDs are internal to this material/attempt. Do not treat renamed IDs across generations as proof of semantic equivalence.
- Source facts/evidence text above are model declarations; validation checks their structure/pages and prevents writes, not their truth against the PDF.
- Hypothetical controls remain subject to review for pedagogical/source appropriateness, even when provenance and numeric safety pass.
- Baseline `corr=-0.499` was adjustable. New raw proposal declares `reported_correlation=-0.499` separately from `explore_correlation`; the new Lab is rejected, so no runtime correlation control exists in this attempt. The frozen expectation does not preauthorize an adjustable trial fit.

Reviewer (leave blank):

- Core source understanding: [ ]
- Fixed / adjustable: [ ]
- Representation appropriateness: [ ]
- Source fidelity: [ ]
- Unsupported invention: [ ]
- Post-fix overall A-axis: [ PASS / PARTIAL / FAIL ]

## probability — OpenIntro Statistics 4e screen-reader edition: Defining Probability

Frozen baseline human A: **FAIL** (unchanged). [Source](https://www.openintro.org/go/?id=os4_for_screen_reader).

Source evidence (frozen concise paraphrases; physical PDF pages):
- p.93: A fair die illustrates disjoint individual outcomes and their addition rule. Formula/concept: Addition for disjoint outcomes. Condition: Six source-defined die outcomes.
- p.94: The die events are A={1,2}, B={4,6} and D={2,3}; A and B are disjoint, while A and D share outcome 2. Formula/concept: Membership and overlap. Condition: Source event membership must remain unchanged.
- p.97: Diamonds and face cards require subtracting overlap when computing inclusive-or probability. Formula/concept: P(A union B) = P(A) + P(B) - P(A intersection B). Condition: 52-card example counts are fixed; no unjustified uniform aggregation.
- p.98: The two-dice sum table assigns unequal probabilities to sums 2 through 12. Formula/concept: Weights 1,2,3,4,5,6,5,4,3,2,1 divided by 36. Condition: The sums are not uniformly likely.

Evaluation → physical mapping: `{"1": 93, "2": 94, "3": 95, "4": 96, "5": 97, "6": 98, "7": 99, "8": 100}`.

Baseline planner/runtime: `dynamic` / `existing validated numeric lab`. Baseline Lab parameter declarations:
- overlap_lab: prob_a=0.3333333333333333 [0.25, 0.5], prob_b=0.3333333333333333 [0.25, 0.5]

New main analysis: Probability calculations depend on how events relate as sets of outcomes. Disjoint events have no overlap, so their probabilities add directly. Overlapping events require subtracting the intersection to avoid double counting. Probability distributions assign valid probabilities to all disjoint outcomes, and complements provide a shortcut by describing everything outside an event.

New planner/engineering observations:

| Observation | Actual result |
|---|---|
| Planner | accepted |
| Family | structural |
| Compiler | rejected |
| Compiler rejection | learning goal is empty or too long. |
| Lab demos rejected | 0 |
| Atlas validator | accepted |
| Pipeline exceptions | [] |

Planner reason (model text): Finite outcome sets and their membership relationships are the central structure. A separately built structural exploration could let learners select die outcomes or cards and compare intersection, inclusive union, disjointness, and complement. This makes double counting visible and connects membership to P(A ∪ B) = P(A) + P(B) − P(A ∩ B) and P(Aᶜ) = 1 − P(A). The supplied distributions also show,

Selected compiler raw proposal (retained even when rejected; not installed as a valid runtime):
```json
{
  "domain": "probability_sets",
  "scene_version": "1.1",
  "title": "Die Rolls: Disjoint Events, Overlap, and Complements",
  "learning_goal": "Identify events within a six-outcome sample space, distinguish disjoint and overlapping events, and calculate probabilities using unions, intersections, and complements.",
  "source_pages": [
    1,
    2,
    5,
    8
  ],
  "outcomes": [
    {
      "id": "roll_1",
      "label": "1",
      "path": [],
      "weight": 1,
      "source_pages": [
        1
      ]
    },
    {
      "id": "roll_2",
      "label": "2",
      "path": [],
      "weight": 1,
      "source_pages": [
        1
      ]
    },
    {
      "id": "roll_3",
      "label": "3",
      "path": [],
      "weight": 1,
      "source_pages": [
        1
      ]
    },
    {
      "id": "roll_4",
      "label": "4",
      "path": [],
      "weight": 1,
      "source_pages": [
        1
      ]
    },
    {
      "id": "roll_5",
      "label": "5",
      "path": [],
      "weight": 1,
      "source_pages": [
        1
      ]
    },
    {
      "id": "roll_6",
      "label": "6",
      "path": [],
      "weight": 1,
      "source_pages": [
        1
      ]
    }
  ],
  "events": [
    {
      "id": "event_a",
      "label": "A: 1 or 2",
      "outcome_ids": [
        "roll_1",
        "roll_2"
      ],
      "source_pages": [
        2
      ]
    },
    {
      "id": "event_b",
      "label": "B: 4 or 6",
      "outcome_ids": [
        "roll_4",
        "roll_6"
      ],
      "source_pages": [
        2
      ]
    },
    {
      "id": "event_d",
      "label": "D: 2 or 3",
      "outcome_ids": [
        "roll_2",
        "roll_3"
      ],
      "source_pages": [
        2
      ]
    }
  ],
  "views": [
    {
      "id": "view_outcomes",
      "type": "sample_space",
      "title": "Six equally likely outcomes",
      "semantic_ids": [
        "roll_1",
        "roll_2",
        "roll_3",
        "roll_4",
        "roll_5",
        "roll_6",
        "event_a",
        "event_b",
        "event_d",
        "focus_a_union_b",
        "focus_a_union_d",
        "focus_a_intersection_d",
        "focus_not_a"
      ]
    },
    {
      "id": "view_sets",
      "type": "set",
      "title": "Event membership and overlap",
      "semantic_ids": [
        "roll_1",
        "roll_2",
        "roll_3",
        "roll_4",
        "roll_5",
        "roll_6",
        "event_a",
        "event_b",
        "event_d",
        "focus_a_union_b",
        "focus_a_union_d",
        "focus_a_intersection_d",
        "focus_not_a"
      ]
    },
    {
      "id": "view_formulas",
      "type": "formula",
      "title": "Event probabilities",
      "semantic_ids": [
        "event_a",
        "event_b",
        "event_d",
        "focus_a_union_b",
        "focus_a_union_d",
        "focus_a_intersection_d",
        "focus_not_a"
      ]
    },
    {
      "id": "view_simulation",
      "type": "monte_carlo",
      "title": "Simulate repeated die rolls",
      "semantic_ids": [
        "roll_1",
        "roll_2",
        "roll_3",
        "roll_4",
        "roll_5",
        "roll_6",
        "event_a",
        "event_b",
        "event_d",
        "focus_a_union_b",
        "focus_a_union_d",
        "focus_a_intersection_d",
        "focus_not_a"
      ]
    }
  ],
  "focus_targets": [
    {
      "id": "focus_a_union_b",
      "label": "A or B: disjoint union",
      "expression": "event_a | event_b",
      "source_pages": [
        2
      ]
    },
    {
      "id": "focus_a_union_d",
      "label": "A or D: overlapping union",
      "expression": "event_a | event_d",
      "source_pages": [
        2,
        5
      ]
    },
    {
      "id": "focus_a_intersection_d",
      "label": "A and D: shared outcomes",
      "expression": "event_a & event_d",
      "source_pages": [
        2
      ]
    },
    {
      "id": "focus_not_a",
      "label": "Complement of A",
      "expression": "~event_a",
      "source_pages": [
        2,
        8
      ]
    }
  ],
  "parameters": []
}
```

### Proposed Lab `demo_overlap` — runtime accepted

See why increasing shared probability reduces a union when event probabilities are otherwise held constant.

Formula display: `P(A)=13/52=1/4; b=P(B); r is the fraction of B shared with A. P(A∩B)=rb; P(A∪B)=1/4+b−rb. Hypothetical exploration: 0≤b≤1/4 and 0≤r≤1. Actual card example: b=12/52 and r=3/12.`.

Independent/runtime axis: `{   "id": "b_probability",   "label": "Hypothetical probability P(B)",   "min": 0,   "max": 0.25,   "points": 400,   "semantic_role": "independent_variable",   "provenance": "hypothetical_exploration" }`.

Source facts declared by the model (source fidelity is for the reviewer):

| ID | Value | Pages (evaluation → physical) | Evidence declared |
|---|---|---|---|
| deck_size | 52 cards | 4→96 | The source describes a regular deck containing 52 unique cards. |
| diamond_count | 13 cards | 4→96 | The diamond event contains 13 cards. |
| face_count | 12 cards | 4→96 | Jacks, queens, and kings give 12 face cards. |
| shared_count | 3 cards | 4→96, 5→97 | J♦, Q♦, and K♦ belong to both source events. |

Controls/read-only parameters:

| ID | Provenance | Source baseline ref | Min / initial / max | Exposed | Semantic refs |
|---|---|---|---|---|---|
| shared_fraction | hypothetical_exploration | None | 0 / 0.25 / 1 | True | ['intersection'] |

Parameter evidence `shared_fraction`: The General Addition Rule explicitly subtracts intersection probability. This fraction and its adjustment range are exploratory, not reported measurements. The chosen domain ensures valid event-region probabilities.

Series/metrics (declared derived expressions and ownership):

- series.union_probability: `diamond_count/deck_size + b_probability - shared_fraction*b_probability`; provenance `derived`; refs `['union', 'general_addition']`.
- series.intersection_probability: `shared_fraction*b_probability`; provenance `derived`; refs `['intersection']`.

Trusted local commit observations:
```json
{
  "demo_id": "demo_overlap",
  "source_facts": [
    {
      "id": "deck_size",
      "label": "Cards in the source deck",
      "unit": "cards",
      "value": 52.0,
      "provenance": "source_fixed",
      "source_pages": [
        4
      ],
      "source_evidence": "The source describes a regular deck containing 52 unique cards."
    },
    {
      "id": "diamond_count",
      "label": "Diamonds in the source deck",
      "unit": "cards",
      "value": 13.0,
      "provenance": "source_fixed",
      "source_pages": [
        4
      ],
      "source_evidence": "The diamond event contains 13 cards."
    },
    {
      "id": "face_count",
      "label": "Face cards in the source deck",
      "unit": "cards",
      "value": 12.0,
      "provenance": "source_fixed",
      "source_pages": [
        4
      ],
      "source_evidence": "Jacks, queens, and kings give 12 face cards."
    },
    {
      "id": "shared_count",
      "label": "Diamond face cards in the source deck",
      "unit": "cards",
      "value": 3.0,
      "provenance": "source_fixed",
      "source_pages": [
        4,
        5
      ],
      "source_evidence": "J♦, Q♦, and K♦ belong to both source events."
    }
  ],
  "source_baseline_immutable": true,
  "initial_values": {
    "shared_fraction": 0.25
  },
  "current_values": {
    "shared_fraction": 0.6
  },
  "commits": [
    {
      "id": "shared_fraction",
      "initial": 0.25,
      "current": 0.6
    }
  ],
  "rejections": [],
  "unknown_commit_rejected": true,
  "curve_changed": true
}
```

Source → representation observations:
```json
{
  "semantic_id": "general_addition",
  "region_id": "p5_addition_box",
  "representation_ids": [
    "general_addition",
    "lab:demo_overlap:series:union_probability"
  ],
  "ownership": {
    "semantic_id": "general_addition",
    "source_region_ids": [
      "p5_card_calculation",
      "p5_addition_box",
      "p5_addition_formula",
      "p5_disjoint_practice"
    ],
    "source_pages": [
      5
    ],
    "support": [
      {
        "region_id": "p5_card_calculation",
        "page": 5,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p5_addition_box",
        "page": 5,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p5_addition_formula",
        "page": 5,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p5_disjoint_practice",
        "page": 5,
        "kind": "estimated_region",
        "confidence": "high"
      }
    ],
    "representation_ids": [
      "general_addition",
      "lab:demo_overlap:series:union_probability"
    ],
    "manipulation_target_ids": [],
    "formal_parameter_ids": [],
    "manipulable": false,
    "reason_not_manipulable": "No validated direct manipulation is available; use the formal view and existing controls."
  },
  "direct_manipulation": {
    "available": false,
    "targets": [],
    "absence_is_not_automatic_failure": true
  },
  "source_roundtrip": true,
  "source_pdf_unchanged": true,
  "atlas_immutable": true,
  "post_compilation_api_delta": 0
}
```

Objective review flags:
- New generated semantic IDs are internal to this material/attempt. Do not treat renamed IDs across generations as proof of semantic equivalence.
- Source facts/evidence text above are model declarations; validation checks their structure/pages and prevents writes, not their truth against the PDF.
- Hypothetical controls remain subject to review for pedagogical/source appropriateness, even when provenance and numeric safety pass.
- Baseline used adjustable `prob_a/prob_b` and no finite-set scene. New Lab uses a card-deck overlap experiment and declared immutable deck/count facts. The structural compiler attempt is rejected. Review finite event membership and exact source probabilities separately from the hypothetical overlap fraction.

Reviewer (leave blank):

- Core source understanding: [ ]
- Fixed / adjustable: [ ]
- Representation appropriateness: [ ]
- Source fidelity: [ ]
- Unsupported invention: [ ]
- Post-fix overall A-axis: [ PASS / PARTIAL / FAIL ]

## circuits — 6.002 Lecture 12: First Order Circuits

Frozen baseline human A: **PARTIAL** (unchanged). [Source](https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/84f4b553fc6a1ddd7007465041c4e213_6002_l12.pdf).

Source evidence (frozen concise paraphrases; physical PDF pages):
- p.6: The capacitor node equation produces a first-order RC differential equation. Formula/concept: RC dv_C/dt + v_C = V_I. Condition: The stated first-order circuit topology.
- p.7: The input is constant and the initial capacitor voltage is given. Formula/concept: v_C(0) = V_0. Condition: Constant input and specified initial condition.
- p.12: The complete solution approaches the input voltage with time constant RC. Formula/concept: v_C(t) = V_I + (V_0 - V_I) exp(-t/(RC)); tau = RC. Condition: Source solution and first-order assumptions.
- p.13: Charging/discharging examples use input and initial voltage pairs 5/0 and 0/5 volts. Formula/concept: Exponential charging/discharging. Condition: The two source example voltage pairs are fixed facts, distinct from a labeled hypothetical exploration.

Evaluation → physical mapping: `{"1": 6, "2": 7, "3": 8, "4": 9, "5": 10, "6": 11, "7": 12, "8": 13}`.

Baseline planner/runtime: `None` / `None`. Baseline Lab parameter declarations:
- rc_voltage_response: input_voltage=5.0 [0.0, 5.0], initial_voltage=0.0 [0.0, 5.0], time_constant=1.0 [0.1, 2.0]

New main analysis: The lecture derives the response of an RC circuit to a constant input using particular and homogeneous solutions. Applying the initial capacitor voltage gives vC(t) = VI + (V0 − VI)e^(−t/RC): the voltage starts at V0 and approaches VI with time constant τ = RC. The charging formula printed on page 8 contains a sign error; the general derivation and plotted charging curve require a minus sign.

New planner/engineering observations:

| Observation | Actual result |
|---|---|
| Planner | rejected |
| Family | None |
| Compiler | NOT_APPLICABLE |
| Compiler rejection | None |
| Lab demos rejected | 0 |
| Atlas validator | accepted |
| Pipeline exceptions | [] |

Planner diagnostic:
```json
{
  "stage": "normalize",
  "code": "plan",
  "path": "$",
  "generated": {
    "planner_family": "dynamic",
    "reason_length": 400,
    "reason_fingerprint": "0f0b2763bb6ad03b",
    "required_capabilities": [
      "equations",
      "continuous_parameters",
      "time_dynamics",
      "structure",
      "interaction_value"
    ],
    "focus_ids": [
      "flow_model",
      "flow_particular",
      "flow_homogeneous",
      "flow_sum",
      "flow_initial",
      "flow_response"
    ],
    "entities": {
      "collections": [],
      "states": [],
      "transitions": []
    }
  },
  "compiled_family": null,
  "normalized_entity_ids": [],
  "process_runtime_reached": false,
  "legacy_visual_flow_used": false,
  "supplied_semantic_ids": [
    "flow_model",
    "flow_particular",
    "flow_homogeneous",
    "flow_sum",
    "flow_initial",
    "flow_response"
  ],
  "runtime_capabilities": {
    "process": true,
    "spatial": false,
    "structural": false,
    "analogy": true,
    "graph": true,
    "lab": true
  }
}
```

### Proposed Lab `demo_rc_response` — runtime accepted

Distinguish the roles of initial voltage, final voltage, and the component-dependent time constant.

Formula display: `v_C(t) = V_I + (V_0 - V_I)e^{-t/(RC)},\qquad \tau = RC.\quad t\text{ in s},\ R\text{ in Ω},\ C\text{ in F}.`.

Independent/runtime axis: `{   "id": "time_s",   "label": "Elapsed time t (s)",   "min": 0,   "max": 30,   "points": 1000,   "semantic_role": "runtime_time",   "provenance": null }`.

Source facts declared by the model (source fidelity is for the reviewer):

| ID | Value | Pages (evaluation → physical) | Evidence declared |
|---|---|---|---|
| fact_charge_initial | 0 V | 8→13 | The charging example specifies V0 = 0 V. |
| fact_charge_input | 5 V | 8→13 | The charging example specifies VI = 5 V. |
| fact_discharge_initial | 5 V | 8→13 | The discharging example specifies V0 = 5 V. |
| fact_discharge_input | 0 V | 8→13 | The discharging example specifies VI = 0 V. |

Controls/read-only parameters:

| ID | Provenance | Source baseline ref | Min / initial / max | Exposed | Semantic refs |
|---|---|---|---|---|---|
| resistance | hypothetical_exploration | None | 1000 / 2000 / 10000 | True | [] |
| capacitance | hypothetical_exploration | None | 0.0001 / 0.0005 / 0.001 | True | [] |
| initial_voltage | hypothetical_exploration | fact_charge_initial | 0 / 0 / 5 | True | [] |
| input_voltage | hypothetical_exploration | fact_charge_input | 0 / 5 / 5 | True | [] |

Parameter evidence `resistance`: R appears in the circuit and response formula; no numerical resistance or adjustment range is supplied. This range is hypothetical.

Parameter evidence `capacitance`: C appears in the circuit and response formula; no numerical capacitance or adjustment range is supplied. This range is hypothetical.

Parameter evidence `initial_voltage`: The general solution uses V0; the immutable charging example specifies 0 V. Intermediate values are hypothetical exploration conditions.

Parameter evidence `input_voltage`: The general solution uses constant VI; the immutable charging example specifies 5 V. Intermediate values are hypothetical exploration conditions.

Series/metrics (declared derived expressions and ownership):

- series.capacitor_voltage: `input_voltage + (initial_voltage - input_voltage) * exp(-time_s / (resistance * capacitance))`; provenance `derived`; refs `['flow_response']`.
- derived_metrics.time_constant: `resistance * capacitance`; provenance `derived`; refs `[]`.

Trusted local commit observations:
```json
{
  "demo_id": "demo_rc_response",
  "source_facts": [
    {
      "id": "fact_charge_initial",
      "label": "Charging example initial voltage",
      "unit": "V",
      "value": 0.0,
      "provenance": "source_fixed",
      "source_pages": [
        8
      ],
      "source_evidence": "The charging example specifies V0 = 0 V."
    },
    {
      "id": "fact_charge_input",
      "label": "Charging example constant input",
      "unit": "V",
      "value": 5.0,
      "provenance": "source_fixed",
      "source_pages": [
        8
      ],
      "source_evidence": "The charging example specifies VI = 5 V."
    },
    {
      "id": "fact_discharge_initial",
      "label": "Discharging example initial voltage",
      "unit": "V",
      "value": 5.0,
      "provenance": "source_fixed",
      "source_pages": [
        8
      ],
      "source_evidence": "The discharging example specifies V0 = 5 V."
    },
    {
      "id": "fact_discharge_input",
      "label": "Discharging example constant input",
      "unit": "V",
      "value": 0.0,
      "provenance": "source_fixed",
      "source_pages": [
        8
      ],
      "source_evidence": "The discharging example specifies VI = 0 V."
    }
  ],
  "source_baseline_immutable": true,
  "initial_values": {
    "resistance": 2000.0,
    "capacitance": 0.0005,
    "initial_voltage": 0.0,
    "input_voltage": 5.0
  },
  "current_values": {
    "resistance": 6400.0,
    "capacitance": 0.00064,
    "initial_voltage": 3.0,
    "input_voltage": 3.0
  },
  "commits": [
    {
      "id": "resistance",
      "initial": 2000.0,
      "current": 6400.0
    },
    {
      "id": "capacitance",
      "initial": 0.0005,
      "current": 0.00064
    },
    {
      "id": "initial_voltage",
      "initial": 0.0,
      "current": 3.0
    },
    {
      "id": "input_voltage",
      "initial": 5.0,
      "current": 3.0
    }
  ],
  "rejections": [],
  "unknown_commit_rejected": true,
  "curve_changed": true
}
```

Source → representation observations:
```json
{
  "semantic_id": "flow_model",
  "region_id": "p1_circuit",
  "representation_ids": [
    "flow_model"
  ],
  "ownership": {
    "semantic_id": "flow_model",
    "source_region_ids": [
      "p1_circuit",
      "p1_node_equation",
      "p1_rc_equation",
      "p1_initial_requirement",
      "p1_time_units"
    ],
    "source_pages": [
      1
    ],
    "support": [
      {
        "region_id": "p1_circuit",
        "page": 1,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p1_node_equation",
        "page": 1,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p1_rc_equation",
        "page": 1,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p1_initial_requirement",
        "page": 1,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p1_time_units",
        "page": 1,
        "kind": "estimated_region",
        "confidence": "high"
      }
    ],
    "representation_ids": [
      "flow_model"
    ],
    "manipulation_target_ids": [],
    "formal_parameter_ids": [],
    "manipulable": false,
    "reason_not_manipulable": "No validated direct manipulation is available; use the formal view and existing controls."
  },
  "direct_manipulation": {
    "available": false,
    "targets": [],
    "absence_is_not_automatic_failure": true
  },
  "source_roundtrip": true,
  "source_pdf_unchanged": true,
  "atlas_immutable": true,
  "post_compilation_api_delta": 0
}
```

Objective review flags:
- New generated semantic IDs are internal to this material/attempt. Do not treat renamed IDs across generations as proof of semantic equivalence.
- Source facts/evidence text above are model declarations; validation checks their structure/pages and prevents writes, not their truth against the PDF.
- Hypothetical controls remain subject to review for pedagogical/source appropriateness, even when provenance and numeric safety pass.
- The new model declares four charging/discharging voltage facts separately from controls. R/C initial exploration values and hypothetical voltages must not be read as measured source conditions. The planner was rejected; the independent validated Lab/formal views remain available.

Reviewer (leave blank):

- Core source understanding: [ ]
- Fixed / adjustable: [ ]
- Representation appropriateness: [ ]
- Source fidelity: [ ]
- Unsupported invention: [ ]
- Post-fix overall A-axis: [ PASS / PARTIAL / FAIL ]

## harmonic — Classical Mechanics Chapter 23: Simple Harmonic Motion

Frozen baseline human A: **PASS** (unchanged). [Source](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/mit8_01scs22_chapter23.pdf).

Source evidence (frozen concise paraphrases; physical PDF pages):
- p.3: Sinusoidal position is introduced with amplitude, angular frequency and phase. Formula/concept: y(t) = A sin(2*pi*t/T); later pages introduce angular frequency and phase. Condition: The displayed sinusoid is a source-defined motion model.
- p.5: A spring restoring force and Newton's second law give the oscillator equation. Formula/concept: m d^2x/dt^2 = -k x. Condition: Undamped spring/mass model.
- p.6: The cosine solution has a natural angular frequency set by spring constant and mass. Formula/concept: omega = sqrt(k/m). Condition: Positive mass and spring stiffness.
- p.8: The general sine/cosine solution coefficients are related to initial position and velocity. Formula/concept: x(t) = C cos(omega t) + D sin(omega t). Condition: Given initial conditions define the source baseline; no damping/drive is declared.

Evaluation → physical mapping: `{"1": 3, "2": 4, "3": 5, "4": 6, "5": 7, "6": 8, "7": 9, "8": 10}`.

Baseline planner/runtime: `dynamic` / `existing validated numeric lab`. Baseline Lab parameter declarations:
- spring_initial_conditions: stiffness=4.0 [1.0, 16.0], mass=1.0 [0.5, 4.0], initial_position=0.5 [-1.0, 1.0], initial_velocity=0.5 [-2.0, 2.0]

New main analysis: Simple harmonic motion is sinusoidal motion produced by a restoring force proportional to displacement. For a frictionless spring–mass system, Newton’s second law gives x″ = −(k/m)x, which leads to angular frequency ω₀ = √(k/m). Initial position and velocity determine the particular motion, while amplitude and phase describe its size and timing.

New planner/engineering observations:

| Observation | Actual result |
|---|---|
| Planner | accepted |
| Family | dynamic |
| Compiler | existing validated numeric lab |
| Compiler rejection | None |
| Lab demos rejected | 0 |
| Atlas validator | accepted |
| Pipeline exceptions | [] |

Planner reason (model text): The ready numeric lab supports meaningful comparison of position and velocity curves for the source’s frictionless, one-dimensional spring–mass model. Vary positive k and m to explore ω₀ = √(k/m) and the period, then vary x₀ and vₓ,₀ in x(t) = x₀ cos(ω₀t) + (vₓ,₀/ω₀) sin(ω₀t). Comparing curves reveals how initial conditions determine amplitude and phase while k/m determines frequency. The deriv De

### Proposed Lab `phase_shift_lab` — runtime accepted

Distinguish changes in oscillation size, cycle duration, and horizontal timing.

Formula display: `x(t) = A cos(2πt/T + φ);  x_reference(t) = A cos(2πt/T);  Δt = −φT/(2π). Time and displacement use the example’s unspecified units; φ is in radians.`.

Independent/runtime axis: `{   "id": "lab_time",   "label": "Time t (unspecified source time units)",   "min": -6,   "max": 6,   "points": 600,   "semantic_role": "runtime_time",   "provenance": null }`.

Source facts declared by the model (source fidelity is for the reviewer):

| ID | Value | Pages (evaluation → physical) | Evidence declared |
|---|---|---|---|
| example_amplitude | 3 unspecified displacement units | 7→9 | The description of Figure 23.4a specifies A = 3. |
| example_period | 3.141592653589793 unspecified time units | 7→9 | The description of Figure 23.4a specifies T = π. |
| example_phase | 0.7853981633974483 rad | 7→9, 8→10 | Figure 23.4a uses φ = π/4 and places the corresponding maximum at t = −T/8. |

Controls/read-only parameters:

| ID | Provenance | Source baseline ref | Min / initial / max | Exposed | Semantic refs |
|---|---|---|---|---|---|
| trial_amplitude | hypothetical_exploration | example_amplitude | 0.5 / 3 / 5 | True | ['amplitude_phase'] |
| trial_period | hypothetical_exploration | example_period | 1 / 3.141592653589793 / 6 | True | ['amplitude_phase'] |
| trial_phase | hypothetical_exploration | example_phase | -3.141592653589793 / 0.7853981633974483 / 3.141592653589793 | True | ['amplitude_phase'] |

Parameter evidence `trial_amplitude`: The source specifies A = 3 for its example and identifies A as the amplitude. The adjustable range is generated for exploration, not reported by the source.

Parameter evidence `trial_period`: The source relates ω₀ to T by ω₀ = 2π/T and uses T = π in Figure 23.4a. The adjustable range is generated for exploration.

Parameter evidence `trial_phase`: The source demonstrates φ = π/4, 0, and −π/4 and explains positive and negative phase shifts. The continuous adjustable range is generated for exploration.

Series/metrics (declared derived expressions and ownership):

- series.shifted_displacement: `trial_amplitude*cos(2*pi*lab_time/trial_period+trial_phase)`; provenance `derived`; refs `['amplitude_phase']`.
- series.unshifted_reference: `trial_amplitude*cos(2*pi*lab_time/trial_period)`; provenance `derived`; refs `['amplitude_phase']`.
- series.source_example_curve: `example_amplitude*cos(2*pi*lab_time/example_period+example_phase)`; provenance `derived`; refs `['amplitude_phase']`.
- derived_metrics.exploration_time_shift: `-trial_phase*trial_period/(2*pi)`; provenance `derived`; refs `['amplitude_phase']`.
- derived_metrics.exploration_angular_frequency: `2*pi/trial_period`; provenance `derived`; refs `['amplitude_phase']`.

Trusted local commit observations:
```json
{
  "demo_id": "phase_shift_lab",
  "source_facts": [
    {
      "id": "example_amplitude",
      "label": "Source example amplitude",
      "unit": "unspecified displacement units",
      "value": 3.0,
      "provenance": "source_fixed",
      "source_pages": [
        7
      ],
      "source_evidence": "The description of Figure 23.4a specifies A = 3."
    },
    {
      "id": "example_period",
      "label": "Source example period",
      "unit": "unspecified time units",
      "value": 3.141592653589793,
      "provenance": "source_fixed",
      "source_pages": [
        7
      ],
      "source_evidence": "The description of Figure 23.4a specifies T = π."
    },
    {
      "id": "example_phase",
      "label": "Source example phase constant",
      "unit": "rad",
      "value": 0.7853981633974483,
      "provenance": "source_fixed",
      "source_pages": [
        7,
        8
      ],
      "source_evidence": "Figure 23.4a uses φ = π/4 and places the corresponding maximum at t = −T/8."
    }
  ],
  "source_baseline_immutable": true,
  "initial_values": {
    "trial_amplitude": 3.0,
    "trial_period": 3.141592653589793,
    "trial_phase": 0.7853981633974483
  },
  "current_values": {
    "trial_amplitude": 3.1999999999999997,
    "trial_period": 4.0,
    "trial_phase": 0.6283185307179586
  },
  "commits": [
    {
      "id": "trial_amplitude",
      "initial": 3.0,
      "current": 3.1999999999999997
    },
    {
      "id": "trial_period",
      "initial": 3.141592653589793,
      "current": 4.0
    },
    {
      "id": "trial_phase",
      "initial": 0.7853981633974483,
      "current": 0.6283185307179586
    }
  ],
  "rejections": [],
  "unknown_commit_rejected": true,
  "curve_changed": true
}
```

Source → representation observations:
```json
{
  "semantic_id": "spring_model",
  "region_id": "p2_displacement_arrow",
  "representation_ids": [
    "spring_model"
  ],
  "ownership": {
    "semantic_id": "spring_model",
    "source_region_ids": [
      "p3_force_diagram",
      "p3_force_vector",
      "p3_displacement_arrow",
      "p3_force_formula",
      "p2_spring_diagram",
      "p2_equilibrium_arrangement",
      "p2_stretched_arrangement",
      "p2_origin_label",
      "p2_positive_direction",
      "p2_displacement_arrow"
    ],
    "source_pages": [
      3,
      2
    ],
    "support": [
      {
        "region_id": "p3_force_diagram",
        "page": 3,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p3_force_vector",
        "page": 3,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p3_displacement_arrow",
        "page": 3,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p3_force_formula",
        "page": 3,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p2_spring_diagram",
        "page": 2,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p2_equilibrium_arrangement",
        "page": 2,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p2_stretched_arrangement",
        "page": 2,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p2_origin_label",
        "page": 2,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p2_positive_direction",
        "page": 2,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p2_displacement_arrow",
        "page": 2,
        "kind": "estimated_region",
        "confidence": "high"
      }
    ],
    "representation_ids": [
      "spring_model"
    ],
    "manipulation_target_ids": [],
    "formal_parameter_ids": [],
    "manipulable": false,
    "reason_not_manipulable": "No validated direct manipulation is available; use the formal view and existing controls."
  },
  "direct_manipulation": {
    "available": false,
    "targets": [],
    "absence_is_not_automatic_failure": true
  },
  "source_roundtrip": true,
  "source_pdf_unchanged": true,
  "atlas_immutable": true,
  "post_compilation_api_delta": 0
}
```

Objective review flags:
- New generated semantic IDs are internal to this material/attempt. Do not treat renamed IDs across generations as proof of semantic equivalence.
- Source facts/evidence text above are model declarations; validation checks their structure/pages and prevents writes, not their truth against the PDF.
- Hypothetical controls remain subject to review for pedagogical/source appropriateness, even when provenance and numeric safety pass.

Reviewer (leave blank):

- Core source understanding: [ ]
- Fixed / adjustable: [ ]
- Representation appropriateness: [ ]
- Source fidelity: [ ]
- Unsupported invention: [ ]
- Post-fix overall A-axis: [ PASS / PARTIAL / FAIL ]

## signals — Think DSP: Sounds and Signals

Frozen baseline human A: **PASS** (unchanged). [Source](https://greenteapress.com/thinkdsp/thinkdsp.pdf).

Source evidence (frozen concise paraphrases; physical PDF pages):
- p.14: The bell recording is periodic, about 2.3 ms per cycle and roughly 439 Hz. Formula/concept: frequency = 1/period. Condition: These are observations of the displayed recording.
- p.16: The violin spectrum includes a fundamental near 440 Hz and integer-multiple harmonics. Formula/concept: Harmonics at approximately 880, 1320, 1760 and 2200 Hz. Condition: The displayed recording/spectrum is source evidence, not regenerated audio.
- p.17: The example constructs a cosine at 440 Hz and a sine at 880 Hz with amplitudes 1.0 and 0.5 and zero offsets. Formula/concept: Superposition of two sinusoids. Condition: Example defaults remain identified; code is source data and is never executed.

Evaluation → physical mapping: `{"1": 14, "2": 15, "3": 16, "4": 17, "5": 18}`.

Baseline planner/runtime: `dynamic` / `existing validated numeric lab`. Baseline Lab parameter declarations:
- harmonic_mixture: cos_amp=1.0 [0.0, 1.0], sin_amp=0.5 [0.0, 1.0], phase=0.0 [0.0, 6.283185307179586]

New main analysis: Periodic sounds repeat in time, but their waveforms can be simple or complex. Spectral decomposition explains complex sounds as sums of sinusoids: the DFT produces a spectrum, and the FFT computes the DFT efficiently. A spectrum reveals the fundamental frequency, harmonics, and their amplitudes. The excerpt also shows how to combine mathematical signals, sample them into a Wave, and inspect a short segment.

New planner/engineering observations:

| Observation | Actual result |
|---|---|
| Planner | accepted |
| Family | static |
| Compiler | NOT_APPLICABLE |
| Compiler rejection | None |
| Lab demos rejected | 1 |
| Atlas validator | accepted |
| Pipeline exceptions | [] |

Planner reason (model text): Use a structured comparison linking the time-domain signal, DFT computation, frequency–amplitude spectrum, sinusoidal addition, and reconstructed waveform. The source supports frequency as inverse period, continuously valued sinusoid parameters, time-varying signals, and decomposition/reconstruction transformations. Compare the supplied 440 Hz cosine of amplitude 1.0 and 880 Hz sine of amplitude 0

### Proposed Lab `demo_signal_sum` — runtime rejected

Observe how the amplitude and phase of an 880 Hz component alter its sum with a fixed 440 Hz cosine.

Formula display: `c(t)=A_c\cos(2\pi f_c t),\quad s(t)=A_h\sin(2\pi f_h t+\phi_h),\quad y(t)=c(t)+s(t).\quad f_c=440\,\mathrm{Hz},\ f_h=880\,\mathrm{Hz},\ A_c=1.0.\ \text{Source example: }A_h=0.5,\ \phi_h=0.`.

Independent/runtime axis: `{   "id": "time_s",   "label": "Time (s); exploration window of approximately three 440 Hz periods",   "min": 0,   "max": 0.006818181818181818,   "points": 400,   "semantic_role": "runtime_time",   "provenance": null }`.

Source facts declared by the model (source fidelity is for the reviewer):

| ID | Value | Pages (evaluation → physical) | Evidence declared |
|---|---|---|---|
| cos_frequency | 440 Hz | 4→17 | The CosSignal example sets freq=440. |
| sin_frequency | 880 Hz | 4→17 | The SinSignal example sets freq=880. |
| cos_amplitude | 1 unspecified amplitude units | 4→17 | The CosSignal example sets amp=1.0. |
| sin_amplitude_baseline | 0.5 unspecified amplitude units | 4→17 | The SinSignal example sets amp=0.5. |
| cos_phase | 0 rad | 4→17 | The CosSignal example sets offset=0. |
| sin_phase_baseline | 0 rad | 4→17 | The SinSignal example sets offset=0. |

Controls/read-only parameters:

| ID | Provenance | Source baseline ref | Min / initial / max | Exposed | Semantic refs |
|---|---|---|---|---|---|
| harmonic_amplitude | hypothetical_exploration | sin_amplitude_baseline | 0 / 0.5 / 1 | True | [] |
| harmonic_phase | hypothetical_exploration | sin_phase_baseline | -3.141592653589793 / 0 / 3.141592653589793 | True | [] |

Parameter evidence `harmonic_amplitude`: The source uses amplitude 0.5; the adjustable range is generated for exploration, not reported measurements.

Parameter evidence `harmonic_phase`: The source defines phase offset in radians and uses zero in this example; the adjustable range is generated for exploration.

Series/metrics (declared derived expressions and ownership):

- series.cos_component: `cos_amplitude*cos(2*pi*cos_frequency*time_s+cos_phase)`; provenance `derived`; refs `[]`.
- series.sin_component: `harmonic_amplitude*sin(2*pi*sin_frequency*time_s+harmonic_phase)`; provenance `derived`; refs `[]`.
- series.summed_waveform: `cos_amplitude*cos(2*pi*cos_frequency*time_s+cos_phase)+harmonic_amplitude*sin(2*pi*sin_frequency*time_s+harmonic_phase)`; provenance `derived`; refs `['reconstructed_signal']`.

Actual Lab rejection: `Invalid declared variables.`. Source facts and controls in this proposal were not installed in the runtime.
- Expression `summed_waveform` references 7 numeric names: `['cos_amplitude', 'cos_frequency', 'cos_phase', 'harmonic_amplitude', 'harmonic_phase', 'sin_frequency', 'time_s']`. Existing safe_math per-expression limit: 5.

Source → representation observations:
```json
{
  "semantic_id": "input_signal",
  "region_id": "p1_bell_caption",
  "representation_ids": [
    "input_signal"
  ],
  "ownership": {
    "semantic_id": "input_signal",
    "source_region_ids": [
      "p2_violin_graph",
      "p2_violin_curve",
      "p2_violin_caption",
      "p1_bell_graph",
      "p1_bell_curve",
      "p1_bell_caption",
      "p1_period_definition"
    ],
    "source_pages": [
      2,
      1
    ],
    "support": [
      {
        "region_id": "p2_violin_graph",
        "page": 2,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p2_violin_curve",
        "page": 2,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p2_violin_caption",
        "page": 2,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p1_bell_graph",
        "page": 1,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p1_bell_curve",
        "page": 1,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p1_bell_caption",
        "page": 1,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p1_period_definition",
        "page": 1,
        "kind": "estimated_region",
        "confidence": "high"
      }
    ],
    "representation_ids": [
      "input_signal"
    ],
    "manipulation_target_ids": [],
    "formal_parameter_ids": [],
    "manipulable": false,
    "reason_not_manipulable": "No validated direct manipulation is available; use the formal view and existing controls."
  },
  "direct_manipulation": {
    "available": false,
    "targets": [],
    "absence_is_not_automatic_failure": true
  },
  "source_roundtrip": true,
  "source_pdf_unchanged": true,
  "atlas_immutable": true,
  "post_compilation_api_delta": 0
}
```

Objective review flags:
- New generated semantic IDs are internal to this material/attempt. Do not treat renamed IDs across generations as proof of semantic equivalence.
- Source facts/evidence text above are model declarations; validation checks their structure/pages and prevents writes, not their truth against the PDF.
- Hypothetical controls remain subject to review for pedagogical/source appropriateness, even when provenance and numeric safety pass.

Reviewer (leave blank):

- Core source understanding: [ ]
- Fixed / adjustable: [ ]
- Representation appropriateness: [ ]
- Source fidelity: [ ]
- Unsupported invention: [ ]
- Post-fix overall A-axis: [ PASS / PARTIAL / FAIL ]

## Big-O — offline shape only; no new live generation

Frozen baseline human A remains PARTIAL. The original adjustable coefficient `a=100` is retained in immutable baseline evidence. The explicit offline annotation creates `source_linear_coefficient=100` (source_fixed) and a separate hypothetical exploration identity. Trusted commits keep the source fact unchanged. This annotation is test data, not a model-generated improvement or an untouched holdout.
- Physical p.223: Algorithm analysis compares growth as input size increases. Asymptotic analysis; Growth class differs from measured machine timing.
- Physical p.224: The illustrative count functions compare a linear expression with a quadratic one. 100n+1 versus n^2+n+1; Source coefficients stay fixed; n is illustrative input size.
- Physical p.225: The Big-O table orders common growth classes. Constant, logarithmic, linear, quadratic and other growth classes; Definitions/table classifications are source facts.

## Five deep cases — unchanged captured IDs, local B replay

These rows revalidate the same captured source semantic entity against real existing formal renderer objects. No ownership is inferred for legacy Labs and no inverse handle is created.

| Case | Source region / evaluation→physical page | Exact semantic ID | Baseline representation_ids | POST_FIX representation_ids | Direct manipulation | Roundtrip |
|---|---|---|---|---|---|---|
| circular | p4_acceleration_decomposition / 4→6 | acceleration_components | [] | ['acceleration_components'] | False | True |
| harmonic | p2_restoring_force_statement / 2→4 | restoring_force | [] | ['restoring_force'] | False | True |
| circuits | p1_circuit / 1→6 | form_equation | [] | ['form_equation'] | False | True |
| probability | p5_addition_rule / 5→97 | union_rule | [] | ['union_rule'] | False | True |
| search | p1_append_formula / 1→226 | list_costs | [] | ['list_costs'] | False | True |

Cross-case facts only:
- All live cases share one sealed production tree, GPT-6.1 Sol / medium, and zero semantic retries.
- Legacy captured Labs are read-only by explicit compatibility policy. Explicit annotations occupy a separate offline lane.
- Formal representation ownership and inverse manipulation ownership remain separate.
- Raw proposals, compiler rejection and normalization omissions remain in the recorded denominator.
- The baseline human A-axis remains 4 PASS / 4 PARTIAL / 2 FAIL.
