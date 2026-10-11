# Day 27 prospective expectation packet — awaiting human adoption

No paid model requests have been made. This is an agent-prepared draft based on the actual source pages. The user requested a human-authored packet before inference; human adoption or corrections are required before freezing it. It is not yet `frozen-expectations.json`.

Deep: circular, harmonic, circuits, probability, spectrum. Stability: circular, harmonic, circuits, probability; three independent declarations on one stored analysis. Gold never enters model context.

## circular — Classical Mechanics Chapter 6: Circular Motion

Publisher: MIT OCW. Original physical PDF pages: [3, 4, 5, 6, 7, 8, 9, 10]. Evaluation pages: 1–8.
[Source](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/mit8_01scs22_chapter6.pdf) · [Terms](https://ocw.mit.edu/pages/privacy-and-terms-of-use/) · CC BY-NC-SA 4.0.

Concepts: position on a circle; angular velocity and period; tangential velocity; radial acceleration.
Families: spatial_dynamics; numeric_lab; formal concept map.
Fixed: source example coefficients remain compiled baseline; not measurements.
Adjustable: positive radius; positive uniform angular speed; time.
Forbidden inventions: no gravitational orbit or motor torque model; no radius=0; no changing the original source examples.
Honest degradation: A formal/numeric view is correct if a consistent bounded planar world cannot compile.

## harmonic — Classical Mechanics Chapter 23: Simple Harmonic Motion

Publisher: MIT OCW. Original physical PDF pages: [3, 4, 5, 6, 7, 8, 9, 10]. Evaluation pages: 1–8.
[Source](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/mit8_01scs22_chapter23.pdf) · [Terms](https://ocw.mit.edu/pages/privacy-and-terms-of-use/) · CC BY-NC-SA 4.0.

Concepts: amplitude and period; Hooke force and mass; omega=sqrt(k/m); initial conditions and phase.
Families: spatial_dynamics; numeric_lab; formal concept map.
Fixed: given initial conditions must remain identified as the source baseline.
Adjustable: positive mass and spring constant; non-negative amplitude; phase; time.
Forbidden inventions: no damping or driving force; no amplitude interpreted as wavelength; no arbitrary 3D mechanics.
Honest degradation: Numeric/formal degradation is correct when the runtime cannot express the oscillator honestly.

## circuits — 6.002 Lecture 12: First Order Circuits

Publisher: MIT OCW. Original physical PDF pages: [6, 7, 8, 9, 10, 11, 12, 13]. Evaluation pages: 1–8.
[Source](https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/84f4b553fc6a1ddd7007465041c4e213_6002_l12.pdf) · [Terms](https://ocw.mit.edu/pages/privacy-and-terms-of-use/) · CC BY-NC-SA 4.0.

Concepts: RC node equation; homogeneous and particular solutions; initial voltage; tau=RC; charging and discharging.
Families: numeric_lab; dynamic_simulation; process_flow; formal comparison.
Fixed: 5 V/0 V examples and boundary conditions are source baselines.
Adjustable: positive R and C; hypothetical input/initial voltage; time.
Forbidden inventions: no invented measured component values; no nonlinear transistor or second-order RLC model; no physical circuit rewiring handle.
Honest degradation: A formula/table/flow is correct without an unambiguous waveform inverse; generic bounded hypothetical defaults must be labeled.

## signals — Think DSP: Sounds and Signals

Publisher: Green Tea Press / Allen B. Downey. Original physical PDF pages: [14, 15, 16, 17, 18]. Evaluation pages: 1–5.
[Source](https://greenteapress.com/thinkdsp/thinkdsp.pdf) · [Terms](https://greenteapress.com/) · CC BY-NC-SA 4.0 (PDF copyright page).

Concepts: period/frequency; waveform/timbre; harmonics and spectral decomposition; two-sinusoid mixture.
Families: numeric_lab; formal concept map; comparison.
Fixed: 439 Hz observed bell and plotted recording; 440/880 Hz, 1.0/0.5 and offset=0 example baseline; original spectrum samples.
Adjustable: hypothetical sine/cosine frequency, amplitude and phase; bounded time window.
Forbidden inventions: no exact recovery of the recorded audio/spectrum from the screenshot; no execution of thinkdsp Python or audio download; no invented measured Fourier coefficients.
Honest degradation: Static descriptions are correct if only measured recordings are modeled or a safe symbolic demo is unsupported.

## regression — OpenIntro Statistics 4e screen-reader edition: Least Squares Regression

Publisher: OpenIntro / Diez, Cetinkaya-Rundel, Barr. Original physical PDF pages: [355, 356, 357, 358, 359, 360]. Evaluation pages: 1–6.
[Source](https://www.openintro.org/go/?id=os4_for_screen_reader) · [Terms](https://github.com/OpenIntroStat/openintro-statistics/blob/master/LICENSE.md) · CC BY-SA 3.0 text; excluded branding/cover.

Concepts: sum of squared residuals; b1=(sy/sx)R; line passes through means; interpretation of slope/intercept; prediction limitations.
Families: numeric_lab; formal comparison; concept map.
Fixed: 50-student sample; means 101780/19940; sd 63200/5460; R=-0.499; fitted slope -0.0431 and intercept 24.319 in thousands; empirical source dots.
Adjustable: prediction input inside observed range; explicitly hypothetical trial line separate from fitted source coefficients.
Forbidden inventions: no causal scholarship policy claim; no real student data reconstruction; do not make fitted estimates adjustable without a hypothetical distinction.
Honest degradation: A formal equation and source plot is correct if fixed empirical data cannot be represented; no drag of observed dots.

## probability — OpenIntro Statistics 4e screen-reader edition: Defining Probability

Publisher: OpenIntro / Diez, Cetinkaya-Rundel, Barr. Original physical PDF pages: [93, 94, 95, 96, 97, 98, 99, 100]. Evaluation pages: 1–8.
[Source](https://www.openintro.org/go/?id=os4_for_screen_reader) · [Terms](https://github.com/OpenIntroStat/openintro-statistics/blob/master/LICENSE.md) · CC BY-SA 3.0 text; excluded branding/cover.

Concepts: disjoint events; die outcome sets A={1,2}, B={4,6}, D={2,3}; inclusive or and intersection correction; complement; non-uniform dice-sum distribution.
Families: probability_sets; formal comparison; concept map.
Fixed: six fair die outcomes and source memberships; 52-card counts; two-dice sum weights; given income/loan proportions.
Adjustable: local event selection/set operations; Monte Carlo sample count with original probabilities.
Forbidden inventions: do not treat dice sums as uniformly likely; no arbitrary changes to source probabilities; no unlimited 52-outcome world if contract exceeds bounds.
Honest degradation: A bounded six-outcome die subset is honest with scope disclosed; other examples may stay formal. Dragging geometry is N/A.

## search — Think Python 2e Appendix B: Analysis of Algorithms, Search

Publisher: Green Tea Press / Allen B. Downey. Original physical PDF pages: [226, 227]. Evaluation pages: 1–2.
[Source](https://greenteapress.com/thinkpython2/thinkpython2.pdf) · [Terms](https://greenteapress.com/) · CC BY-NC 3.0 (PDF copyright page).

Concepts: sequential search O(n); sorted-list bisection O(log n); constant-time list operations; hashing and dictionaries.
Families: process_flow; formal flow; comparison.
Fixed: algorithm correctness and complexity assumptions; source contains no measured timing dataset.
Adjustable: local navigation through declared process; explicit hypothetical sorted input only if safely resolved.
Forbidden inventions: no execution of generated Python; no unsupported arbitrary binary-search machine; no invented measured benchmarks.
Honest degradation: A read-only flow/comparison is correct when bounded execution is unsupported.

## complexity — Think Python 2e Appendix B: Order of Growth

Publisher: Green Tea Press / Allen B. Downey. Original physical PDF pages: [223, 224, 225]. Evaluation pages: 1–3.
[Source](https://greenteapress.com/thinkpython2/thinkpython2.pdf) · [Terms](https://greenteapress.com/) · CC BY-NC 3.0 (PDF copyright page).

Concepts: asymptotic analysis; linear vs quadratic; 100n+1 vs n^2+n+1; Big-O growth table.
Families: comparison; numeric_lab; concept map.
Fixed: source example coefficients 100 and 1; Big-O definitions and table classes.
Adjustable: positive integer input size n for illustrative operation counts.
Forbidden inventions: do not present operation count as measured wall-clock time; no changing source algorithm coefficients; no source-supported hardware benchmark claim.
Honest degradation: A comparison/table is sufficient; numeric count curves are optional and must stay illustrative.

## spectrum — Tour of the Electromagnetic Spectrum 3e: Unit Conversion Scale

Publisher: NASA / Ginger Butcher. Original physical PDF pages: [35]. Evaluation pages: 1–1.
[Source](https://science.nasa.gov/wp-content/uploads/2023/08/tour-of-the-ems-tagged-v7-0.pdf) · [Terms](https://www.nasa.gov/nasa-brand-center/images-and-media/) · NASA general educational/informational media permission; attribution; no endorsement.

Concepts: frequency/wavelength/energy unit conventions; scientific notation; unit conversion scale table; positive wavelength values.
Families: comparison; numeric_lab; formal table.
Fixed: every source table cell and size comparison; vacuum conversion baseline approximately c=3e8 m/s if explained as general physics.
Adjustable: explicitly hypothetical positive wavelength/frequency conversion within numeric limits.
Forbidden inventions: no zero wavelength; no invented full spectrum dataset or new 3D propagation scene; no claimed exact page-box grounding before Atlas validation.
Honest degradation: Static table is correct if numeric dynamic ranges exceed the bounded evaluator. Only physical PDF page 35 is ingested: photo/stock pages are excluded.

## debugging — Think Python 2e Appendix A: Debugging

Publisher: Green Tea Press / Allen B. Downey. Original physical PDF pages: [215, 216]. Evaluation pages: 1–2.
[Source](https://greenteapress.com/thinkpython2/thinkpython2.pdf) · [Terms](https://greenteapress.com/) · CC BY-NC 3.0 (PDF copyright page).

Concepts: syntax/runtime/semantic errors; incremental testing; localizing syntax faults; debugging strategy.
Families: formal flow; concept map; comparison.
Fixed: error-category meanings; source advice.
Adjustable: local reading/selection only.
Forbidden inventions: no numerical physics world; no fabricated executable debugger or source code; no justified numeric drag handle.
Honest degradation: Formal/static representation is the intended success, preserving selection/source navigation without fabricated manipulation.
