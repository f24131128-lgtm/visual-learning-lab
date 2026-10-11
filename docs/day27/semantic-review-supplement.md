# Day27 A-axis human semantic-review packet

A-axis final verdicts are reserved for the human reviewer. All ten cases remain in the denominator. Compiler/validator acceptance supplies B-axis evidence only. No semantic correctness verdict is assigned here.

Attribution: AI-drafted, human-reviewed and approved expectations before model execution. Source page labels below are original physical PDF pages; outputs cite renumbered evaluation pages.

## circular — Classical Mechanics Chapter 6: Circular Motion

[Original source](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/mit8_01scs22_chapter6.pdf) · [Terms](https://ocw.mit.edu/pages/privacy-and-terms-of-use/) · CC BY-NC-SA 4.0

### 1. Source evidence and frozen conditions

Physical PDF pages: [3, 4, 5, 6, 7, 8, 9, 10]. Evaluation → original mapping: {"1": 3, "2": 4, "3": 5, "4": 6, "5": 7, "6": 8, "7": 9, "8": 10}.
Source-grounded concise paraphrases from the reviewed prospective packet: position on a circle; angular velocity and period; tangential velocity; radial acceleration.
Fixed source conditions: source example coefficients remain compiled baseline; not measurements.
Permitted adjustment/local operations: positive radius; angular velocity: signed or positive according to source direction/coordinate semantics; never infer its domain from the parameter ID or label.

- Original PDF p.3: Position on a circle is described with radius and radial/tangential unit directions. Formula/concept: r = R r_hat. Fixed condition: Circular path has constant radius in the defined motion.
- Original PDF p.4: Angular motion is defined relative to an angle coordinate and its time derivative. Formula/concept: omega = d(theta)/dt. Fixed condition: The source coordinate/direction convention determines signed angular velocity versus speed magnitude.
- Original PDF p.6: Velocity follows the tangential direction and depends on radius and angular rate. Formula/concept: v = R omega theta_hat. Fixed condition: Use the same radius and angular coordinate.
- Original PDF p.9: Uniform motion has constant angular rate and inward radial acceleration. Formula/concept: a_radial = -R omega^2 r_hat. Fixed condition: Uniform angular rate; no gravitational-orbit model is supplied.

### 2–8. Actual output, declarations, representation, grounding and differences

```json
{
  "quick_summary": "Circular motion has tangential velocity and inward radial acceleration because the direction of motion continually changes. Differentiating position in a rotating polar basis gives velocity and the tangential and radial acceleration components. Uniform circular motion has constant speed, but nonzero centripetal acceleration, with equivalent descriptions using angular speed, period, and frequency.",
  "key_concepts": [
    {
      "concept": "Position and polar unit vectors",
      "explanation": "For a fixed radius r, the position is r⃗(t) = r r̂(t). The outward radial vector r̂ and tangential vector θ̂ rotate with the particle: r̂ = cosθ î + sinθ ĵ and θ̂ = −sinθ î + cosθ ĵ.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Derivatives of the rotating basis",
      "explanation": "Even at constant radius, the basis vectors change direction: d r̂/dt = θ̇ θ̂ and d θ̂/dt = −θ̇ r̂. These identities are essential when differentiating velocity.",
      "source_pages": [
        2,
        5
      ]
    },
    {
      "concept": "Tangential velocity and angular speed",
      "explanation": "The signed tangential component is vθ = rθ̇, so v⃗ = rθ̇ θ̂. Speed is v = r|θ̇|. Distinguish signed angular rate θ̇ from angular speed ω = |θ̇|; the extraction sometimes omits magnitude signs.",
      "source_pages": [
        2,
        4
      ]
    },
    {
      "concept": "Geometric velocity derivation",
      "explanation": "A displacement spanning a small positive angle Δθ has chord length 2r sin(Δθ/2). For small angles in radians, this approaches rΔθ. Dividing by Δt and taking the limit gives tangential velocity.",
      "source_pages": [
        3,
        4
      ]
    },
    {
      "concept": "Tangential acceleration",
      "explanation": "The tangential component is aθ = rθ̈. It arises from changing angular rate and can change the speed.",
      "source_pages": [
        5,
        6
      ]
    },
    {
      "concept": "Radial acceleration and centripetal force",
      "explanation": "With outward r̂ positive, ar = −rθ̇². Its magnitude is ac = rω² = v²/r, and it points inward whenever speed is nonzero. The net radial force satisfies Fr = mar.",
      "source_pages": [
        1,
        6,
        7,
        8
      ]
    },
    {
      "concept": "Uniform circular motion",
      "explanation": "Zero net tangential force gives aθ = 0 and constant speed. The velocity still changes direction, so acceleration remains inward rather than vanishing.",
      "source_pages": [
        6,
        7,
        8
      ]
    },
    {
      "concept": "Period and frequency",
      "explanation": "The period T is the time for one revolution, and frequency f is revolutions per second. For uniform circular motion, T = 2πr/v = 2π/ω and f = 1/T = ω/(2π), measured in hertz.",
      "source_pages": [
        7,
        8
      ]
    },
    {
      "concept": "Equivalent centripetal acceleration formulas",
      "explanation": "The inward acceleration magnitude can be written ac = rω² = v²/r = 4π²rf² = 4π²r/T². Choose the form matching the known quantities; do not confuse this positive magnitude with the signed component ar.",
      "source_pages": [
        7,
        8
      ]
    },
    {
      "concept": "Time-dependent angular motion example",
      "explanation": "For θ(t) = At³ − Bt, θ̇ = 3At² − B and θ̈ = 6At. Thus v⃗ = R(3At² − B)θ̂ and a⃗ = 6RAt θ̂ − R(3At² − B)²r̂. At nonnegative time, centripetal acceleration vanishes at t = √(B/(3A)). The extracted velocity line contains an extra t after B, and the extracted root is missing.",
      "source_pages": [
        6
      ]
    }
  ],
  "relationships": [
    {
      "source": "Position vector",
      "relation": "equals fixed radius multiplied by",
      "target": "Outward radial unit vector",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Polar unit vectors",
      "relation": "depend on",
      "target": "Angular position θ(t)",
      "source_pages": [
        1,
        2
      ]
    },
    {
      "source": "Radial unit vector",
      "relation": "has time derivative θ̇ times",
      "target": "Tangential unit vector",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Tangential unit vector",
      "relation": "has time derivative −θ̇ times",
      "target": "Radial unit vector",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Velocity",
      "relation": "is the time derivative of",
      "target": "Position vector",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Velocity",
      "relation": "is tangent to the orbit and perpendicular to",
      "target": "Position vector",
      "source_pages": [
        4
      ]
    },
    {
      "source": "Tangential velocity component",
      "relation": "equals rθ̇ and therefore depends on",
      "target": "Radius and signed angular rate",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Speed",
      "relation": "equals radius multiplied by",
      "target": "Angular speed",
      "source_pages": [
        4,
        7
      ]
    },
    {
      "source": "Small-angle approximation",
      "relation": "makes chord length approach",
      "target": "Arc length rΔθ",
      "source_pages": [
        3,
        4
      ]
    },
    {
      "source": "Acceleration",
      "relation": "is the time derivative of",
      "target": "Velocity",
      "source_pages": [
        5
      ]
    },
    {
      "source": "Acceleration",
      "relation": "decomposes into",
      "target": "Tangential and radial components",
      "source_pages": [
        4,
        5,
        6
      ]
    },
    {
      "source": "Tangential acceleration",
      "relation": "equals radius multiplied by",
      "target": "Angular acceleration θ̈",
      "source_pages": [
        5
      ]
    },
    {
      "source": "Changing tangential basis direction",
      "relation": "produces the inward term in",
      "target": "Radial acceleration",
      "source_pages": [
        5,
        6
      ]
    },
    {
      "source": "Signed radial acceleration",
      "relation": "equals",
      "target": "−rθ̇²",
      "source_pages": [
        6
      ]
    },
    {
      "source": "Net radial force",
      "relation": "equals mass multiplied by",
      "target": "Signed radial acceleration",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Zero net tangential force",
      "relation": "implies",
      "target": "Zero tangential acceleration and constant speed",
      "source_pages": [
        6,
        7
      ]
    },
    {
      "source": "Uniform circular motion",
      "relation": "has constant speed but continuously changing",
      "target": "Velocity direction",
      "source_pages": [
        7,
        8
      ]
    },
    {
      "source": "Changing velocity direction",
      "relation": "requires",
      "target": "Nonzero acceleration",
      "source_pages": [
        8
      ]
    },
    {
      "source": "Period",
      "relation": "is the time required for",
      "target": "One complete revolution",
      "source_pages": [
        7
      ]
    },
    {
      "source": "Frequency",
      "relation": "is the reciprocal of",
      "target": "Period",
      "source_pages": [
        7,
        8
      ]
    },
    {
      "source": "Angular speed",
      "relation": "equals 2π times",
      "target": "Frequency",
      "source_pages": [
        7
      ]
    },
    {
      "source": "Centripetal acceleration magnitude",
      "relation": "has equivalent expressions",
      "target": "rω², v²/r, 4π²rf², and 4π²r/T²",
      "source_pages": [
        7,
        8
      ]
    },
    {
      "source": "Angular law θ = At³ − Bt",
      "relation": "gives",
      "target": "Angular rate 3At² − B and angular acceleration 6At",
      "source_pages": [
        6
      ]
    },
    {
      "source": "Zero angular rate in the worked example",
      "relation": "gives zero",
      "target": "Centripetal acceleration",
      "source_pages": [
        6
      ]
    }
  ],
  "visual_evidence": [
    {
      "page": 4,
      "type": "formula",
      "description": "Equation 6.2.15 visibly includes magnitude signs in the limiting derivation v = r|dθ/dt| = rω.",
      "learning_value": "Clarifies the distinction between positive speed and signed angular rate, which is obscured in the extraction."
    },
    {
      "page": 4,
      "type": "diagram",
      "description": "Figure 6.3 shows two nearby radius vectors, their displacement chord, the angular separation, a tangent line, and radial and tangential unit vectors.",
      "learning_value": "Makes the limiting argument for tangential velocity visible: the shrinking chord approaches the tangent direction."
    },
    {
      "page": 4,
      "type": "formula",
      "description": "Equation 6.3.1 decomposes acceleration as a⃗ = ar r̂(t) + aθ θ̂(t).",
      "learning_value": "Separates the two perpendicular directions used in the acceleration derivation."
    },
    {
      "page": 8,
      "type": "formula",
      "description": "Equation 6.4.9 visibly gives the radial acceleration magnitude as |ar| = 4π²r/T².",
      "learning_value": "Emphasizes that the positive magnitude is different from the negative outward-coordinate radial component."
    },
    {
      "page": 8,
      "type": "diagram",
      "description": "Figure 6.4 places tangent velocity arrows around a circular path and labels position and velocity at two nearby times.",
      "learning_value": "Shows why constant speed does not mean constant velocity."
    },
    {
      "page": 8,
      "type": "diagram",
      "description": "Figure 6.5 compares v⃗(t) and v⃗(t + Δt) with a connecting Δv⃗ arrow and their angular separation.",
      "learning_value": "Illustrates how a change in velocity direction creates acceleration even when the velocity magnitudes are equal."
    }
  ],
  "primary_visualization": {
    "type": "flow",
    "reason": "The central learning task is following the explicit derivation from circular position through rotating-basis derivatives to velocity and acceleration, then specializing to uniform motion and orbital measurements."
  },
  "planner": null,
  "numeric_lab_declarations": [
    {
      "id": "angular_acceleration_lab",
      "source_pages": [
        5,
        6
      ],
      "parameters": [
        {
          "id": "coefA",
          "label": "Angular-law coefficient A",
          "unit": "rad/s³",
          "min": 0.1,
          "max": 1.0,
          "default": 0.3,
          "step": 0.05,
          "parameter_kind": "adjustable"
        },
        {
          "id": "coefB",
          "label": "Angular-law coefficient B",
          "unit": "rad/s",
          "min": 0.1,
          "max": 3.0,
          "default": 0.9,
          "step": 0.1,
          "parameter_kind": "adjustable"
        },
        {
          "id": "radius",
          "label": "Circle radius R",
          "unit": "m",
          "min": 0.5,
          "max": 3.0,
          "default": 1.0,
          "step": 0.1,
          "parameter_kind": "adjustable"
        }
      ],
      "x": {
        "id": "time",
        "label": "Time t (s)",
        "min": 0.0,
        "max": 3.5,
        "points": 400
      },
      "series": [
        {
          "id": "tangent_accel",
          "label": "Tangential component aθ (m/s²)",
          "expression": "6*radius*coefA*time"
        },
        {
          "id": "radial_accel",
          "label": "Signed radial component ar (m/s²)",
          "expression": "-radius*(3*coefA*time**2-coefB)**2"
        }
      ],
      "derived_metrics": [
        {
          "id": "zero_radial_time",
          "label": "Time when radial acceleration is zero",
          "expression": "sqrt(coefB/(3*coefA))",
          "unit": "s"
        },
        {
          "id": "tangent_at_zero",
          "label": "Tangential acceleration at that time",
          "expression": "6*radius*coefA*sqrt(coefB/(3*coefA))",
          "unit": "m/s²"
        }
      ]
    }
  ],
  "scene_declarations": null,
  "normalized_declarations": null,
  "affordances": null,
  "source_refs": {
    "declared_count": 91,
    "invalid": [],
    "valid": true
  },
  "grounding_status": "NOT_EVALUATED",
  "failure_reason": {
    "stage": "normalize",
    "code": "provenance",
    "path": "$",
    "generated": {
      "planner_family": "dynamic",
      "reason_length": 400,
      "reason_fingerprint": "4db0d4052606c637",
      "required_capabilities": [
        "equations",
        "continuous_parameters",
        "time_dynamics",
        "spatial_relations",
        "structure",
        "interaction_value"
      ],
      "focus_ids": [
        "position_basis",
        "basis_derivatives",
        "tangent_velocity",
        "acceleration_components",
        "uniform_motion",
        "orbit_measures"
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
      "position_basis",
      "basis_derivatives",
      "tangent_velocity",
      "acceleration_components",
      "uniform_motion",
      "orbit_measures"
    ],
    "runtime_capabilities": {
      "process": true,
      "spatial": true,
      "structural": false,
      "analogy": true,
      "graph": true,
      "lab": true
    }
  }
}
```

Predefined reasonable families: spatial_dynamics; numeric_lab; formal concept map.
Unsupported semantics to inspect: no gravitational orbit or motor torque model; no radius=0; no changing the original source examples.
Static/formal conditions: A formal/numeric view is correct if a consistent bounded planar world cannot compile.
Objective observations: selected family = None; invalid raw analysis refs = []; rejected lab count = 0.
Compare source fixed conditions against the min/max/default and expressions above. A varying fitted/source constant, new formula, added dynamics or unmatched support is a review flag; this packet does not decide its semantic verdict.
**A verdict: HUMAN REVIEW PENDING.**

## harmonic — Classical Mechanics Chapter 23: Simple Harmonic Motion

[Original source](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/mit8_01scs22_chapter23.pdf) · [Terms](https://ocw.mit.edu/pages/privacy-and-terms-of-use/) · CC BY-NC-SA 4.0

### 1. Source evidence and frozen conditions

Physical PDF pages: [3, 4, 5, 6, 7, 8, 9, 10]. Evaluation → original mapping: {"1": 3, "2": 4, "3": 5, "4": 6, "5": 7, "6": 8, "7": 9, "8": 10}.
Source-grounded concise paraphrases from the reviewed prospective packet: amplitude and period; Hooke force and mass; omega=sqrt(k/m); initial conditions and phase.
Fixed source conditions: given initial conditions must remain identified as the source baseline.
Permitted adjustment/local operations: positive mass and spring constant; non-negative amplitude; phase.

- Original PDF p.3: Sinusoidal position is introduced with amplitude, angular frequency and phase. Formula/concept: y(t) = A sin(2*pi*t/T); later pages introduce angular frequency and phase. Fixed condition: The displayed sinusoid is a source-defined motion model.
- Original PDF p.5: A spring restoring force and Newton's second law give the oscillator equation. Formula/concept: m d^2x/dt^2 = -k x. Fixed condition: Undamped spring/mass model.
- Original PDF p.6: The cosine solution has a natural angular frequency set by spring constant and mass. Formula/concept: omega = sqrt(k/m). Fixed condition: Positive mass and spring stiffness.
- Original PDF p.8: The general sine/cosine solution coefficients are related to initial position and velocity. Formula/concept: x(t) = C cos(omega t) + D sin(omega t). Fixed condition: Given initial conditions define the source baseline; no damping/drive is declared.

### 2–8. Actual output, declarations, representation, grounding and differences

```json
{
  "quick_summary": "Simple harmonic motion is sinusoidal motion with a repeating period. For a frictionless spring–mass system, the restoring force leads to x″ = −(k/m)x. Verifying sinusoidal solutions gives ω₀ = √(k/m), and combining sine and cosine terms allows the motion to satisfy any initial position and velocity. The same solution can be expressed using amplitude and phase.",
  "key_concepts": [
    {
      "concept": "Simple harmonic motion and amplitude",
      "explanation": "SHM varies sinusoidally. In y(t) = A sin(2πt/T), the positive amplitude A sets the extrema +A and −A.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Period, frequency, and angular frequency",
      "explanation": "The period T is the repeat time: y(t + T) = y(t). Frequency is f = 1/T in hertz, and angular frequency is ω₀ = 2π/T = 2πf in rad/s. Angular frequency is constant for SHM.",
      "source_pages": [
        1,
        2
      ]
    },
    {
      "concept": "Spring displacement and restoring force",
      "explanation": "Displacement x is measured from equilibrium, with positive x indicating extension and negative x compression. The force Fₓ = −kx points toward equilibrium.",
      "source_pages": [
        2,
        3
      ]
    },
    {
      "concept": "Simple harmonic oscillator equation",
      "explanation": "Newton’s second law gives mx″ = −kx, or x″ = −(k/m)x. Acceleration is proportional to displacement and opposite in direction, so it is not constant during nonzero oscillation.",
      "source_pages": [
        3
      ]
    },
    {
      "concept": "Natural angular frequency and period",
      "explanation": "Substituting a cosine solution into the oscillator equation requires ω₀² = k/m. Thus ω₀ = √(k/m) and T = 2π√(m/k). These quantities depend on mass and stiffness, not the initial conditions.",
      "source_pages": [
        4,
        6
      ]
    },
    {
      "concept": "Special sine and cosine solutions",
      "explanation": "A cos(ω₀t) starts at displacement A with zero velocity. B sin(ω₀t) starts at equilibrium with velocity ω₀B. Each solves the oscillator equation but cannot alone represent all initial conditions.",
      "source_pages": [
        4,
        5
      ]
    },
    {
      "concept": "Superposition and the general solution",
      "explanation": "Because the oscillator equation is linear, sums of its solutions are also solutions. Its general solution is x(t) = C cos(ω₀t) + D sin(ω₀t).",
      "source_pages": [
        5
      ]
    },
    {
      "concept": "Initial conditions determine coefficients",
      "explanation": "Evaluating position and velocity at t = 0 gives C = x₀ and D = vₓ,₀/ω₀. Therefore x(t) = x₀ cos(ω₀t) + (vₓ,₀/ω₀) sin(ω₀t), valid for any initial position and velocity.",
      "source_pages": [
        6
      ]
    },
    {
      "concept": "Amplitude–phase representation",
      "explanation": "The general solution also equals A cos(ω₀t + φ), with C = A cosφ and D = −A sinφ. Hence A = √(C² + D²) = √(x₀² + (vₓ,₀/ω₀)²). The source gives tanφ = −D/C; the coefficient signs must also be used to select the correct quadrant.",
      "source_pages": [
        6,
        7
      ]
    },
    {
      "concept": "Phase and horizontal shift",
      "explanation": "The phase is ω₀t + φ and φ is the phase constant. Relative to A cos(ω₀t), positive φ shifts the curve left and negative φ shifts it right. Maxima satisfy ω₀t + φ = 2πn; the n = 0 maximum occurs at t = −φ/ω₀.",
      "source_pages": [
        7,
        8
      ]
    }
  ],
  "relationships": [
    {
      "source": "Simple harmonic motion",
      "relation": "is motion in which a physical quantity varies",
      "target": "sinusoidally",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Amplitude A",
      "relation": "sets the displacement bounds",
      "target": "−A to +A",
      "source_pages": [
        1,
        7
      ]
    },
    {
      "source": "Period T",
      "relation": "is the repeat interval satisfying",
      "target": "y(t + T) = y(t)",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Frequency f",
      "relation": "is the reciprocal of",
      "target": "period T: f = 1/T",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Angular frequency ω₀",
      "relation": "is related to period and frequency by",
      "target": "ω₀ = 2π/T = 2πf",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Angular frequency in SHM",
      "relation": "is",
      "target": "constant",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Angular speed in uniform circular motion",
      "relation": "equals",
      "target": "angular frequency",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Spring displacement x",
      "relation": "is measured from",
      "target": "the equilibrium position",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Positive and negative spring displacement",
      "relation": "correspond respectively to",
      "target": "extension and compression",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Spring restoring force",
      "relation": "opposes displacement according to",
      "target": "Fₓ = −kx",
      "source_pages": [
        2,
        3
      ]
    },
    {
      "source": "Fₓ = −kx and Newton’s second law",
      "relation": "give",
      "target": "x″ = −(k/m)x",
      "source_pages": [
        3
      ]
    },
    {
      "source": "Oscillator acceleration",
      "relation": "is proportional to and opposite in sign to",
      "target": "displacement",
      "source_pages": [
        3
      ]
    },
    {
      "source": "Sine and cosine functions",
      "relation": "have second derivatives equal to",
      "target": "−ω₀² times the original function",
      "source_pages": [
        3,
        4,
        5
      ]
    },
    {
      "source": "A sinusoidal solution of the spring oscillator equation",
      "relation": "requires",
      "target": "ω₀² = k/m",
      "source_pages": [
        4
      ]
    },
    {
      "source": "Mass m and spring constant k",
      "relation": "determine",
      "target": "ω₀ = √(k/m) and T = 2π√(m/k)",
      "source_pages": [
        4
      ]
    },
    {
      "source": "A cos(ω₀t)",
      "relation": "has initial conditions",
      "target": "x(0) = A and vₓ(0) = 0",
      "source_pages": [
        4
      ]
    },
    {
      "source": "B sin(ω₀t)",
      "relation": "has initial conditions",
      "target": "x(0) = 0 and vₓ(0) = ω₀B",
      "source_pages": [
        5
      ]
    },
    {
      "source": "Linearity of the oscillator equation",
      "relation": "allows",
      "target": "superposition of sine and cosine solutions",
      "source_pages": [
        5
      ]
    },
    {
      "source": "General position solution",
      "relation": "is",
      "target": "x(t) = C cos(ω₀t) + D sin(ω₀t)",
      "source_pages": [
        5
      ]
    },
    {
      "source": "Position x(t)",
      "relation": "has time derivative",
      "target": "vₓ(t) = −ω₀C sin(ω₀t) + ω₀D cos(ω₀t)",
      "source_pages": [
        6
      ]
    },
    {
      "source": "Initial position x₀",
      "relation": "determines",
      "target": "C = x₀",
      "source_pages": [
        6
      ]
    },
    {
      "source": "Initial velocity vₓ,₀",
      "relation": "determines",
      "target": "D = vₓ,₀/ω₀",
      "source_pages": [
        6
      ]
    },
    {
      "source": "Sine–cosine representation",
      "relation": "is equivalent to",
      "target": "x(t) = A cos(ω₀t + φ)",
      "source_pages": [
        6,
        7
      ]
    },
    {
      "source": "Amplitude and phase constant",
      "relation": "determine the coefficients through",
      "target": "C = A cosφ and D = −A sinφ",
      "source_pages": [
        7
      ]
    },
    {
      "source": "Initial position and velocity",
      "relation": "determine the amplitude through",
      "target": "A = √(x₀² + (vₓ,₀/ω₀)²)",
      "source_pages": [
        7
      ]
    },
    {
      "source": "Phase constant φ",
      "relation": "sets the horizontal shift",
      "target": "−φ/ω₀",
      "source_pages": [
        7,
        8
      ]
    },
    {
      "source": "Positive phase constant",
      "relation": "shifts the cosine curve",
      "target": "left, to earlier maxima",
      "source_pages": [
        7,
        8
      ]
    },
    {
      "source": "Negative phase constant",
      "relation": "shifts the cosine curve",
      "target": "right, to later maxima",
      "source_pages": [
        7,
        8
      ]
    },
    {
      "source": "Maximum displacement",
      "relation": "occurs when",
      "target": "ω₀t + φ = 2πn",
      "source_pages": [
        7
      ]
    }
  ],
  "visual_evidence": [
    {
      "page": 1,
      "type": "graph",
      "description": "Figure 23.1 shows a sinusoidal time graph with +A and −A marked vertically and a horizontal arrow marking the repeat interval T.",
      "learning_value": "Separates amplitude, a vertical scale, from period, a horizontal repeat interval."
    },
    {
      "page": 1,
      "type": "formula",
      "description": "The displayed equations give y(t) = A sin(2πt/T), demonstrate y(t + T) = y(t), and define f = 1/T and ω₀ = 2π/T = 2πf.",
      "learning_value": "Connects the repeating graph to equivalent mathematical descriptions and frequency units."
    },
    {
      "page": 2,
      "type": "diagram",
      "description": "Figure 23.2 contrasts the spring–object system at equilibrium and in a stretched position, labeling l_eq, l₀, x = 0, x(t), and the positive direction.",
      "learning_value": "Clarifies that x is displacement from equilibrium, not the spring’s total length."
    },
    {
      "page": 3,
      "type": "diagram",
      "description": "Figure 23.3 shows a block displaced to the right and a spring-force arrow pointing left, alongside the restoring-force expression.",
      "learning_value": "Makes the negative sign in Fₓ = −kx physically meaningful."
    },
    {
      "page": 3,
      "type": "formula",
      "description": "The displayed derivation introduces −kx = m d²x/dt², rearranges it to d²x/dt² = −(k/m)x, and proposes x(t) = A cos(ω₀t).",
      "learning_value": "Shows how the physical force model becomes a differential equation and motivates a sinusoidal trial solution."
    },
    {
      "page": 8,
      "type": "graph",
      "description": "Figure 23.4 contains three cosine plots for φ = π/4, φ = 0, and φ = −π/4, with shifted maxima indicated at −T/8 and +T/8.",
      "learning_value": "Shows that changing phase shifts peak timing without changing amplitude or period."
    }
  ],
  "primary_visualization": {
    "type": "flow",
    "reason": "The core material develops a complete solution through a coherent derivation: restoring force → equation of motion → verified sinusoids → superposition → initial-condition fitting → amplitude and phase."
  },
  "planner": {
    "version": "1.1",
    "focus_ids": [
      "restoring_force",
      "motion_equation",
      "verify_sinusoid",
      "combine_solutions",
      "apply_initial_conditions",
      "amplitude_phase"
    ],
    "source_pages": [
      2,
      3,
      4,
      5,
      6,
      7,
      8
    ],
    "features": {
      "equations": true,
      "continuous_parameters": true,
      "time_dynamics": true,
      "spatial_relations": true,
      "finite_outcomes": false,
      "set_relations": false,
      "ordered_collection": false,
      "transitions": false,
      "analogy_suitable": false,
      "structure": true,
      "interaction_value": true
    },
    "family": "dynamic",
    "reason": "Use the ready numeric lab to compare position curves for a frictionless, one-dimensional spring–mass system. Vary positive k and m and initial conditions x₀ and vₓ,₀ using ω₀ = √(k/m) and x(t) = x₀ cos(ω₀t) + (vₓ,₀/ω₀) sin(ω₀t). Parameter comparison reveals how k/m controls the period while initial conditions determine amplitude and phase. Connect the curves to Fₓ = −kx, x″ = −(k/m)x, and the sine",
    "process": null,
    "execution": null,
    "adapted": false,
    "requested_family": "dynamic",
    "degraded": false,
    "recovery_codes": []
  },
  "numeric_lab_declarations": [
    {
      "id": "spring_initial_conditions",
      "source_pages": [
        4,
        6,
        7
      ],
      "parameters": [
        {
          "id": "stiffness",
          "label": "Spring constant k",
          "unit": "N/m",
          "min": 1.0,
          "max": 16.0,
          "default": 4.0,
          "step": 0.25,
          "parameter_kind": "adjustable"
        },
        {
          "id": "mass",
          "label": "Mass m",
          "unit": "kg",
          "min": 0.5,
          "max": 4.0,
          "default": 1.0,
          "step": 0.1,
          "parameter_kind": "adjustable"
        },
        {
          "id": "initial_position",
          "label": "Initial displacement x₀",
          "unit": "m",
          "min": -1.0,
          "max": 1.0,
          "default": 0.5,
          "step": 0.05,
          "parameter_kind": "adjustable"
        },
        {
          "id": "initial_velocity",
          "label": "Initial velocity vₓ,₀",
          "unit": "m/s",
          "min": -2.0,
          "max": 2.0,
          "default": 0.5,
          "step": 0.1,
          "parameter_kind": "adjustable"
        }
      ],
      "x": {
        "id": "time",
        "label": "Time t (s)",
        "min": 0.0,
        "max": 12.0,
        "points": 600
      },
      "series": [
        {
          "id": "position",
          "label": "Displacement x(t) (m)",
          "expression": "initial_position*cos(sqrt(stiffness/mass)*time)+(initial_velocity/sqrt(stiffness/mass))*sin(sqrt(stiffness/mass)*time)"
        }
      ],
      "derived_metrics": [
        {
          "id": "angular_frequency",
          "label": "Angular frequency ω₀",
          "expression": "sqrt(stiffness/mass)",
          "unit": "rad/s"
        },
        {
          "id": "period",
          "label": "Period T",
          "expression": "2*pi*sqrt(mass/stiffness)",
          "unit": "s"
        },
        {
          "id": "amplitude",
          "label": "Amplitude A",
          "expression": "sqrt(initial_position**2+(initial_velocity/sqrt(stiffness/mass))**2)",
          "unit": "m"
        }
      ]
    }
  ],
  "scene_declarations": null,
  "normalized_declarations": {},
  "affordances": [],
  "source_refs": {
    "declared_count": 92,
    "invalid": [],
    "valid": true
  },
  "grounding_status": "Validated source-page references only; semantic Atlas not compiled in first-pass stages.",
  "failure_reason": null
}
```

Predefined reasonable families: spatial_dynamics; numeric_lab; formal concept map.
Unsupported semantics to inspect: no damping or driving force; no amplitude interpreted as wavelength; no arbitrary 3D mechanics.
Static/formal conditions: Numeric/formal degradation is correct when the runtime cannot express the oscillator honestly.
Objective observations: selected family = dynamic; invalid raw analysis refs = []; rejected lab count = 0.
Compare source fixed conditions against the min/max/default and expressions above. A varying fitted/source constant, new formula, added dynamics or unmatched support is a review flag; this packet does not decide its semantic verdict.
**A verdict: HUMAN REVIEW PENDING.**

## circuits — 6.002 Lecture 12: First Order Circuits

[Original source](https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/84f4b553fc6a1ddd7007465041c4e213_6002_l12.pdf) · [Terms](https://ocw.mit.edu/pages/privacy-and-terms-of-use/) · CC BY-NC-SA 4.0

### 1. Source evidence and frozen conditions

Physical PDF pages: [6, 7, 8, 9, 10, 11, 12, 13]. Evaluation → original mapping: {"1": 6, "2": 7, "3": 8, "4": 9, "5": 10, "6": 11, "7": 12, "8": 13}.
Source-grounded concise paraphrases from the reviewed prospective packet: RC node equation; homogeneous and particular solutions; initial voltage; tau=RC; charging and discharging.
Fixed source conditions: 5 V/0 V examples and boundary conditions are source baselines.
Permitted adjustment/local operations: positive R and C; hypothetical input/initial voltage.

- Original PDF p.6: The capacitor node equation produces a first-order RC differential equation. Formula/concept: RC dv_C/dt + v_C = V_I. Fixed condition: The stated first-order circuit topology.
- Original PDF p.7: The input is constant and the initial capacitor voltage is given. Formula/concept: v_C(0) = V_0. Fixed condition: Constant input and specified initial condition.
- Original PDF p.12: The complete solution approaches the input voltage with time constant RC. Formula/concept: v_C(t) = V_I + (V_0 - V_I) exp(-t/(RC)); tau = RC. Fixed condition: Source solution and first-order assumptions.
- Original PDF p.13: Charging/discharging examples use input and initial voltage pairs 5/0 and 0/5 volts. Formula/concept: Exponential charging/discharging. Fixed condition: The two source example voltage pairs are fixed facts, distinct from a labeled hypothetical exploration.

### 2–8. Actual output, declarations, representation, grounding and differences

```json
{
  "quick_summary": "This lecture derives the constant-input response of an RC circuit using particular and homogeneous solutions. Applying the initial capacitor voltage gives vC(t) = VI + (V0 − VI)e^(−t/RC): the voltage starts at V0 and approaches VI with time constant τ = RC.",
  "key_concepts": [
    {
      "concept": "RC circuit model",
      "explanation": "A Thévenin voltage source vI(t) and resistance R drive a capacitor C. The output is the capacitor voltage vC(t).",
      "source_pages": [
        1,
        2
      ]
    },
    {
      "concept": "Node equation",
      "explanation": "The node method gives (vC − vI)/R + C dvC/dt = 0, or RC dvC/dt + vC = vI. An initial capacitor voltage is needed to determine the response.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Constant input and initial condition",
      "explanation": "The worked example assumes vI(t) = VI and vC(0) = V0.",
      "source_pages": [
        2,
        3
      ]
    },
    {
      "concept": "Particular solution",
      "explanation": "A particular solution satisfies the original driven equation. For a constant input, vCP = VI works because its time derivative is zero.",
      "source_pages": [
        4
      ]
    },
    {
      "concept": "Homogeneous solution",
      "explanation": "Setting the drive to zero gives RC dvCH/dt + vCH = 0. Trying vCH = Ae^(st) yields s = −1/(RC), so vCH = Ae^(−t/RC).",
      "source_pages": [
        5
      ]
    },
    {
      "concept": "Time constant",
      "explanation": "τ = RC has units of time and sets the exponential response rate. A larger τ produces a slower approach to the final voltage.",
      "source_pages": [
        1,
        5,
        7,
        8
      ]
    },
    {
      "concept": "Total solution and initial-condition fitting",
      "explanation": "Adding the particular and homogeneous solutions gives vC = VI + Ae^(−t/RC). Using vC(0) = V0 determines A = V0 − VI.",
      "source_pages": [
        3,
        6
      ]
    },
    {
      "concept": "Capacitor voltage response",
      "explanation": "The complete response is vC(t) = VI + (V0 − VI)e^(−t/RC). It starts at V0 and approaches VI; the transient is the difference from the final voltage.",
      "source_pages": [
        6,
        7
      ]
    },
    {
      "concept": "Capacitor current",
      "explanation": "iC = C dvC/dt = (VI − V0)e^(−t/RC)/R. The current decays toward zero and its sign depends on whether VI is above or below V0.",
      "source_pages": [
        6
      ]
    },
    {
      "concept": "Charging and discharging examples",
      "explanation": "For V0 = 0 V and VI = 5 V, the general solution gives 5 − 5e^(−t/RC). For V0 = 5 V and VI = 0 V, it gives 5e^(−t/RC). The charging formula printed on page 8 has a plus-sign error; its plotted curve and stated conditions agree with the minus-sign form.",
      "source_pages": [
        6,
        8
      ]
    }
  ],
  "relationships": [
    {
      "source": "Thévenin RC circuit",
      "relation": "is modeled by applying the node method to obtain",
      "target": "RC dvC/dt + vC = vI",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Constant input vI(t) = VI",
      "relation": "specializes the circuit equation to",
      "target": "RC dvC/dt + vC = VI",
      "source_pages": [
        2,
        3
      ]
    },
    {
      "source": "Particular solution",
      "relation": "satisfies",
      "target": "The original driven equation",
      "source_pages": [
        4
      ]
    },
    {
      "source": "Constant input VI",
      "relation": "admits the particular solution",
      "target": "vCP = VI",
      "source_pages": [
        4
      ]
    },
    {
      "source": "Homogeneous equation",
      "relation": "is obtained by setting the drive to zero in",
      "target": "The original circuit equation",
      "source_pages": [
        5
      ]
    },
    {
      "source": "Exponential trial vCH = Ae^(st)",
      "relation": "produces",
      "target": "Characteristic equation RCs + 1 = 0",
      "source_pages": [
        5
      ]
    },
    {
      "source": "Characteristic equation RCs + 1 = 0",
      "relation": "determines",
      "target": "s = −1/(RC)",
      "source_pages": [
        5
      ]
    },
    {
      "source": "Homogeneous solution",
      "relation": "has the form",
      "target": "vCH = Ae^(−t/RC)",
      "source_pages": [
        5
      ]
    },
    {
      "source": "Time constant τ",
      "relation": "equals",
      "target": "RC",
      "source_pages": [
        5,
        8
      ]
    },
    {
      "source": "RC",
      "relation": "has",
      "target": "Units of time",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Total solution",
      "relation": "is the sum of",
      "target": "Particular and homogeneous solutions",
      "source_pages": [
        3,
        6
      ]
    },
    {
      "source": "Initial condition vC(0) = V0",
      "relation": "determines the remaining constant",
      "target": "A = V0 − VI",
      "source_pages": [
        6
      ]
    },
    {
      "source": "A = V0 − VI",
      "relation": "gives the complete voltage response",
      "target": "vC(t) = VI + (V0 − VI)e^(−t/RC)",
      "source_pages": [
        6
      ]
    },
    {
      "source": "Capacitor voltage response",
      "relation": "starts at",
      "target": "V0",
      "source_pages": [
        6,
        7
      ]
    },
    {
      "source": "Capacitor voltage response",
      "relation": "approaches",
      "target": "VI",
      "source_pages": [
        6,
        7,
        8
      ]
    },
    {
      "source": "Capacitor current",
      "relation": "equals capacitance times the voltage derivative",
      "target": "iC = C dvC/dt",
      "source_pages": [
        6
      ]
    },
    {
      "source": "Complete voltage response",
      "relation": "yields",
      "target": "iC(t) = (VI − V0)e^(−t/RC)/R",
      "source_pages": [
        6
      ]
    },
    {
      "source": "V0 = 0 V and VI = 5 V",
      "relation": "produce",
      "target": "Charging from 0 V toward 5 V",
      "source_pages": [
        8
      ]
    },
    {
      "source": "V0 = 5 V and VI = 0 V",
      "relation": "produce",
      "target": "Discharging from 5 V toward 0 V",
      "source_pages": [
        8
      ]
    }
  ],
  "visual_evidence": [
    {
      "page": 1,
      "type": "diagram",
      "description": "A source, series resistor, and capacitor form the RC circuit. The capacitor voltage polarity and a dashed Thévenin boundary are marked.",
      "learning_value": "Connects the abstract variables to circuit components and identifies the output voltage."
    },
    {
      "page": 1,
      "type": "formula",
      "description": "The node equation is rearranged into RC dvC/dt + vC = vI. RC is circled and annotated as having units of time.",
      "learning_value": "Shows how the circuit becomes a first-order differential equation and highlights its characteristic time scale."
    },
    {
      "page": 2,
      "type": "formula",
      "description": "The constant-input conditions vI(t) = VI and vC(0) = V0 accompany RC dvC/dt + vC = VI.",
      "learning_value": "Separates the driving input from the initial capacitor state."
    },
    {
      "page": 4,
      "type": "formula",
      "description": "The choice vCP = VI is highlighted, and an arrow identifies its derivative as zero.",
      "learning_value": "Makes the verification of the particular solution explicit."
    },
    {
      "page": 6,
      "type": "formula",
      "description": "The initial condition determines A = V0 − VI, followed by the highlighted complete voltage response and a capacitor-current formula.",
      "learning_value": "Shows how the arbitrary homogeneous amplitude becomes a physically determined transient."
    },
    {
      "page": 7,
      "type": "graph",
      "description": "A green exponential curve rises from V0 toward the dashed VI level. Its initial tangent meets that level at the marked time RC.",
      "learning_value": "Links the initial value, final value, and time constant to visible features of the response."
    },
    {
      "page": 8,
      "type": "graph",
      "description": "Side-by-side green curves show charging from 0 V toward 5 V and discharging from 5 V toward 0 V, with step-input sketches. The charging expression is visibly printed with a plus sign, inconsistent with the curve and initial condition.",
      "learning_value": "Illustrates both response directions and provides an opportunity to check a formula against its initial value."
    },
    {
      "page": 8,
      "type": "waveform",
      "description": "A lower green waveform alternates between exponential rising and falling segments bounded by dashed voltage levels.",
      "learning_value": "Shows how repeated changes in the input generate successive charging and discharging intervals."
    }
  ],
  "primary_visualization": {
    "type": "flow",
    "reason": "The central structure is a coherent derivation from the circuit equation through particular and homogeneous solutions to an initial-condition-fitted response."
  },
  "planner": null,
  "numeric_lab_declarations": [
    {
      "id": "rc_voltage_response",
      "source_pages": [
        5,
        6,
        7,
        8
      ],
      "parameters": [
        {
          "id": "input_voltage",
          "label": "Constant input VI",
          "unit": "V",
          "min": 0.0,
          "max": 5.0,
          "default": 5.0,
          "step": 0.1,
          "parameter_kind": "adjustable"
        },
        {
          "id": "initial_voltage",
          "label": "Initial capacitor voltage V0",
          "unit": "V",
          "min": 0.0,
          "max": 5.0,
          "default": 0.0,
          "step": 0.1,
          "parameter_kind": "adjustable"
        },
        {
          "id": "time_constant",
          "label": "Time constant τ = RC",
          "unit": "s",
          "min": 0.1,
          "max": 2.0,
          "default": 1.0,
          "step": 0.1,
          "parameter_kind": "adjustable"
        }
      ],
      "x": {
        "id": "time",
        "label": "Time t (s)",
        "min": 0.0,
        "max": 10.0,
        "points": 500
      },
      "series": [
        {
          "id": "capacitor_voltage",
          "label": "Capacitor voltage vC(t) (V)",
          "expression": "input_voltage + (initial_voltage - input_voltage) * exp(-time / time_constant)"
        },
        {
          "id": "final_voltage",
          "label": "Final voltage VI (V)",
          "expression": "input_voltage"
        }
      ],
      "derived_metrics": [
        {
          "id": "transient_amplitude",
          "label": "Initial transient amplitude V0 − VI",
          "expression": "initial_voltage - input_voltage",
          "unit": "V"
        },
        {
          "id": "voltage_at_tau",
          "label": "Voltage at t = τ",
          "expression": "input_voltage + (initial_voltage - input_voltage) * exp(-1)",
          "unit": "V"
        }
      ]
    }
  ],
  "scene_declarations": null,
  "normalized_declarations": null,
  "affordances": null,
  "source_refs": {
    "declared_count": 86,
    "invalid": [],
    "valid": true
  },
  "grounding_status": "NOT_EVALUATED",
  "failure_reason": {
    "stage": "normalize",
    "code": "plan",
    "path": "$",
    "generated": {
      "planner_family": "dynamic",
      "reason_length": 400,
      "reason_fingerprint": "8b34ec6a53013c05",
      "required_capabilities": [
        "equations",
        "continuous_parameters",
        "time_dynamics",
        "structure",
        "interaction_value"
      ],
      "focus_ids": [
        "form_equation",
        "find_particular",
        "find_homogeneous",
        "combine_solutions",
        "apply_initial",
        "complete_response"
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
      "form_equation",
      "find_particular",
      "find_homogeneous",
      "combine_solutions",
      "apply_initial",
      "complete_response"
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
}
```

Predefined reasonable families: numeric_lab; dynamic_simulation; process_flow; formal comparison.
Unsupported semantics to inspect: no invented measured component values; no nonlinear transistor or second-order RLC model; no physical circuit rewiring handle.
Static/formal conditions: A formula/table/flow is correct without an unambiguous waveform inverse; generic bounded hypothetical defaults must be labeled.
Objective observations: selected family = None; invalid raw analysis refs = []; rejected lab count = 0.
Compare source fixed conditions against the min/max/default and expressions above. A varying fitted/source constant, new formula, added dynamics or unmatched support is a review flag; this packet does not decide its semantic verdict.
**A verdict: HUMAN REVIEW PENDING.**

## signals — Think DSP: Sounds and Signals

[Original source](https://greenteapress.com/thinkdsp/thinkdsp.pdf) · [Terms](https://greenteapress.com/) · CC BY-NC-SA 4.0 (PDF copyright page)

### 1. Source evidence and frozen conditions

Physical PDF pages: [14, 15, 16, 17, 18]. Evaluation → original mapping: {"1": 14, "2": 15, "3": 16, "4": 17, "5": 18}.
Source-grounded concise paraphrases from the reviewed prospective packet: period/frequency; waveform/timbre; harmonics and spectral decomposition; two-sinusoid mixture.
Fixed source conditions: 439 Hz observed bell and plotted recording; 440/880 Hz, 1.0/0.5 and offset=0 example baseline; original spectrum samples.
Permitted adjustment/local operations: hypothetical sine/cosine frequency, amplitude and phase; bounded time window.

- Original PDF p.14: The bell recording is periodic, about 2.3 ms per cycle and roughly 439 Hz. Formula/concept: frequency = 1/period. Fixed condition: These are observations of the displayed recording.
- Original PDF p.16: The violin spectrum includes a fundamental near 440 Hz and integer-multiple harmonics. Formula/concept: Harmonics at approximately 880, 1320, 1760 and 2200 Hz. Fixed condition: The displayed recording/spectrum is source evidence, not regenerated audio.
- Original PDF p.17: The example constructs a cosine at 440 Hz and a sine at 880 Hz with amplitudes 1.0 and 0.5 and zero offsets. Formula/concept: Superposition of two sinusoids. Fixed condition: Example defaults remain identified; code is source data and is never executed.

### 2–8. Actual output, declarations, representation, grounding and differences

```json
{
  "quick_summary": "Periodic sounds can be understood both as repeating waveforms in time and as collections of sinusoidal frequency components. The DFT produces a signal’s spectrum, and the FFT computes the DFT efficiently. Fundamental frequency usually determines pitch, while waveform shape determines timbre. The excerpt also shows how to combine sinusoidal signals, sample them into a Wave, and inspect a short segment.",
  "key_concepts": [
    {
      "concept": "Periodic signals, period, and frequency",
      "explanation": "A periodic signal repeats after a period T. Frequency f counts cycles per second in Hertz and satisfies f = 1/T. The bell example has a period of about 2.3 ms and a frequency of about 439 Hz; these are approximate measurements.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Sinusoids",
      "explanation": "Sinusoids have the shape of sine or cosine functions. A tuning fork produces a sinusoid because its tines undergo simple harmonic motion.",
      "source_pages": [
        1,
        4
      ]
    },
    {
      "concept": "Waveform and timbre",
      "explanation": "Waveform is the shape of a periodic signal. That shape determines timbre, the perceived quality of the sound. The violin waveform repeats but is more complex than the bell’s approximately sinusoidal waveform.",
      "source_pages": [
        1,
        2
      ]
    },
    {
      "concept": "Spectral decomposition and spectrum",
      "explanation": "Spectral decomposition expresses a signal as a sum of sinusoids at different frequencies. Its spectrum describes those components; the illustrated spectrum plots component amplitude against frequency.",
      "source_pages": [
        2,
        3
      ]
    },
    {
      "concept": "DFT and FFT",
      "explanation": "The discrete Fourier transform (DFT) takes a signal and produces its spectrum. The Fast Fourier transform (FFT) is an efficient algorithm for computing the DFT.",
      "source_pages": [
        2
      ]
    },
    {
      "concept": "Fundamental frequency, dominant frequency, and pitch",
      "explanation": "The fundamental is the lowest frequency component; the dominant frequency is the component with the greatest amplitude. They coincide in the violin example, but normally the fundamental determines pitch even when it is not dominant.",
      "source_pages": [
        3
      ]
    },
    {
      "concept": "Harmonics and octaves",
      "explanation": "Harmonics occur at integer multiples of the fundamental frequency. For a fundamental near 440 Hz, the excerpt identifies components near 880, 1320, 1760, and 2200 Hz. Moving up one octave doubles frequency.",
      "source_pages": [
        3
      ]
    },
    {
      "concept": "Signal parameters and addition",
      "explanation": "thinkdsp sinusoidal signals use frequency in Hz, amplitude in unspecified units, and phase offset in radians. Phase controls where a cycle starts. Adding signals creates a SumSignal representing their sum.",
      "source_pages": [
        4
      ]
    },
    {
      "concept": "Signal versus Wave",
      "explanation": "A Signal represents a mathematical function of time. A Wave stores its evaluated values at a sequence of times. A frame identifies a time point, while a sample is the measurement at that point.",
      "source_pages": [
        4
      ]
    },
    {
      "concept": "Sampling and segment inspection",
      "explanation": "make_wave specifies duration, start time, and framerate. The timestep is the reciprocal of framerate. A short segment makes individual cycles visible when a long plot would contain too many periods.",
      "source_pages": [
        4,
        5
      ]
    }
  ],
  "relationships": [
    {
      "source": "Periodic signal",
      "relation": "repeats after a time interval called",
      "target": "Period",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Cycle",
      "relation": "is one full repetition of",
      "target": "Periodic signal",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Frequency",
      "relation": "counts cycles per second and is the reciprocal of",
      "target": "Period",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Frequency",
      "relation": "is measured in",
      "target": "Hertz (Hz)",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Sinusoid",
      "relation": "has the shape of",
      "target": "Sine or cosine function",
      "source_pages": [
        1,
        4
      ]
    },
    {
      "source": "Simple harmonic motion of tuning-fork tines",
      "relation": "generates",
      "target": "Sinusoidal signal",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Waveform",
      "relation": "is the shape of",
      "target": "Periodic signal",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Waveform shape",
      "relation": "determines",
      "target": "Timbre",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Timbre",
      "relation": "is the perceived",
      "target": "Quality of sound",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Spectral decomposition",
      "relation": "expresses a signal as",
      "target": "Sum of sinusoids at different frequencies",
      "source_pages": [
        2
      ]
    },
    {
      "source": "DFT",
      "relation": "transforms a signal into",
      "target": "Spectrum",
      "source_pages": [
        2
      ]
    },
    {
      "source": "FFT",
      "relation": "efficiently computes",
      "target": "DFT",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Spectrum",
      "relation": "describes the sinusoidal components that sum to produce",
      "target": "Signal",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Spectrum plot",
      "relation": "shows component amplitude against",
      "target": "Frequency",
      "source_pages": [
        2,
        3
      ]
    },
    {
      "source": "Fundamental frequency",
      "relation": "is the",
      "target": "Lowest frequency component",
      "source_pages": [
        3
      ]
    },
    {
      "source": "Dominant frequency",
      "relation": "is the frequency of the",
      "target": "Largest-amplitude component",
      "source_pages": [
        3
      ]
    },
    {
      "source": "Fundamental frequency",
      "relation": "normally determines even when not dominant",
      "target": "Perceived pitch",
      "source_pages": [
        3
      ]
    },
    {
      "source": "Violin example’s fundamental",
      "relation": "is also its",
      "target": "Dominant frequency",
      "source_pages": [
        3
      ]
    },
    {
      "source": "Harmonic frequencies",
      "relation": "are integer multiples of",
      "target": "Fundamental frequency",
      "source_pages": [
        3
      ]
    },
    {
      "source": "One octave upward",
      "relation": "corresponds to",
      "target": "Doubling frequency",
      "source_pages": [
        3
      ]
    },
    {
      "source": "Illustrated harmonics near 880, 1320, 1760, and 2200 Hz",
      "relation": "approximately correspond to notes in",
      "target": "A major chord across multiple octaves",
      "source_pages": [
        3
      ]
    },
    {
      "source": "Equal temperament",
      "relation": "explains why some harmonic-to-note matches are",
      "target": "Approximate",
      "source_pages": [
        3
      ]
    },
    {
      "source": "Adding sinusoidal components",
      "relation": "reconstructs",
      "target": "Signal",
      "source_pages": [
        3,
        4
      ]
    },
    {
      "source": "Signal class",
      "relation": "is a parent class of",
      "target": "Sinusoid",
      "source_pages": [
        4
      ]
    },
    {
      "source": "Sinusoid",
      "relation": "represents",
      "target": "Sine and cosine signals",
      "source_pages": [
        4
      ]
    },
    {
      "source": "Phase offset",
      "relation": "controls",
      "target": "Starting position within a cycle",
      "source_pages": [
        4
      ]
    },
    {
      "source": "Signal addition",
      "relation": "creates",
      "target": "SumSignal",
      "source_pages": [
        4
      ]
    },
    {
      "source": "Signal",
      "relation": "represents",
      "target": "Mathematical function of time",
      "source_pages": [
        4
      ]
    },
    {
      "source": "Evaluating a Signal at a sequence of times",
      "relation": "produces values stored in",
      "target": "Wave",
      "source_pages": [
        4
      ]
    },
    {
      "source": "Frame",
      "relation": "identifies",
      "target": "Evaluation time point",
      "source_pages": [
        4
      ]
    },
    {
      "source": "Sample",
      "relation": "is the",
      "target": "Measurement at a time point",
      "source_pages": [
        4
      ]
    },
    {
      "source": "make_wave",
      "relation": "returns",
      "target": "Wave",
      "source_pages": [
        4
      ]
    },
    {
      "source": "Framerate",
      "relation": "specifies",
      "target": "Frames or samples per second",
      "source_pages": [
        5
      ]
    },
    {
      "source": "Timestep",
      "relation": "is the reciprocal of",
      "target": "Framerate",
      "source_pages": [
        5
      ]
    },
    {
      "source": "Wave.segment",
      "relation": "copies a selected time interval into",
      "target": "New Wave",
      "source_pages": [
        5
      ]
    },
    {
      "source": "Short waveform segment",
      "relation": "makes visible",
      "target": "Individual periods",
      "source_pages": [
        5
      ]
    }
  ],
  "visual_evidence": [
    {
      "page": 1,
      "type": "waveform",
      "description": "Figure 1.1 plots a bell recording against time, showing approximately three smooth, nearly sinusoidal cycles over about seven milliseconds. The time axis has a +7 s offset.",
      "learning_value": "Makes repetition and cycle duration visible, supporting the connection between period and frequency."
    },
    {
      "page": 2,
      "type": "waveform",
      "description": "Figure 1.2 shows a violin recording with repeated, complex patterns containing several local peaks and troughs within each cycle.",
      "learning_value": "Demonstrates that a signal can be periodic without being sinusoidal, connecting waveform complexity to timbre."
    },
    {
      "page": 3,
      "type": "graph",
      "description": "Figure 1.3 plots amplitude against frequency from 0 to 10,000 Hz. It contains narrow spectral peaks, with the strongest low-frequency peak near 440 Hz and additional peaks at higher frequencies.",
      "learning_value": "Shows how a complicated waveform becomes identifiable frequency components, and distinguishes peak location from peak strength."
    },
    {
      "page": 5,
      "type": "waveform",
      "description": "Figure 1.4 shows roughly three repetitions of the mixture of the 440 Hz cosine and 880 Hz sine signals. Each cycle has an asymmetric profile with a shoulder near zero.",
      "learning_value": "Provides a concrete visual result of sinusoidal addition: simple components create a more complex repeating waveform."
    }
  ],
  "primary_visualization": {
    "type": "flow",
    "reason": "The core learning structure is an explicit analysis-and-reconstruction process: a signal passes through the DFT to a spectrum, whose sinusoidal components can be added to reconstruct a time-domain signal."
  },
  "planner": {
    "version": "1.1",
    "focus_ids": [
      "time_signal",
      "apply_dft",
      "component_spectrum",
      "sum_components",
      "reconstructed_signal"
    ],
    "source_pages": [
      1,
      2,
      3,
      4,
      5
    ],
    "features": {
      "equations": true,
      "continuous_parameters": true,
      "time_dynamics": true,
      "spatial_relations": false,
      "finite_outcomes": false,
      "set_relations": false,
      "ordered_collection": false,
      "transitions": true,
      "analogy_suitable": false,
      "structure": true,
      "interaction_value": true
    },
    "family": "dynamic",
    "reason": "The source defines sine and cosine signals through frequency, amplitude, and phase offset, and explains their addition. The ready numeric lab can compare component curves and their summed waveform while learners vary these continuous parameters, starting with the supplied 440 Hz cosine and 880 Hz sine example. This makes the relationship between components and waveform shape directly observable; a",
    "process": null,
    "execution": null,
    "adapted": false,
    "requested_family": "dynamic",
    "degraded": false,
    "recovery_codes": []
  },
  "numeric_lab_declarations": [
    {
      "id": "harmonic_mixture",
      "source_pages": [
        4,
        5
      ],
      "parameters": [
        {
          "id": "cos_amp",
          "label": "440 Hz cosine amplitude",
          "unit": "unspecified amplitude units",
          "min": 0.0,
          "max": 1.0,
          "default": 1.0,
          "step": 0.05,
          "parameter_kind": "adjustable"
        },
        {
          "id": "sin_amp",
          "label": "880 Hz sine amplitude",
          "unit": "unspecified amplitude units",
          "min": 0.0,
          "max": 1.0,
          "default": 0.5,
          "step": 0.05,
          "parameter_kind": "adjustable"
        },
        {
          "id": "phase",
          "label": "880 Hz sine phase offset",
          "unit": "rad",
          "min": 0.0,
          "max": 6.283185307179586,
          "default": 0.0,
          "step": 0.05,
          "parameter_kind": "adjustable"
        }
      ],
      "x": {
        "id": "time",
        "label": "Time (s)",
        "min": 0.0,
        "max": 0.006818181818,
        "points": 400
      },
      "series": [
        {
          "id": "cos_component",
          "label": "440 Hz cosine",
          "expression": "cos_amp*cos(2*pi*440*time)"
        },
        {
          "id": "sin_component",
          "label": "880 Hz sine",
          "expression": "sin_amp*sin(2*pi*880*time+phase)"
        },
        {
          "id": "mixture",
          "label": "Sum of components",
          "expression": "cos_amp*cos(2*pi*440*time)+sin_amp*sin(2*pi*880*time+phase)"
        }
      ],
      "derived_metrics": []
    }
  ],
  "scene_declarations": null,
  "normalized_declarations": {},
  "affordances": [],
  "source_refs": {
    "declared_count": 83,
    "invalid": [],
    "valid": true
  },
  "grounding_status": "Validated source-page references only; semantic Atlas not compiled in first-pass stages.",
  "failure_reason": null
}
```

Predefined reasonable families: numeric_lab; formal concept map; comparison.
Unsupported semantics to inspect: no exact recovery of the recorded audio/spectrum from the screenshot; no execution of thinkdsp Python or audio download; no invented measured Fourier coefficients.
Static/formal conditions: Static descriptions are correct if only measured recordings are modeled or a safe symbolic demo is unsupported.
Objective observations: selected family = dynamic; invalid raw analysis refs = []; rejected lab count = 0.
Compare source fixed conditions against the min/max/default and expressions above. A varying fitted/source constant, new formula, added dynamics or unmatched support is a review flag; this packet does not decide its semantic verdict.
**A verdict: HUMAN REVIEW PENDING.**

## regression — OpenIntro Statistics 4e screen-reader edition: Least Squares Regression

[Original source](https://www.openintro.org/go/?id=os4_for_screen_reader) · [Terms](https://github.com/OpenIntroStat/openintro-statistics/blob/master/LICENSE.md) · CC BY-SA 3.0 text; excluded branding/cover

### 1. Source evidence and frozen conditions

Physical PDF pages: [355, 356, 357, 358, 359, 360]. Evaluation → original mapping: {"1": 355, "2": 356, "3": 357, "4": 358, "5": 359, "6": 360}.
Source-grounded concise paraphrases from the reviewed prospective packet: sum of squared residuals; b1=(sy/sx)R; line passes through means; interpretation of slope/intercept; prediction limitations.
Fixed source conditions: 50-student sample; means 101780/19940; sd 63200/5460; R=-0.499; fitted slope -0.0431 and intercept 24.319 in thousands; empirical source dots; all fitted results remain source facts, not freely adjustable parameters.
Permitted adjustment/local operations: prediction input inside observed range.

- Original PDF p.355: The gift-aid example uses a sample of fifty freshmen and compares fitted lines on the observed scatterplot. Formula/concept: Least-squares fitting of gift aid versus family income. Fixed condition: The sample and plotted empirical points are source facts.
- Original PDF p.358: The fitted slope uses standard deviations and correlation, and the fitted line passes through the sample means. Formula/concept: b1 = (s_y/s_x) R. Fixed condition: Means 101780/19940; SDs 63200/5460; R = -0.499.
- Original PDF p.359: The source reports the fitted line and interprets its estimated coefficients. Formula/concept: Rounded worked line: aid_hat = 24327 - 0.0431*income (dollars); software summary intercept 24319.3. Fixed condition: Fitted estimates are fixed results; prediction input can vary within the observed range.
- Original PDF p.360: Prediction is an estimate subject to cohort and model limitations. Formula/concept: Prediction limitations. Fixed condition: Do not infer a causal or guaranteed financial-aid rule.

### 2–8. Actual output, declarations, representation, grounding and differences

```json
{
  "quick_summary": "Least squares regression fits a line by minimizing the sum of squared residuals. The section uses family income and gift aid for 50 Elmhurst freshmen to show how to check model conditions, calculate a slope and intercept from summary statistics, and interpret predictions without confusing association with causation.",
  "key_concepts": [
    {
      "concept": "Elmhurst income–aid relationship",
      "explanation": "In a random sample of 50 freshmen, higher family income was associated with lower gift aid. The correlation was R = −0.499. Gift aid does not need to be repaid.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Least squares criterion",
      "explanation": "The least squares line minimizes e₁² + e₂² + ⋯ + eₙ². Squaring gives disproportionately greater weight to larger residuals: doubling a residual quadruples its squared contribution.",
      "source_pages": [
        1,
        2
      ]
    },
    {
      "concept": "Absolute-residual alternative",
      "explanation": "Another fitting criterion minimizes |e₁| + |e₂| + ⋯ + |eₙ|. It produces the dashed line in the Elmhurst scatterplot, whereas least squares produces the solid line.",
      "source_pages": [
        1,
        2
      ]
    },
    {
      "concept": "Model conditions",
      "explanation": "The chapter's regression methods generally require a linear trend, nearly normal residuals, roughly constant variability around the line, and independent observations. Curvature, unusual residuals, increasing spread, and correlated sequential observations are warning signs.",
      "source_pages": [
        2,
        3
      ]
    },
    {
      "concept": "Parameters and estimates",
      "explanation": "β₀ and β₁ denote the regression intercept and slope parameters; b₀ and b₁ are their estimates from observed data. The fitted prediction is written ŷ = b₀ + b₁x.",
      "source_pages": [
        4,
        5
      ]
    },
    {
      "concept": "Slope from summary statistics",
      "explanation": "The slope estimate is b₁ = (sᵧ/sₓ)R. For Elmhurst, (5460/63200)(−0.499) ≈ −0.0431 dollars of aid per dollar of family income.",
      "source_pages": [
        4,
        5
      ]
    },
    {
      "concept": "Mean-point property",
      "explanation": "The least squares line passes through (x̄, ȳ). For Elmhurst, this point is ($101,780, $19,940).",
      "source_pages": [
        4,
        5
      ]
    },
    {
      "concept": "Intercept calculation",
      "explanation": "Using ŷ − ȳ = b₁(x − x̄) gives b₀ = ȳ − b₁x̄. The worked example reports an intercept of $24,327, while software reports $24,319.3; the source attributes the small difference to rounding.",
      "source_pages": [
        5
      ]
    },
    {
      "concept": "Slope interpretation",
      "explanation": "A slope describes the estimated difference in the response for a one-unit increase in the explanatory variable. Here, an additional $1,000 of family income corresponds to about $43.10 less aid on average.",
      "source_pages": [
        6
      ]
    },
    {
      "concept": "Intercept interpretation",
      "explanation": "The intercept estimates the average response when x = 0, provided the model remains valid there. The Elmhurst intercept is meaningful because some sampled students had zero family income.",
      "source_pages": [
        6
      ]
    },
    {
      "concept": "Prediction and causal limitations",
      "explanation": "The equation estimates a trend, not an exact individual award. Aid policies may change across years, and these observational data do not establish that changing income causes aid to change.",
      "source_pages": [
        6
      ]
    },
    {
      "concept": "Regression software output",
      "explanation": "The output includes coefficient estimates, standard errors, t statistics, and p-values. For the slope, the reported standard error is 0.0108, the t statistic is −3.98, and the two-sided p-value for testing β₁ = 0 is 0.0002.",
      "source_pages": [
        5,
        6
      ]
    }
  ],
  "relationships": [
    {
      "source": "Family income",
      "relation": "is the explanatory variable used to predict",
      "target": "Gift aid",
      "source_pages": [
        4
      ]
    },
    {
      "source": "Higher family income",
      "relation": "is associated with",
      "target": "Lower gift aid",
      "source_pages": [
        1,
        6
      ]
    },
    {
      "source": "Gift aid",
      "relation": "is financial aid that",
      "target": "Does not need to be repaid",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Least squares line",
      "relation": "minimizes",
      "target": "Sum of squared residuals",
      "source_pages": [
        1,
        2
      ]
    },
    {
      "source": "Absolute-residual fit",
      "relation": "minimizes",
      "target": "Sum of residual magnitudes",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Squaring residuals",
      "relation": "gives greater relative penalty to",
      "target": "Large residuals",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Least squares regression methods in this chapter",
      "relation": "generally require",
      "target": "Linearity, nearly normal residuals, constant variability, and independence",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Nonlinear trend",
      "relation": "violates",
      "target": "Linearity condition",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Outliers and influential-point concerns",
      "relation": "can make unreasonable",
      "target": "Nearly normal residuals condition",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Increasing response spread as x increases",
      "relation": "violates",
      "target": "Constant variability condition",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Correlated successive observations",
      "relation": "violate",
      "target": "Independent observations condition",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Elmhurst data",
      "relation": "appear suitable for",
      "target": "Least squares regression",
      "source_pages": [
        3
      ]
    },
    {
      "source": "Observed data",
      "relation": "provide estimates b₀ and b₁ of",
      "target": "Parameters β₀ and β₁",
      "source_pages": [
        4,
        5
      ]
    },
    {
      "source": "Correlation and sample standard deviations",
      "relation": "determine through b₁ = (sᵧ/sₓ)R",
      "target": "Slope estimate",
      "source_pages": [
        4,
        5
      ]
    },
    {
      "source": "Least squares line",
      "relation": "passes through",
      "target": "Sample mean point (x̄, ȳ)",
      "source_pages": [
        4,
        5
      ]
    },
    {
      "source": "Slope and sample means",
      "relation": "determine through b₀ = ȳ − b₁x̄",
      "target": "Intercept estimate",
      "source_pages": [
        5
      ]
    },
    {
      "source": "Fitted response",
      "relation": "is marked with",
      "target": "A prediction hat",
      "source_pages": [
        5
      ]
    },
    {
      "source": "Slope",
      "relation": "describes",
      "target": "Estimated response difference per one-unit increase in x",
      "source_pages": [
        6
      ]
    },
    {
      "source": "Intercept",
      "relation": "describes, when the model is valid at zero",
      "target": "Average response at x = 0",
      "source_pages": [
        6
      ]
    },
    {
      "source": "Observations near x = 0",
      "relation": "support practical interpretation of",
      "target": "Intercept",
      "source_pages": [
        6
      ]
    },
    {
      "source": "Observational association",
      "relation": "does not establish",
      "target": "Causation",
      "source_pages": [
        6
      ]
    },
    {
      "source": "Regression prediction",
      "relation": "provides an imperfect estimate of",
      "target": "An individual student's aid",
      "source_pages": [
        6
      ]
    },
    {
      "source": "Changing aid policies across years",
      "relation": "can limit applicability of",
      "target": "The one-class Elmhurst model",
      "source_pages": [
        6
      ]
    },
    {
      "source": "Slope standard error",
      "relation": "quantifies uncertainty in",
      "target": "Slope point estimate",
      "source_pages": [
        6
      ]
    },
    {
      "source": "Slope t statistic and two-sided p-value",
      "relation": "refer to testing",
      "target": "Null hypothesis β₁ = 0",
      "source_pages": [
        6
      ]
    }
  ],
  "visual_evidence": [
    {
      "page": 1,
      "type": "graph",
      "description": "Figure 8.11 shows income–aid observations with two downward-sloping fitted lines. The solid line is the least squares fit; the dashed line minimizes absolute residual magnitudes.",
      "learning_value": "Connects negative association with a negative slope and shows that different fitting criteria can yield different lines."
    },
    {
      "page": 1,
      "type": "formula",
      "description": "Displayed formulas contrast |e₁| + ⋯ + |eₙ| with e₁² + ⋯ + eₙ².",
      "learning_value": "Makes the distinction between absolute and squared residual penalties explicit."
    },
    {
      "page": 2,
      "type": "graph",
      "description": "Figure 8.12 contains four fitted-data panels and corresponding residual panels: curvature, an unusually distant point, increasing spread, and correlated sequential patterns.",
      "learning_value": "Helps learners recognize visual warning signs for the chapter's regression conditions rather than only memorizing their names."
    },
    {
      "page": 5,
      "type": "formula",
      "description": "A highlighted procedure gives b₁ = (sᵧ/sₓ)R, the mean-point equation, and b₀ = ȳ − b₁x̄. The worked example expands the equation into predicted aid = 24,327 − 0.0431 × family income.",
      "learning_value": "Shows a complete, ordered calculation from summary statistics to a fitted prediction equation."
    },
    {
      "page": 5,
      "type": "table",
      "description": "Figure 8.14 lists the intercept and family-income coefficient with Estimate, Std. Error, t value, and Pr(>|t|) columns.",
      "learning_value": "Links hand-calculated coefficients to software output and separates coefficient estimates from inferential quantities."
    },
    {
      "page": 6,
      "type": "formula",
      "description": "The worked interpretation multiplies $1,000 by −0.0431 to obtain −$43.10; a highlighted box states the meanings of slope and intercept.",
      "learning_value": "Demonstrates how to translate a coefficient into a useful change in real-world units."
    }
  ],
  "primary_visualization": {
    "type": "flow",
    "reason": "The central worked procedure progresses from summary statistics to slope, mean-point anchoring, intercept, and contextual interpretation. A flow makes those dependencies easier to follow."
  },
  "planner": {
    "version": "1.1",
    "focus_ids": [
      "summary_stats",
      "compute_slope",
      "anchor_line",
      "fitted_equation",
      "interpret_model"
    ],
    "source_pages": [
      4,
      5,
      6
    ],
    "features": {
      "equations": true,
      "continuous_parameters": true,
      "time_dynamics": false,
      "spatial_relations": true,
      "finite_outcomes": false,
      "set_relations": false,
      "ordered_collection": true,
      "transitions": false,
      "analogy_suitable": false,
      "structure": true,
      "interaction_value": true
    },
    "family": "dynamic",
    "reason": "The ready numeric lab can connect the ordered derivation to meaningful parameter exploration: b₁ = (sᵧ/sₓ)R, b₀ = ȳ − b₁x̄, and ŷ = b₀ + b₁x. Comparing valid summary-statistic inputs shows how correlation and the standard-deviation ratio change the slope while the fitted line remains anchored at (x̄, ȳ). This makes the slope, intercept, and predictions easier to interpret without requiring time or",
    "process": null,
    "execution": null,
    "adapted": false,
    "requested_family": "dynamic",
    "degraded": false,
    "recovery_codes": []
  },
  "numeric_lab_declarations": [
    {
      "id": "correlation_and_line",
      "source_pages": [
        4,
        5,
        6
      ],
      "parameters": [
        {
          "id": "corr",
          "label": "Correlation R (exploration range)",
          "unit": "unitless",
          "min": -0.6,
          "max": 0.6,
          "default": -0.499,
          "step": 0.001,
          "parameter_kind": "adjustable"
        }
      ],
      "x": {
        "id": "income",
        "label": "Family income ($)",
        "min": 0.0,
        "max": 250000.0,
        "points": 400
      },
      "series": [
        {
          "id": "predicted_aid",
          "label": "Predicted gift aid ($)",
          "expression": "19940 + (5460 / 63200) * corr * (income - 101780)"
        }
      ],
      "derived_metrics": [
        {
          "id": "slope_value",
          "label": "Slope b₁",
          "expression": "(5460 / 63200) * corr",
          "unit": "$ aid per $ income"
        },
        {
          "id": "intercept_value",
          "label": "Intercept b₀",
          "expression": "19940 - (5460 / 63200) * corr * 101780",
          "unit": "$"
        },
        {
          "id": "aid_change_1000",
          "label": "Predicted aid difference per $1,000 income",
          "expression": "1000 * (5460 / 63200) * corr",
          "unit": "$"
        }
      ]
    }
  ],
  "scene_declarations": null,
  "normalized_declarations": {},
  "affordances": [],
  "source_refs": {
    "declared_count": 79,
    "invalid": [],
    "valid": true
  },
  "grounding_status": "Validated source-page references only; semantic Atlas not compiled in first-pass stages.",
  "failure_reason": null
}
```

Predefined reasonable families: numeric_lab; formal comparison; concept map.
Unsupported semantics to inspect: no causal scholarship policy claim; no real student data reconstruction; empirical points, source statistics and fitted results remain source facts; no adjustable hypothetical trial line unless explicitly supported by the original source.
Static/formal conditions: A formal equation and source plot is correct if fixed empirical data cannot be represented; no drag of observed dots.
Objective observations: selected family = dynamic; invalid raw analysis refs = []; rejected lab count = 0.
Compare source fixed conditions against the min/max/default and expressions above. A varying fitted/source constant, new formula, added dynamics or unmatched support is a review flag; this packet does not decide its semantic verdict.
**A verdict: HUMAN REVIEW PENDING.**

## probability — OpenIntro Statistics 4e screen-reader edition: Defining Probability

[Original source](https://www.openintro.org/go/?id=os4_for_screen_reader) · [Terms](https://github.com/OpenIntroStat/openintro-statistics/blob/master/LICENSE.md) · CC BY-SA 3.0 text; excluded branding/cover

### 1. Source evidence and frozen conditions

Physical PDF pages: [93, 94, 95, 96, 97, 98, 99, 100]. Evaluation → original mapping: {"1": 93, "2": 94, "3": 95, "4": 96, "5": 97, "6": 98, "7": 99, "8": 100}.
Source-grounded concise paraphrases from the reviewed prospective packet: disjoint events; die outcome sets A={1,2}, B={4,6}, D={2,3}; inclusive or and intersection correction; complement; non-uniform dice-sum distribution.
Fixed source conditions: six fair die outcomes and source memberships; 52-card counts; two-dice sum weights; given income/loan proportions.
Permitted adjustment/local operations: local event selection/set operations; Monte Carlo sample count with original probabilities.

- Original PDF p.93: A fair die illustrates disjoint individual outcomes and their addition rule. Formula/concept: Addition for disjoint outcomes. Fixed condition: Six source-defined die outcomes.
- Original PDF p.94: The die events are A={1,2}, B={4,6} and D={2,3}; A and B are disjoint, while A and D share outcome 2. Formula/concept: Membership and overlap. Fixed condition: Source event membership must remain unchanged.
- Original PDF p.97: Diamonds and face cards require subtracting overlap when computing inclusive-or probability. Formula/concept: P(A union B) = P(A) + P(B) - P(A intersection B). Fixed condition: 52-card example counts are fixed; no unjustified uniform aggregation.
- Original PDF p.98: The two-dice sum table assigns unequal probabilities to sums 2 through 12. Formula/concept: Weights 1,2,3,4,5,6,5,4,3,2,1 divided by 36. Fixed condition: The sums are not uniformly likely.

### 2–8. Actual output, declarations, representation, grounding and differences

```json
{
  "quick_summary": "Probability calculations depend on how events relate as sets of outcomes. Add probabilities for disjoint events; subtract shared probability when events overlap. Valid probability distributions list disjoint outcomes with probabilities between 0 and 1 that total 1. An event and its complement cover the whole sample space, so their probabilities add to 1.",
  "key_concepts": [
    {
      "concept": "Random process",
      "explanation": "A process with uncertain outcomes can be modeled probabilistically, even when its behavior is merely too difficult to predict exactly.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Sample space",
      "explanation": "The sample space S is the set of all possible outcomes. For one die, S = {1, 2, 3, 4, 5, 6}.",
      "source_pages": [
        6,
        8
      ]
    },
    {
      "concept": "Event",
      "explanation": "An event is a set of outcomes. For example, A = {1, 2} represents rolling either 1 or 2.",
      "source_pages": [
        2
      ]
    },
    {
      "concept": "Disjoint or mutually exclusive events",
      "explanation": "Disjoint events have no outcomes in common and cannot occur simultaneously. These two terms mean the same thing.",
      "source_pages": [
        1,
        2
      ]
    },
    {
      "concept": "Addition Rule for disjoint events",
      "explanation": "For disjoint events, P(A or B) = P(A) + P(B). The same principle applies to any collection of mutually disjoint outcomes.",
      "source_pages": [
        1,
        2,
        3
      ]
    },
    {
      "concept": "Union and inclusive or",
      "explanation": "A or B includes outcomes in A, in B, or in both. Statistical 'or' is inclusive unless explicitly stated otherwise.",
      "source_pages": [
        5
      ]
    },
    {
      "concept": "Intersection",
      "explanation": "A and B consists of outcomes belonging to both events. In the card example, the shared outcomes are J♦, Q♦, and K♦.",
      "source_pages": [
        4,
        5
      ]
    },
    {
      "concept": "General Addition Rule",
      "explanation": "For any two events, P(A or B) = P(A) + P(B) − P(A and B). Subtracting the intersection corrects double counting.",
      "source_pages": [
        4,
        5
      ]
    },
    {
      "concept": "Probability distribution",
      "explanation": "A probability distribution lists all disjoint outcomes and their probabilities. Every probability must be between 0 and 1, and the probabilities must sum to 1.",
      "source_pages": [
        6
      ]
    },
    {
      "concept": "Probability bar plot",
      "explanation": "Bar heights represent outcome probabilities. Numerical discrete outcomes can be plotted at their numerical locations, as with two-dice sums.",
      "source_pages": [
        6,
        7
      ]
    },
    {
      "concept": "Complement",
      "explanation": "The complement Aᶜ contains all outcomes in the sample space that are not in A. Since A and Aᶜ are disjoint and exhaustive, P(A) = 1 − P(Aᶜ).",
      "source_pages": [
        6,
        7,
        8
      ]
    }
  ],
  "relationships": [
    {
      "source": "Random process",
      "relation": "has possible outcomes collected in",
      "target": "Sample space",
      "source_pages": [
        1,
        6
      ]
    },
    {
      "source": "Event",
      "relation": "is a set of",
      "target": "Outcomes",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Sample space",
      "relation": "contains all possible",
      "target": "Outcomes",
      "source_pages": [
        6,
        8
      ]
    },
    {
      "source": "Disjoint events",
      "relation": "are also called",
      "target": "Mutually exclusive events",
      "source_pages": [
        1,
        2
      ]
    },
    {
      "source": "Disjoint events",
      "relation": "share no",
      "target": "Outcomes",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Disjoint events",
      "relation": "cannot occur",
      "target": "Simultaneously",
      "source_pages": [
        1,
        5
      ]
    },
    {
      "source": "Disjoint events",
      "relation": "have intersection probability",
      "target": "P(A and B) = 0",
      "source_pages": [
        5
      ]
    },
    {
      "source": "Addition Rule for disjoint events",
      "relation": "calculates",
      "target": "P(A or B) = P(A) + P(B)",
      "source_pages": [
        1,
        2
      ]
    },
    {
      "source": "Addition Rule for disjoint events",
      "relation": "extends to",
      "target": "Collections of mutually disjoint outcomes",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Inclusive or",
      "relation": "includes",
      "target": "A alone, B alone, and both A and B",
      "source_pages": [
        5
      ]
    },
    {
      "source": "Intersection",
      "relation": "contains",
      "target": "Outcomes shared by both events",
      "source_pages": [
        4,
        5
      ]
    },
    {
      "source": "Venn diagram",
      "relation": "represents shared outcomes using",
      "target": "Overlapping event regions",
      "source_pages": [
        4,
        5
      ]
    },
    {
      "source": "P(A) + P(B)",
      "relation": "counts twice",
      "target": "Probability of the intersection",
      "source_pages": [
        4,
        5
      ]
    },
    {
      "source": "General Addition Rule",
      "relation": "corrects double counting by subtracting",
      "target": "P(A and B)",
      "source_pages": [
        5
      ]
    },
    {
      "source": "General Addition Rule",
      "relation": "reduces to the disjoint Addition Rule when",
      "target": "P(A and B) = 0",
      "source_pages": [
        5
      ]
    },
    {
      "source": "Probability distribution",
      "relation": "lists",
      "target": "All disjoint outcomes and their probabilities",
      "source_pages": [
        6
      ]
    },
    {
      "source": "Probability distribution",
      "relation": "requires each probability to lie in",
      "target": "The interval from 0 to 1",
      "source_pages": [
        6
      ]
    },
    {
      "source": "Probability distribution",
      "relation": "requires probabilities to total",
      "target": "1",
      "source_pages": [
        6
      ]
    },
    {
      "source": "Probability bar plot",
      "relation": "encodes outcome probability through",
      "target": "Bar height",
      "source_pages": [
        6,
        7
      ]
    },
    {
      "source": "Complement Aᶜ",
      "relation": "contains",
      "target": "All sample-space outcomes outside A",
      "source_pages": [
        6,
        8
      ]
    },
    {
      "source": "A and Aᶜ",
      "relation": "are",
      "target": "Disjoint events",
      "source_pages": [
        7,
        8
      ]
    },
    {
      "source": "A and Aᶜ",
      "relation": "together cover",
      "target": "The sample space",
      "source_pages": [
        8
      ]
    },
    {
      "source": "Complement rule",
      "relation": "gives",
      "target": "P(A) + P(Aᶜ) = 1",
      "source_pages": [
        7,
        8
      ]
    },
    {
      "source": "Complement rule",
      "relation": "can simplify",
      "target": "Calculations where the excluded outcomes are easier to evaluate",
      "source_pages": [
        8
      ]
    }
  ],
  "visual_evidence": [
    {
      "page": 1,
      "type": "formula",
      "description": "A highlighted rule box states the Addition Rule for two disjoint outcomes and its extension to many disjoint outcomes.",
      "learning_value": "Connects mutual exclusivity to adding probabilities without overlap corrections."
    },
    {
      "page": 2,
      "type": "diagram",
      "description": "Figure 3.2 outlines A = {1, 2}, D = {2, 3}, and B = {4, 6} among the six die outcomes. A and D overlap at 2; B shares no outcomes with either.",
      "learning_value": "Makes disjointness a question of shared members, rather than the placement or shape of event boundaries."
    },
    {
      "page": 5,
      "type": "formula",
      "description": "The card calculation subtracts 3/52 from 13/52 + 12/52 to obtain 22/52. A highlighted box states the General Addition Rule.",
      "learning_value": "Explains why shared outcomes must be subtracted once after adding event probabilities."
    },
    {
      "page": 5,
      "type": "diagram",
      "description": "The loan Venn diagram shows 3839 mortgage-only loans, 950 loans with both attributes, 545 joint-only loans, and 4666 outside both events.",
      "learning_value": "Separates the intersection from the union. Exact counts give union probability 5334/10000 = 0.5334; the source's 0.534 uses rounded region probabilities."
    },
    {
      "page": 6,
      "type": "table",
      "description": "Figure 3.5 lists two-dice sums from 2 to 12 with probabilities 1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1 divided by 36.",
      "learning_value": "Provides a complete distribution and shows that different sums are not equally probable."
    },
    {
      "page": 6,
      "type": "table",
      "description": "Figure 3.6 presents three candidate household-income distributions. Row (a) totals 1.06, row (b) contains −0.27, and row (c) satisfies the probability requirements.",
      "learning_value": "Supports checking probability bounds and total probability independently."
    },
    {
      "page": 7,
      "type": "graph",
      "description": "Figure 3.7 displays household-income probabilities as four bars with heights 0.28, 0.27, 0.29, and 0.16.",
      "learning_value": "Shows how a categorical probability table becomes a visual summary."
    },
    {
      "page": 7,
      "type": "graph",
      "description": "Figure 3.8 plots the symmetric two-dice sum distribution, peaking at 7 and decreasing toward 2 and 12.",
      "learning_value": "Highlights the relative likelihood of sums and the distribution's symmetry."
    },
    {
      "page": 8,
      "type": "diagram",
      "description": "Figure 3.9 encloses all six die outcomes in S and separates D = {2, 3} from Dᶜ = {1, 4, 5, 6}.",
      "learning_value": "Shows that an event and its complement are nonoverlapping and together include every possible outcome."
    },
    {
      "page": 8,
      "type": "formula",
      "description": "The complement rule box states P(A) + P(Aᶜ) = 1 and P(A) = 1 − P(Aᶜ).",
      "learning_value": "Links the set partition to a shortcut for calculating probabilities."
    }
  ],
  "primary_visualization": {
    "type": "concept_map",
    "reason": "The core structure is the relationship between outcome sets and probability rules. No single ordered process dominates the sections on addition, distributions, and complements."
  },
  "planner": {
    "version": "1.1",
    "focus_ids": [
      "event_probability",
      "sample_space",
      "events",
      "disjoint",
      "intersection",
      "union_rule",
      "disjoint_rule",
      "distribution",
      "complement"
    ],
    "source_pages": [
      1,
      2,
      4,
      5,
      6,
      7,
      8
    ],
    "features": {
      "equations": true,
      "continuous_parameters": true,
      "time_dynamics": false,
      "spatial_relations": false,
      "finite_outcomes": true,
      "set_relations": true,
      "ordered_collection": true,
      "transitions": false,
      "analogy_suitable": false,
      "structure": true,
      "interaction_value": true
    },
    "family": "dynamic",
    "reason": "Use the ready numeric lab to compare valid probability parameters in P(A ∪ B) = P(A) + P(B) − P(A ∩ B) and P(Aᶜ) = 1 − P(A). Varying overlap reveals why simple addition double-counts shared outcomes and why disjoint events are the zero-overlap case. Keep comparisons within valid probability constraints and connect them to the source's die and card examples. Distribution probabilities must remain e",
    "process": null,
    "execution": null,
    "adapted": false,
    "requested_family": "dynamic",
    "degraded": false,
    "recovery_codes": []
  },
  "numeric_lab_declarations": [
    {
      "id": "overlap_lab",
      "source_pages": [
        5
      ],
      "parameters": [
        {
          "id": "prob_a",
          "label": "p_A = P(A)",
          "unit": "probability",
          "min": 0.25,
          "max": 0.5,
          "default": 0.3333333333333333,
          "step": 0.01,
          "parameter_kind": "adjustable"
        },
        {
          "id": "prob_b",
          "label": "p_B = P(B)",
          "unit": "probability",
          "min": 0.25,
          "max": 0.5,
          "default": 0.3333333333333333,
          "step": 0.01,
          "parameter_kind": "adjustable"
        }
      ],
      "x": {
        "id": "overlap",
        "label": "Overlap probability u = P(A and B)",
        "min": 0.0,
        "max": 0.25,
        "points": 400
      },
      "series": [
        {
          "id": "union_probability",
          "label": "Correct union probability",
          "expression": "prob_a + prob_b - overlap"
        },
        {
          "id": "uncorrected_sum",
          "label": "Sum before correcting overlap",
          "expression": "prob_a + prob_b"
        }
      ],
      "derived_metrics": []
    }
  ],
  "scene_declarations": null,
  "normalized_declarations": {},
  "affordances": [],
  "source_refs": {
    "declared_count": 108,
    "invalid": [],
    "valid": true
  },
  "grounding_status": "Validated source-page references only; semantic Atlas not compiled in first-pass stages.",
  "failure_reason": null
}
```

Predefined reasonable families: probability_sets; formal comparison; concept map.
Unsupported semantics to inspect: do not treat dice sums as uniformly likely; no arbitrary changes to source probabilities; no unlimited 52-outcome world if contract exceeds bounds.
Static/formal conditions: A bounded six-outcome die subset is honest with scope disclosed; other examples may stay formal. Dragging geometry is N/A.
Objective observations: selected family = dynamic; invalid raw analysis refs = []; rejected lab count = 0.
Compare source fixed conditions against the min/max/default and expressions above. A varying fitted/source constant, new formula, added dynamics or unmatched support is a review flag; this packet does not decide its semantic verdict.
**A verdict: HUMAN REVIEW PENDING.**

## search — Think Python 2e Appendix B: Analysis of Algorithms, Search

[Original source](https://greenteapress.com/thinkpython2/thinkpython2.pdf) · [Terms](https://greenteapress.com/) · CC BY-NC 3.0 (PDF copyright page)

### 1. Source evidence and frozen conditions

Physical PDF pages: [226, 227]. Evaluation → original mapping: {"1": 226, "2": 227}.
Source-grounded concise paraphrases from the reviewed prospective packet: sequential search O(n); sorted-list bisection O(log n); constant-time list operations; hashing and dictionaries.
Fixed source conditions: algorithm correctness and complexity assumptions; source contains no measured timing dataset.
Permitted adjustment/local operations: local navigation through declared process; explicit hypothetical sorted input only if safely resolved.

- Original PDF p.226: Basic Python-operation costs and general loop-growth rules precede the search section. Formula/concept: O(n^a) body repeated n times gives O(n^(a+1)); fixed k does not change growth order. Fixed condition: These are complexity rules, not measured timing data.
- Original PDF p.227: Linear search scans the collection; bisection halves a sorted sequence, and hash-table lookup is separately discussed. Formula/concept: Linear O(n); sorted bisection O(log n). Fixed condition: Bisection requires sorted input; no resolved hypothetical input sequence is provided.

### 2–8. Actual output, declarations, representation, grounding and differences

```json
{
  "quick_summary": "The excerpt explains how Python operation costs depend on input size, how loop iteration counts combine with the cost of each iteration, and how data structures affect search efficiency. Constant factors can change actual speed without changing growth order. Linear search is O(n), bisection on ordered data is O(log n), and dictionary lookup is described as constant time.",
  "key_concepts": [
    {
      "concept": "Growth order versus actual runtime",
      "explanation": "Big-O describes how work grows with input size, not exact execution time. A faster implementation or a fixed multiplier can change runtime without changing its growth order.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Constant-time operations",
      "explanation": "The excerpt treats ordinary arithmetic and sequence or dictionary indexing as constant time. Very large integers are an exception because arithmetic cost grows with their number of digits.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Loop cost",
      "explanation": "A loop's cost depends on both its iteration count and its body cost. With an O(n^a) body, n or n/k iterations give O(n^(a+1)), while a fixed k iterations give O(n^a), provided k is independent of n.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Linear traversal and aggregation",
      "explanation": "Traversing all n elements with constant-time work per element is O(n). Both an explicit summation loop and sum are linear, although sum generally has a smaller leading coefficient. min and max are also linear.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Length-dependent sequence operations",
      "explanation": "Most string and tuple operations are described as linear, with indexing and len as constant-time exceptions. Slicing depends on output length; concatenation depends on the combined operand lengths; join depends on the total length of the strings. Bounded-length string operations are treated as constant time.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "List-operation exceptions",
      "explanation": "Most list methods are described as linear. Appending is O(1) on average because occasional resizing costs are spread over many appends. Removing the last element is constant time, and sorting is O(n log n).",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Dictionary-operation costs",
      "explanation": "Most dictionary operations are described as constant time. update depends on the size of the incoming dictionary. Creating keys, values, or items iteration objects is described as constant time, but traversing them is linear.",
      "source_pages": [
        1,
        2
      ]
    },
    {
      "concept": "Linear search",
      "explanation": "Linear search examines collection items in sequence and stops when it finds the target. Its worst case examines the entire collection, giving O(n). Sequence membership and string methods such as find and count are described as using linear search.",
      "source_pages": [
        2
      ]
    },
    {
      "concept": "Bisection search",
      "explanation": "On an ordered sequence, compare the target with the middle item and continue in the appropriate half. Repeated halving gives O(log n); about 20 steps suffice for one million items. Obtaining the required ordering may involve extra work.",
      "source_pages": [
        2
      ]
    },
    {
      "concept": "Hashtable search",
      "explanation": "Hashtables support search described as constant time without requiring sorted items. Python dictionaries use hashtables, explaining the stated constant-time behavior of dictionary membership and most dictionary operations.",
      "source_pages": [
        2
      ]
    }
  ],
  "relationships": [
    {
      "source": "Big-O growth order",
      "relation": "is unchanged by multiplication or division by",
      "target": "a fixed constant",
      "source_pages": [
        1
      ]
    },
    {
      "source": "sum",
      "relation": "has the same linear growth order but typically a smaller leading coefficient than",
      "target": "an explicit list-summation loop",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Ordinary arithmetic",
      "relation": "is described as",
      "target": "constant time",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Very large integer arithmetic",
      "relation": "has runtime that increases with",
      "target": "the number of digits",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Sequence and dictionary indexing",
      "relation": "is described as",
      "target": "constant time",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Full traversal with a constant-time body",
      "relation": "has",
      "target": "linear runtime",
      "source_pages": [
        1
      ]
    },
    {
      "source": "An O(n^a) loop body executed n times",
      "relation": "produces",
      "target": "O(n^(a+1)) total loop cost",
      "source_pages": [
        1
      ]
    },
    {
      "source": "An O(n^a) loop body executed a fixed k times",
      "relation": "retains",
      "target": "O(n^a) total loop cost",
      "source_pages": [
        1
      ]
    },
    {
      "source": "An O(n^a) loop body executed n/k times for fixed k",
      "relation": "produces",
      "target": "O(n^(a+1)) total loop cost",
      "source_pages": [
        1
      ]
    },
    {
      "source": "min and max",
      "relation": "have",
      "target": "linear runtime",
      "source_pages": [
        1
      ]
    },
    {
      "source": "String and tuple indexing and len",
      "relation": "are exceptions to generally linear operations because they are",
      "target": "constant time",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Slice runtime",
      "relation": "is proportional to",
      "target": "output length rather than input size",
      "source_pages": [
        1
      ]
    },
    {
      "source": "String concatenation runtime",
      "relation": "depends on",
      "target": "the sum of operand lengths",
      "source_pages": [
        1
      ]
    },
    {
      "source": "String join runtime",
      "relation": "depends on",
      "target": "the total length of the strings",
      "source_pages": [
        1
      ]
    },
    {
      "source": "String operations on lengths bounded by a constant",
      "relation": "are treated as",
      "target": "constant time",
      "source_pages": [
        1
      ]
    },
    {
      "source": "List append",
      "relation": "occasionally triggers",
      "target": "copying into a larger location",
      "source_pages": [
        1
      ]
    },
    {
      "source": "n list appends",
      "relation": "have O(n) total cost, yielding",
      "target": "O(1) average cost per append",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Removing the last list element",
      "relation": "has",
      "target": "constant-time cost",
      "source_pages": [
        1
      ]
    },
    {
      "source": "List sorting",
      "relation": "has",
      "target": "O(n log n) cost",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Dictionary update runtime",
      "relation": "is proportional to",
      "target": "the size of the dictionary passed as an argument",
      "source_pages": [
        1
      ]
    },
    {
      "source": "keys, values, and items",
      "relation": "are described as constant-time creation of",
      "target": "iteration objects",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Traversing dictionary iteration objects",
      "relation": "has",
      "target": "linear runtime",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Search",
      "relation": "determines",
      "target": "whether a target belongs to a collection, often returning its index",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Linear search",
      "relation": "checks items sequentially until",
      "target": "the target is found or the collection is exhausted",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Linear search",
      "relation": "has",
      "target": "O(n) worst-case runtime",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Sequence membership, find, and count",
      "relation": "are described as using",
      "target": "linear search",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Bisection search",
      "relation": "requires",
      "target": "an ordered sequence",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Bisection search",
      "relation": "repeatedly halves",
      "target": "the remaining search region",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Repeated halving in bisection",
      "relation": "gives",
      "target": "O(log n) search runtime",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Preparing data for bisection",
      "relation": "may require",
      "target": "extra work to put the sequence in order",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Hashtable search",
      "relation": "is described as constant time without requiring",
      "target": "sorted items",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Python dictionaries",
      "relation": "are implemented using",
      "target": "hashtables",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Hashtable implementation",
      "relation": "explains the stated constant-time behavior of",
      "target": "dictionary membership and most dictionary operations",
      "source_pages": [
        2
      ]
    }
  ],
  "visual_evidence": [],
  "primary_visualization": {
    "type": "concept_map",
    "reason": "The core structure connects operation costs, growth-order rules, relevant input sizes, and search implementations. Bisection's procedure is important but does not dominate the overall material."
  },
  "planner": {
    "version": "1.1",
    "focus_ids": [
      "runtime_analysis",
      "growth_order",
      "basic_costs",
      "loop_cost",
      "dictionary_costs",
      "linear_search",
      "bisection_search"
    ],
    "source_pages": [
      1,
      2
    ],
    "features": {
      "equations": true,
      "continuous_parameters": true,
      "time_dynamics": false,
      "spatial_relations": false,
      "finite_outcomes": false,
      "set_relations": false,
      "ordered_collection": true,
      "transitions": false,
      "analogy_suitable": false,
      "structure": true,
      "interaction_value": true
    },
    "family": "dynamic",
    "reason": "Use the ready numeric lab to compare illustrative constant, linear, and logarithmic growth curves and vary their leading coefficients. This makes the distinction between growth order and constant factors visible and connects loop cost to iteration count. Input size represents an integer count; smooth curves are scaling illustrations, not measured Python timings or exact consequences of Big-O alone",
    "process": null,
    "execution": null,
    "adapted": false,
    "requested_family": "dynamic",
    "degraded": false,
    "recovery_codes": []
  },
  "numeric_lab_declarations": [
    {
      "id": "loop_growth_demo",
      "source_pages": [
        1
      ],
      "parameters": [
        {
          "id": "a",
          "label": "Body-cost exponent a",
          "unit": "dimensionless",
          "min": 0.0,
          "max": 2.0,
          "default": 1.0,
          "step": 0.25,
          "parameter_kind": "adjustable"
        },
        {
          "id": "k",
          "label": "Fixed factor k, independent of n",
          "unit": "dimensionless",
          "min": 1.0,
          "max": 10.0,
          "default": 5.0,
          "step": 1.0,
          "parameter_kind": "adjustable"
        }
      ],
      "x": {
        "id": "n",
        "label": "Input size n",
        "min": 10.0,
        "max": 100.0,
        "points": 400
      },
      "series": [
        {
          "id": "body_work",
          "label": "One body execution: n^a",
          "expression": "n**a"
        },
        {
          "id": "fixed_count_work",
          "label": "Fixed k iterations: k n^a",
          "expression": "k*n**a"
        },
        {
          "id": "scaled_count_work",
          "label": "n/k iterations: n^(a+1)/k",
          "expression": "n**(a+1)/k"
        }
      ],
      "derived_metrics": []
    }
  ],
  "scene_declarations": null,
  "normalized_declarations": {},
  "affordances": [],
  "source_refs": {
    "declared_count": 64,
    "invalid": [],
    "valid": true
  },
  "grounding_status": "Validated source-page references only; semantic Atlas not compiled in first-pass stages.",
  "failure_reason": null
}
```

Predefined reasonable families: process_flow; formal flow; comparison.
Unsupported semantics to inspect: no execution of generated Python; no unsupported arbitrary binary-search machine; no invented measured benchmarks.
Static/formal conditions: A read-only flow/comparison is correct when bounded execution is unsupported.
Objective observations: selected family = dynamic; invalid raw analysis refs = []; rejected lab count = 0.
Compare source fixed conditions against the min/max/default and expressions above. A varying fitted/source constant, new formula, added dynamics or unmatched support is a review flag; this packet does not decide its semantic verdict.
**A verdict: HUMAN REVIEW PENDING.**

## complexity — Think Python 2e Appendix B: Order of Growth

[Original source](https://greenteapress.com/thinkpython2/thinkpython2.pdf) · [Terms](https://greenteapress.com/) · CC BY-NC 3.0 (PDF copyright page)

### 1. Source evidence and frozen conditions

Physical PDF pages: [223, 224, 225]. Evaluation → original mapping: {"1": 223, "2": 224, "3": 225}.
Source-grounded concise paraphrases from the reviewed prospective packet: asymptotic analysis; linear vs quadratic; 100n+1 vs n^2+n+1; Big-O growth table.
Fixed source conditions: source example coefficients 100 and 1; Big-O definitions and table classes.
Permitted adjustment/local operations: positive integer input size n for illustrative operation counts.

- Original PDF p.223: Algorithm analysis compares growth as input size increases. Formula/concept: Asymptotic analysis. Fixed condition: Growth class differs from measured machine timing.
- Original PDF p.224: The illustrative count functions compare a linear expression with a quadratic one. Formula/concept: 100n+1 versus n^2+n+1. Fixed condition: Source coefficients stay fixed; n is illustrative input size.
- Original PDF p.225: The Big-O table orders common growth classes. Formula/concept: Constant, logarithmic, linear, quadratic and other growth classes. Fixed condition: Definitions/table classifications are source facts.

### 2–8. Actual output, declarations, representation, grounding and differences

```json
{
  "quick_summary": "Algorithm analysis compares how resource requirements grow with input size. By counting operations under a machine model and examining dominant terms, we can predict which algorithms scale better. Growth classes are useful for large inputs, but coefficients, input characteristics, hardware, and crossover points still matter in practice.",
  "key_concepts": [
    {
      "concept": "Algorithm analysis",
      "explanation": "Studies algorithm performance, especially run time and space requirements, to guide design decisions.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Machine models and operation counts",
      "explanation": "A specified machine model makes comparisons less dependent on particular hardware by measuring the number of steps or operations.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Worst-case and average-case analysis",
      "explanation": "Performance depends on the dataset. Worst-case analysis examines the most demanding inputs; average-case analysis can be useful but requires deciding which inputs to average over.",
      "source_pages": [
        1,
        2
      ]
    },
    {
      "concept": "Run time as a function of input size",
      "explanation": "Expressing operation counts as a function of input size n reveals scaling. The example compares A(n) = 100n + 1 with B(n) = n² + n + 1.",
      "source_pages": [
        2
      ]
    },
    {
      "concept": "Leading terms and growth classes",
      "explanation": "For a polynomial, the leading term has the highest exponent and determines eventual growth. Constant multipliers and lower-order terms do not change its growth class. The source uses Big-Oh notation informally for these classes; formally, Big-Oh specifies an asymptotic upper bound.",
      "source_pages": [
        2,
        3
      ]
    },
    {
      "concept": "Common orders of growth",
      "explanation": "The listed families are constant O(1), logarithmic O(log n), linear O(n), linearithmic O(n log n), quadratic O(n²), cubic O(n³), and exponential O(cⁿ), with c > 1 for exponential growth.",
      "source_pages": [
        3
      ]
    },
    {
      "concept": "Crossover points",
      "explanation": "An algorithm with better asymptotic growth can still be slower for small inputs. In the example, B is faster at n = 10, while A is slightly faster at n = 100 and increasingly better for larger n.",
      "source_pages": [
        2
      ]
    },
    {
      "concept": "Practical limitations",
      "explanation": "Growth classes do not determine exact performance. Coefficients, lower-order terms, hardware, programming language, and input characteristics can matter substantially, especially for small problems.",
      "source_pages": [
        2,
        3
      ]
    },
    {
      "concept": "Logarithmic and exponential bases",
      "explanation": "Changing a logarithm's fixed base only introduces a constant factor, so its growth class is unchanged. The source also groups exponential bases as equivalent, but this is mathematically inaccurate: for example, 3ⁿ is not O(2ⁿ). Different bases greater than 1 belong to the exponential family without necessarily sharing a tight growth class.",
      "source_pages": [
        3
      ]
    }
  ],
  "relationships": [
    {
      "source": "Algorithm analysis",
      "relation": "studies",
      "target": "Run time and space requirements",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Algorithm analysis",
      "relation": "supports",
      "target": "Performance predictions and design decisions",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Hardware characteristics",
      "relation": "can change",
      "target": "Relative algorithm performance",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Machine models",
      "relation": "provide a basis for counting",
      "target": "Algorithm steps or operations",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Dataset characteristics",
      "relation": "can change",
      "target": "Relative algorithm performance",
      "source_pages": [
        1,
        2
      ]
    },
    {
      "source": "Worst-case analysis",
      "relation": "addresses input variability by examining",
      "target": "The most demanding case",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Average-case analysis",
      "relation": "requires choosing",
      "target": "A set of cases to average over",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Input size",
      "relation": "is the independent variable in",
      "target": "Run-time functions",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Run-time functions",
      "relation": "are grouped by",
      "target": "Order of growth",
      "source_pages": [
        2,
        3
      ]
    },
    {
      "source": "Algorithm A",
      "relation": "requires",
      "target": "100n + 1 steps",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Algorithm B",
      "relation": "requires",
      "target": "n² + n + 1 steps",
      "source_pages": [
        2
      ]
    },
    {
      "source": "A polynomial's leading term",
      "relation": "is its term with",
      "target": "The highest exponent",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Leading terms",
      "relation": "determine",
      "target": "Eventual polynomial growth",
      "source_pages": [
        2,
        3
      ]
    },
    {
      "source": "Constant coefficients and lower-order terms",
      "relation": "can affect",
      "target": "Small-input performance and crossover points",
      "source_pages": [
        2,
        3
      ]
    },
    {
      "source": "2n, 100n, and n + 1",
      "relation": "share",
      "target": "Linear growth O(n)",
      "source_pages": [
        3
      ]
    },
    {
      "source": "Polynomial run times with leading term proportional to n²",
      "relation": "have",
      "target": "Quadratic growth O(n²)",
      "source_pages": [
        3
      ]
    },
    {
      "source": "Linear growth",
      "relation": "eventually grows more slowly than",
      "target": "Quadratic growth",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Algorithm B",
      "relation": "is faster at n = 10 than",
      "target": "Algorithm A",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Algorithm A",
      "relation": "is faster at n = 100 and the larger tabulated inputs than",
      "target": "Algorithm B",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Changing a logarithm's fixed base",
      "relation": "introduces only",
      "target": "A constant multiplier",
      "source_pages": [
        3
      ]
    },
    {
      "source": "Exponential growth",
      "relation": "limits practical use to",
      "target": "Small problems",
      "source_pages": [
        3
      ]
    },
    {
      "source": "Equal growth classes",
      "relation": "do not establish",
      "target": "Which implementation is faster",
      "source_pages": [
        3
      ]
    },
    {
      "source": "Bubble sort",
      "relation": "is described as",
      "target": "Conceptually simple but slow for large datasets",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Profiling",
      "relation": "can establish whether optimizing sorting would significantly improve",
      "target": "Application performance",
      "source_pages": [
        1
      ]
    }
  ],
  "visual_evidence": [],
  "primary_visualization": {
    "type": "concept_map",
    "reason": "The core learning task is understanding how comparison assumptions, run-time functions, dominant terms, growth classes, and practical caveats relate. The numerical comparison is an illustration, not the appendix's dominant structure."
  },
  "planner": {
    "version": "1.1",
    "focus_ids": [
      "runtime_functions",
      "algorithm_example",
      "crossover",
      "leading_terms",
      "growth_classes",
      "practical_limits"
    ],
    "source_pages": [
      2,
      3
    ],
    "features": {
      "equations": true,
      "continuous_parameters": true,
      "time_dynamics": false,
      "spatial_relations": false,
      "finite_outcomes": false,
      "set_relations": true,
      "ordered_collection": true,
      "transitions": false,
      "analogy_suitable": false,
      "structure": true,
      "interaction_value": true
    },
    "family": "dynamic",
    "reason": "The ready numeric lab can compare the source-supported curves 100n + 1 and n² + n + 1 while learners vary the input-size range. Their positive crossover is n = 99, illustrating why a linear algorithm can cost more for small inputs yet scale better for large inputs. Comparing the supplied linear examples 2n, 100n, and n + 1 also distinguishes practical coefficients from growth-class membership. Use",
    "process": null,
    "execution": null,
    "adapted": false,
    "requested_family": "dynamic",
    "degraded": false,
    "recovery_codes": []
  },
  "numeric_lab_declarations": [
    {
      "id": "runtime_crossover_demo",
      "source_pages": [
        2
      ],
      "parameters": [
        {
          "id": "a",
          "label": "Linear coefficient a (source example: 100)",
          "unit": "operations per input unit",
          "min": 2.0,
          "max": 200.0,
          "default": 100.0,
          "step": 1.0,
          "parameter_kind": "adjustable"
        }
      ],
      "x": {
        "id": "n",
        "label": "Input size n (integer sizes are the algorithmic interpretation)",
        "min": 1.0,
        "max": 300.0,
        "points": 400
      },
      "series": [
        {
          "id": "linear_cost",
          "label": "A: linear operation count",
          "expression": "a*n+1"
        },
        {
          "id": "quadratic_cost",
          "label": "B: quadratic operation count",
          "expression": "n**2+n+1"
        }
      ],
      "derived_metrics": [
        {
          "id": "positive_crossover",
          "label": "Positive crossover input size",
          "expression": "a-1",
          "unit": "input units"
        }
      ]
    }
  ],
  "scene_declarations": null,
  "normalized_declarations": {},
  "affordances": [],
  "source_refs": {
    "declared_count": 68,
    "invalid": [],
    "valid": true
  },
  "grounding_status": "Validated source-page references only; semantic Atlas not compiled in first-pass stages.",
  "failure_reason": null
}
```

Predefined reasonable families: comparison; numeric_lab; concept map.
Unsupported semantics to inspect: do not present operation count as measured wall-clock time; no changing source algorithm coefficients; no source-supported hardware benchmark claim.
Static/formal conditions: A comparison/table is sufficient; numeric count curves are optional and must stay illustrative.
Objective observations: selected family = dynamic; invalid raw analysis refs = []; rejected lab count = 0.
Compare source fixed conditions against the min/max/default and expressions above. A varying fitted/source constant, new formula, added dynamics or unmatched support is a review flag; this packet does not decide its semantic verdict.
**A verdict: HUMAN REVIEW PENDING.**

## spectrum — Tour of the Electromagnetic Spectrum 3e: Unit Conversion Scale

[Original source](https://science.nasa.gov/wp-content/uploads/2023/08/tour-of-the-ems-tagged-v7-0.pdf) · [Terms](https://www.nasa.gov/nasa-brand-center/images-and-media/) · NASA general educational/informational media permission; attribution; no endorsement

### 1. Source evidence and frozen conditions

Physical PDF pages: [35]. Evaluation → original mapping: {"1": 35}.
Source-grounded concise paraphrases from the reviewed prospective packet: frequency/wavelength/energy unit conventions; scientific notation; unit conversion scale table; positive wavelength values.
Fixed source conditions: every source table cell and size comparison; vacuum conversion baseline approximately c=3e8 m/s if explained as general physics.
Permitted adjustment/local operations: explicitly hypothetical positive wavelength/frequency conversion within numeric limits.

- Original PDF p.35: The conversion table presents electromagnetic scales using convenient frequency, wavelength and energy units. Formula/concept: Examples: 10 kHz corresponds to 30 km; 1 GHz corresponds to 0.3 m. Fixed condition: Every printed table cell and size comparison remains unchanged; no zero wavelength or fabricated propagation scene.

### 2–8. Actual output, declarations, representation, grounding and differences

```json
{
  "quick_summary": "Electromagnetic radiation can be described by frequency, wavelength, or energy. Different spectral regions conventionally use different units, but this table expresses every example as a wavelength in meters so that scales can be compared directly. Scientific notation and familiar size references make the enormous range easier to interpret.",
  "key_concepts": [
    {
      "concept": "Three descriptions of electromagnetic radiation",
      "explanation": "Frequency, wavelength, and energy are alternative ways to describe electromagnetic radiation.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Conventional units by spectral region",
      "explanation": "Radio and microwaves usually use frequency in hertz; infrared and visible light use wavelength units; X-rays and gamma rays use energy in electron volts. These conventions keep numerical values convenient.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Wavelength in meters as a common reference",
      "explanation": "The table converts the different descriptions into wavelength in meters, allowing examples expressed in otherwise different units to be compared.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Equivalent wavelength units",
      "explanation": "A wavelength can be written in several equivalent units. For example, 1000 nanometers equals 1 micrometer, and 5000 angstroms equals 500 nanometers.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Scientific notation",
      "explanation": "The scientific-notation column expresses the same meter values compactly. For example, 0.0000005 m is 5.0 × 10⁻⁷ m.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Inverse patterns in the conversion examples",
      "explanation": "The table shows shorter wavelengths for higher frequencies and higher energies. For example, increasing frequency from 10 kHz to 100 kHz reduces wavelength from 30,000 m to 3,000 m.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Physical size references",
      "explanation": "Pictures of the Statue of Liberty, a baseball, a human hair, a soap-bubble membrane, an atom, and a nucleus provide approximate scale references. They are visual guides, not exact equality statements for every neighboring row.",
      "source_pages": [
        1
      ]
    }
  ],
  "relationships": [
    {
      "source": "Electromagnetic radiation",
      "relation": "can be described by",
      "target": "Frequency",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Electromagnetic radiation",
      "relation": "can be described by",
      "target": "Wavelength",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Electromagnetic radiation",
      "relation": "can be described by",
      "target": "Energy",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Radio and microwaves",
      "relation": "are conventionally described using",
      "target": "Frequency in hertz",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Infrared and visible light",
      "relation": "are conventionally described using",
      "target": "Wavelength",
      "source_pages": [
        1
      ]
    },
    {
      "source": "X-rays and gamma rays",
      "relation": "are conventionally described using",
      "target": "Energy in electron volts",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Conventional unit choices",
      "relation": "help avoid",
      "target": "Inconveniently large or small numerical values",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Wavelength in meters",
      "relation": "provides a common basis for",
      "target": "Comparing the table's radiation examples",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Scientific notation",
      "relation": "compactly represents",
      "target": "The same wavelength values in meters",
      "source_pages": [
        1
      ]
    },
    {
      "source": "1000 nanometers",
      "relation": "equals",
      "target": "1 micrometer or 1.0 × 10⁻⁶ m",
      "source_pages": [
        1
      ]
    },
    {
      "source": "5000 angstroms",
      "relation": "equals",
      "target": "500 nanometers or 5.0 × 10⁻⁷ m",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Higher frequency in the listed examples",
      "relation": "corresponds to",
      "target": "Shorter wavelength",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Higher energy in the listed examples",
      "relation": "corresponds to",
      "target": "Shorter wavelength",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Physical size references",
      "relation": "help interpret",
      "target": "Wavelength scales",
      "source_pages": [
        1
      ]
    }
  ],
  "visual_evidence": [
    {
      "page": 1,
      "type": "table",
      "description": "A five-column conversion table aligns discipline units, alternate units, decimal wavelength in meters, scientific notation in meters, and size comparisons. Its wavelength entries range from 3.0 × 10⁴ m to 1.2 × 10⁻¹⁵ m.",
      "learning_value": "Reading across a row reveals equivalent descriptions; reading down the meter columns reveals the large range of wavelength scales."
    },
    {
      "page": 1,
      "type": "image",
      "description": "The size-comparison column contains circular illustrations or photographs of the Statue of Liberty, a baseball, a human hair, a soap bubble, an atom, and a nucleus, with labeled horizontal guide lines.",
      "learning_value": "The images anchor abstract lengths to familiar or microscopic objects. Their placement should be interpreted as approximate scale guidance rather than exact measurements."
    }
  ],
  "primary_visualization": {
    "type": "concept_map",
    "reason": "The main structure connects frequency, wavelength, and energy through conventional units and a common meter scale. No ordered process dominates the page."
  },
  "planner": {
    "version": "1.1",
    "focus_ids": [
      "radiation",
      "frequency",
      "wavelength",
      "energy",
      "meter_scale",
      "equivalent_units",
      "scientific_notation",
      "size_references"
    ],
    "source_pages": [
      1
    ],
    "features": {
      "equations": false,
      "continuous_parameters": false,
      "time_dynamics": false,
      "spatial_relations": false,
      "finite_outcomes": false,
      "set_relations": true,
      "ordered_collection": false,
      "transitions": false,
      "analogy_suitable": true,
      "structure": true,
      "interaction_value": false
    },
    "family": "static",
    "reason": "Use a structured comparison linking radio and microwaves to frequency in Hertz, infrared and visible light to wavelength in meters, and X-rays and gamma rays to energy in electron volts. Highlight that a common wavelength scale in meters enables comparison across these conventions, with scientific notation and size references aiding interpretation. The supplied excerpt lacks complete conversion120",
    "process": null,
    "execution": null,
    "adapted": false,
    "requested_family": "static",
    "degraded": false,
    "recovery_codes": []
  },
  "numeric_lab_declarations": [],
  "scene_declarations": null,
  "normalized_declarations": {},
  "affordances": [],
  "source_refs": {
    "declared_count": 38,
    "invalid": [],
    "valid": true
  },
  "grounding_status": "Validated source-page references only; semantic Atlas not compiled in first-pass stages.",
  "failure_reason": null
}
```

Predefined reasonable families: comparison; numeric_lab; formal table.
Unsupported semantics to inspect: no zero wavelength; no invented full spectrum dataset or new 3D propagation scene; no claimed exact page-box grounding before Atlas validation.
Static/formal conditions: Static table is correct if numeric dynamic ranges exceed the bounded evaluator. Only physical PDF page 35 is ingested: photo/stock pages are excluded.
Objective observations: selected family = static; invalid raw analysis refs = []; rejected lab count = 0.
Compare source fixed conditions against the min/max/default and expressions above. A varying fitted/source constant, new formula, added dynamics or unmatched support is a review flag; this packet does not decide its semantic verdict.
**A verdict: HUMAN REVIEW PENDING.**

## debugging — Think Python 2e Appendix A: Debugging

[Original source](https://greenteapress.com/thinkpython2/thinkpython2.pdf) · [Terms](https://greenteapress.com/) · CC BY-NC 3.0 (PDF copyright page)

### 1. Source evidence and frozen conditions

Physical PDF pages: [215, 216]. Evaluation → original mapping: {"1": 215, "2": 216}.
Source-grounded concise paraphrases from the reviewed prospective packet: syntax/runtime/semantic errors; incremental testing; localizing syntax faults; debugging strategy.
Fixed source conditions: error-category meanings; source advice.
Permitted adjustment/local operations: local reading/selection only.

- Original PDF p.215: The appendix distinguishes syntax, runtime and semantic errors and discusses debugging strategy. Formula/concept: Three error categories. Fixed condition: Category meanings and source advice; no numerical world is declared.
- Original PDF p.216: Incremental changes and localizing a syntax fault are recommended. Formula/concept: Incremental debugging. Fixed condition: Static/formal reading and selection are justified; no executable debugger or drag handle is supplied.

### 2–8. Actual output, declarations, representation, grounding and differences

```json
{
  "quick_summary": "Effective debugging starts by distinguishing syntax, runtime, and semantic errors. These pages focus on syntax errors: interpret the reported location cautiously, check common structural mistakes, and verify that Python is running the file you actually edited.",
  "key_concepts": [
    {
      "concept": "Error classification",
      "explanation": "The first debugging task is to identify the kind of error. Syntax, runtime, and semantic errors require different kinds of investigation.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Syntax errors",
      "explanation": "The interpreter detects problems with program structure while translating source code into byte code. A missing colon after a def header is one example.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Runtime errors",
      "explanation": "These occur during execution. Error messages often identify the location and executing functions; infinite recursion can eventually exceed the maximum recursion depth.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Semantic errors",
      "explanation": "A program runs without reporting an error but produces an unintended result. Unexpected expression evaluation order is one possible cause.",
      "source_pages": [
        1
      ]
    },
    {
      "concept": "Reported location versus actual cause",
      "explanation": "A syntax error message identifies where Python noticed a problem, not necessarily where it began. The cause may be on the preceding line.",
      "source_pages": [
        1,
        2
      ]
    },
    {
      "concept": "Targeted source inspection",
      "explanation": "For incremental development, inspect the most recently added line. For copied code, compare every character while remembering that the reference itself may contain mistakes.",
      "source_pages": [
        2
      ]
    },
    {
      "concept": "Syntax checklist",
      "explanation": "Check reserved keywords, header colons, matching straight quotes, terminated triple-quoted strings, closed delimiters, = versus == in conditionals, consistent indentation, and potentially troublesome pasted characters.",
      "source_pages": [
        2
      ]
    },
    {
      "concept": "Unclosed strings and delimiters",
      "explanation": "An unterminated triple-quoted string can absorb later code or produce an error far from its origin. An unclosed parenthesis, brace, or bracket makes Python treat the next line as part of the current statement.",
      "source_pages": [
        2
      ]
    },
    {
      "concept": "Edited code versus executed code",
      "explanation": "If changes have no effect, verify that Python is running the file being edited. A deliberate syntax error near the beginning provides a diagnostic test; if it is not detected, the new code is not being run. Unsaved changes are one possible cause.",
      "source_pages": [
        2
      ]
    }
  ],
  "relationships": [
    {
      "source": "Debugging",
      "relation": "begins by identifying",
      "target": "Error classification",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Error classification",
      "relation": "distinguishes",
      "target": "Syntax errors, runtime errors, and semantic errors",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Syntax errors",
      "relation": "are detected during",
      "target": "Translation of source code into byte code",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Syntax errors",
      "relation": "indicate problems with",
      "target": "Program structure",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Missing colon after a def header",
      "relation": "is an example of",
      "target": "Syntax errors",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Runtime errors",
      "relation": "occur during",
      "target": "Program execution",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Runtime error messages",
      "relation": "often report",
      "target": "Error location and executing functions",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Infinite recursion",
      "relation": "eventually causes",
      "target": "Maximum recursion depth exceeded",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Semantic errors",
      "relation": "produce",
      "target": "Unintended results without error messages",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Unexpected expression evaluation order",
      "relation": "can cause",
      "target": "Semantic errors",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Syntax error messages",
      "relation": "identify",
      "target": "Where Python noticed a problem",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Actual syntax error cause",
      "relation": "may precede",
      "target": "Reported error location",
      "source_pages": [
        1
      ]
    },
    {
      "source": "Incremental development",
      "relation": "helps narrow inspection to",
      "target": "The most recently added line",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Copied code",
      "relation": "should be checked through",
      "target": "Character-by-character comparison with the reference",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Reference code",
      "relation": "may itself contain",
      "target": "Syntax errors",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Unterminated triple-quoted strings",
      "relation": "can cause",
      "target": "A distant error or later code being treated as a string",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Unclosed opening delimiters",
      "relation": "make Python interpret",
      "target": "The next line as part of the current statement",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Mixed tabs and spaces",
      "relation": "can cause",
      "target": "Indentation problems",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Python-aware text editors",
      "relation": "help maintain",
      "target": "Consistent indentation",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Non-ASCII characters",
      "relation": "may cause problems, although",
      "target": "Python 3 usually handles them",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Changes having no effect",
      "relation": "may indicate a mismatch between",
      "target": "Edited code and executed code",
      "source_pages": [
        2
      ]
    },
    {
      "source": "An undetected deliberate syntax error",
      "relation": "indicates",
      "target": "The new code is not being run",
      "source_pages": [
        2
      ]
    },
    {
      "source": "Unsaved edits",
      "relation": "can explain",
      "target": "Changes having no effect",
      "source_pages": [
        2
      ]
    }
  ],
  "visual_evidence": [],
  "primary_visualization": {
    "type": "concept_map",
    "reason": "Understanding depends on linking error categories to diagnostic clues and syntax-checking techniques. The checklist is not a mandatory sequence, and the brief file-verification test is not the central process of the excerpt."
  },
  "planner": {
    "version": "1.1",
    "focus_ids": [
      "debugging",
      "syntax",
      "runtime",
      "semantic",
      "location",
      "inspection",
      "checklist",
      "running_code"
    ],
    "source_pages": [
      1,
      2
    ],
    "features": {
      "equations": false,
      "continuous_parameters": false,
      "time_dynamics": false,
      "spatial_relations": false,
      "finite_outcomes": true,
      "set_relations": false,
      "ordered_collection": true,
      "transitions": false,
      "analogy_suitable": false,
      "structure": true,
      "interaction_value": false
    },
    "family": "static",
    "reason": "Use a structured comparison of syntax, runtime, and semantic errors, paired with a syntax-debugging checklist. Distinguish when each error is detected and what its symptoms indicate. Connect syntax errors to cautious interpretation of reported locations, close inspection of recent or copied code, common structural checks, and verification that the edited file is executed. The numbered checks are a",
    "process": null,
    "execution": null,
    "adapted": false,
    "requested_family": "static",
    "degraded": false,
    "recovery_codes": []
  },
  "numeric_lab_declarations": [],
  "scene_declarations": null,
  "normalized_declarations": {},
  "affordances": [],
  "source_refs": {
    "declared_count": 51,
    "invalid": [],
    "valid": true
  },
  "grounding_status": "Validated source-page references only; semantic Atlas not compiled in first-pass stages.",
  "failure_reason": null
}
```

Predefined reasonable families: formal flow; concept map; comparison.
Unsupported semantics to inspect: no numerical physics world; no fabricated executable debugger or source code; no justified numeric drag handle.
Static/formal conditions: Formal/static representation is the intended success, preserving selection/source navigation without fabricated manipulation.
Objective observations: selected family = static; invalid raw analysis refs = []; rejected lab count = 0.
Compare source fixed conditions against the min/max/default and expressions above. A varying fitted/source constant, new formula, added dynamics or unmatched support is a review flag; this packet does not decide its semantic verdict.
**A verdict: HUMAN REVIEW PENDING.**

# Additional objective review observations

The first-pass packet remains immutable. These later observations do not change expectations, outputs or A-axis verdicts. See source-evidence-supplement.json for precise source-location and rounded-estimate clarifications.

## circular

The Numeric Lab declares coefA and coefB adjustable at defaults 0.3 and 0.9; its curves implement the source angular-law example rather than a rendered moving circle. Frozen expectations require source-example coefficients to remain identifiable baseline facts. No angular-velocity parameter is declared; do not infer a signed/positive domain from coefA/coefB. time is the Lab x variable, not a parameter.

Original planner declaration (including rejected declarations):

```json
{
  "version": "1.1",
  "focus_ids": [
    "position_basis",
    "basis_derivatives",
    "tangent_velocity",
    "acceleration_components",
    "uniform_motion",
    "orbit_measures"
  ],
  "source_pages": [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8
  ],
  "features": {
    "equations": true,
    "continuous_parameters": true,
    "time_dynamics": true,
    "spatial_relations": true,
    "finite_outcomes": false,
    "set_relations": false,
    "ordered_collection": false,
    "transitions": false,
    "analogy_suitable": false,
    "structure": true,
    "interaction_value": true
  },
  "preferred": "dynamic",
  "reason": "Use the ready numeric lab to compare source-supported circular-motion equations as radius and angular speed vary: v = rω, a_r = −rω², T = 2π/ω, and f = ω/(2π), with positive radius and angular speed for period comparisons. Parameter exploration reveals that constant speed does not mean zero acceleration and distinguishes linear speed scaling from quadratic centripetal-acceleration scaling. The non",
  "process": {
    "collections": [],
    "states": [],
    "transitions": [],
    "annotations": []
  },
  "execution": null
}
```

Deep source-to-runtime objective observation:

```json
{
  "material_id": "circular",
  "A": "HUMAN_REVIEW_PENDING",
  "B": "PASS",
  "browser_status": "PENDING_REAL_BROWSER",
  "browser_errors": "NOT_EVALUATED",
  "context_jumps": "NOT_EVALUATED",
  "direct_manipulation": {
    "available": false,
    "targets": [],
    "absence_is_not_automatic_failure": true
  },
  "post_compilation_api_delta": 0,
  "atlas_status": "accepted",
  "regions": 19,
  "atlas_diagnostics": [
    "regions[13].plain_text",
    "regions[14].plain_text"
  ],
  "selected_region": "p4_acceleration_decomposition",
  "selected_semantic_id": "acceleration_components",
  "semantic_identity_continuity": true,
  "source_grounding": "Validated Atlas link; semantic support/location needs human review",
  "target_ownership": true,
  "linked_support": {
    "semantic_id": "acceleration_components",
    "source_region_ids": [
      "p4_acceleration_decomposition",
      "p6_kinematics_example",
      "p6_example_acceleration",
      "p6_zero_centripetal"
    ],
    "source_pages": [
      4,
      6
    ],
    "support": [
      {
        "region_id": "p4_acceleration_decomposition",
        "page": 4,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p6_kinematics_example",
        "page": 6,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p6_example_acceleration",
        "page": 6,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p6_zero_centripetal",
        "page": 6,
        "kind": "estimated_region",
        "confidence": "high"
      }
    ],
    "representation_ids": [],
    "manipulation_target_ids": [],
    "formal_parameter_ids": [],
    "manipulable": false,
    "reason_not_manipulable": "No validated direct manipulation is available; use the formal view and existing controls."
  },
  "interaction": "existing Numeric Lab canonical slider callbacks",
  "commit_accepted": true,
  "linked_projection": [
    {
      "demo_id": "angular_acceleration_lab",
      "parameter_id": "coefA",
      "canonical_value": 0.64,
      "baseline": 0.3,
      "curve_changed": true,
      "stale_callback_rejected": true,
      "comparison_rows": [
        {
          "id": "coefA",
          "label": "Angular-law coefficient A",
          "unit": "rad/s³",
          "baseline": 0.3,
          "current": 0.64,
          "delta": 0.34,
          "generated_range": true
        }
      ]
    }
  ],
  "baseline_current_separation": "Compiled defaults retained; callback updates existing Lab store only",
  "atomic_rejection": "Stale callback rejection tested; arbitrary out-of-range callback injection not claimed",
  "source_roundtrip": {
    "focus_preserved": true,
    "supporting_region": "p4_acceleration_decomposition",
    "selected_source_context_preserved": true
  },
  "source_immutable": true
}
```

Actual generated Source Atlas regions (estimated boxes/transcriptions, requiring human location/semantic review):

```json
{
  "atlas_version": "1.0",
  "processed_pages": [
    4,
    6,
    8
  ],
  "regions": [
    {
      "region_id": "p8_frequency_relation",
      "page": 8,
      "bbox": {
        "x0": 0.265,
        "y0": 0.124,
        "x1": 0.405,
        "y1": 0.145
      },
      "type": "formula",
      "label": "Frequency, period, and angular speed relation",
      "semantic_ids": [
        "orbit_measures"
      ],
      "source_text_excerpt": "f = 1/T = ω/2π",
      "parent_region_id": null,
      "related_region_ids": [
        "p8_acceleration_magnitude"
      ],
      "layer": "formulas",
      "grounding_note": "Inline relation in the opening paragraph.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p8_acceleration_magnitude",
      "page": 8,
      "bbox": {
        "x0": 0.447,
        "y0": 0.182,
        "x1": 0.856,
        "y1": 0.225
      },
      "type": "formula",
      "label": "Centripetal acceleration magnitude in terms of period",
      "semantic_ids": [
        "orbit_measures"
      ],
      "source_text_excerpt": "|a_r| = 4π²r/T². (6.4.9)",
      "parent_region_id": null,
      "related_region_ids": [
        "p8_frequency_relation"
      ],
      "layer": "formulas",
      "grounding_note": "Displayed equation includes magnitude bars around the radial component.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p8_centripetal_definition",
      "page": 8,
      "bbox": {
        "x0": 0.145,
        "y0": 0.454,
        "x1": 0.858,
        "y1": 0.543
      },
      "type": "definition",
      "label": "Inward acceleration and changing velocity direction",
      "semantic_ids": [],
      "source_text_excerpt": "Any radial inward acceleration is called centripetal acceleration.",
      "parent_region_id": null,
      "related_region_ids": [
        "p8_orbit_diagram",
        "p8_velocity_triangle"
      ],
      "layer": "structure",
      "grounding_note": "Paragraph immediately above the two geometric figures.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p8_orbit_diagram",
      "page": 8,
      "bbox": {
        "x0": 0.192,
        "y0": 0.558,
        "x1": 0.423,
        "y1": 0.712
      },
      "type": "diagram",
      "label": "Figure 6.4: tangent velocities around a circular orbit",
      "semantic_ids": [],
      "source_text_excerpt": "",
      "parent_region_id": null,
      "related_region_ids": [
        "p8_velocity_triangle",
        "p8_centripetal_definition"
      ],
      "layer": "structure",
      "grounding_note": "Lower-left circle shows nearby radius vectors, angular separation, tangent arrows, and a unit-vector inset.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p8_velocity_triangle",
      "page": 8,
      "bbox": {
        "x0": 0.613,
        "y0": 0.561,
        "x1": 0.782,
        "y1": 0.668
      },
      "type": "diagram",
      "label": "Figure 6.5: geometric change in velocity",
      "semantic_ids": [],
      "source_text_excerpt": "",
      "parent_region_id": null,
      "related_region_ids": [
        "p8_orbit_diagram",
        "p8_delta_velocity"
      ],
      "layer": "structure",
      "grounding_note": "Lower-right vector triangle compares velocities at two nearby times.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p8_delta_velocity",
      "page": 8,
      "bbox": {
        "x0": 0.642,
        "y0": 0.563,
        "x1": 0.66,
        "y1": 0.666
      },
      "type": "vector",
      "label": "Downward change-in-velocity vector",
      "semantic_ids": [],
      "source_text_excerpt": "",
      "parent_region_id": "p8_velocity_triangle",
      "related_region_ids": [],
      "layer": "vectors",
      "grounding_note": "Vertical arrow forms the left side of the velocity triangle; the Δv label is immediately to its left.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p4_chord_formula",
      "page": 4,
      "bbox": {
        "x0": 0.447,
        "y0": 0.09,
        "x1": 0.856,
        "y1": 0.119
      },
      "type": "formula",
      "label": "Small-angle chord approximation",
      "semantic_ids": [
        "tangent_velocity"
      ],
      "source_text_excerpt": "|Δr⃗| ≅ r Δθ. (6.2.14)",
      "parent_region_id": null,
      "related_region_ids": [
        "p4_speed_limit",
        "p4_tangent_diagram"
      ],
      "layer": "formulas",
      "grounding_note": "Displayed approximation at the top of the page.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p4_speed_limit",
      "page": 4,
      "bbox": {
        "x0": 0.274,
        "y0": 0.241,
        "x1": 0.857,
        "y1": 0.292
      },
      "type": "formula",
      "label": "Speed obtained from the displacement limit",
      "semantic_ids": [
        "tangent_velocity"
      ],
      "source_text_excerpt": "v ≡ |v⃗(t)| = lim |Δr⃗|/Δt = lim r|Δθ|/Δt = r lim |Δθ|/Δt = r|dθ/dt| = rω. (6.2.15)",
      "parent_region_id": null,
      "related_region_ids": [
        "p4_chord_formula",
        "p4_tangent_diagram"
      ],
      "layer": "formulas",
      "grounding_note": "Long displayed limiting derivation visibly uses magnitude bars. Transcription is not independently verified.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p4_tangent_diagram",
      "page": 4,
      "bbox": {
        "x0": 0.348,
        "y0": 0.386,
        "x1": 0.654,
        "y1": 0.613
      },
      "type": "diagram",
      "label": "Figure 6.3: displacement approaches the tangent",
      "semantic_ids": [
        "tangent_velocity"
      ],
      "source_text_excerpt": "",
      "parent_region_id": null,
      "related_region_ids": [
        "p4_displacement_vectors",
        "p4_velocity_vector",
        "p4_basis_vectors"
      ],
      "layer": "structure",
      "grounding_note": "Central dashed circle includes radius vectors, colored displacement construction, a tangent line, and a polar-basis inset.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p4_displacement_vectors",
      "page": 4,
      "bbox": {
        "x0": 0.438,
        "y0": 0.446,
        "x1": 0.536,
        "y1": 0.468
      },
      "type": "vector",
      "label": "Displacement chords near the tangent",
      "semantic_ids": [
        "tangent_velocity"
      ],
      "source_text_excerpt": "",
      "parent_region_id": "p4_tangent_diagram",
      "related_region_ids": [
        "p4_velocity_vector"
      ],
      "layer": "vectors",
      "grounding_note": "Broad box encloses the overlapping red and cyan chord arrows near the top of the circle, rather than assigning tiny individual boxes.",
      "confidence": "medium",
      "excerpt_verified": false
    },
    {
      "region_id": "p4_velocity_vector",
      "page": 4,
      "bbox": {
        "x0": 0.48,
        "y0": 0.429,
        "x1": 0.542,
        "y1": 0.464
      },
      "type": "vector",
      "label": "Tangential velocity vector",
      "semantic_ids": [
        "tangent_velocity"
      ],
      "source_text_excerpt": "",
      "parent_region_id": "p4_tangent_diagram",
      "related_region_ids": [
        "p4_displacement_vectors",
        "p4_basis_vectors"
      ],
      "layer": "vectors",
      "grounding_note": "Purple arrow points up-left from the current position, with v⃗(t) above it.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p4_basis_vectors",
      "page": 4,
      "bbox": {
        "x0": 0.467,
        "y0": 0.387,
        "x1": 0.624,
        "y1": 0.43
      },
      "type": "vector",
      "label": "Radial and tangential unit-vector inset",
      "semantic_ids": [],
      "source_text_excerpt": "",
      "parent_region_id": "p4_tangent_diagram",
      "related_region_ids": [
        "p4_velocity_vector",
        "p4_acceleration_decomposition"
      ],
      "layer": "vectors",
      "grounding_note": "Two black arrows above the circle show r̂(t) and θ̂(t). No basis-derivative operation is shown here.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p4_acceleration_decomposition",
      "page": 4,
      "bbox": {
        "x0": 0.415,
        "y0": 0.871,
        "x1": 0.857,
        "y1": 0.896
      },
      "type": "formula",
      "label": "Acceleration resolved into polar components",
      "semantic_ids": [
        "acceleration_components"
      ],
      "source_text_excerpt": "a⃗ = a_r r̂(t) + a_θ θ̂(t). (6.3.1)",
      "parent_region_id": null,
      "related_region_ids": [
        "p6_example_acceleration"
      ],
      "layer": "formulas",
      "grounding_note": "Displayed equation at the bottom of the page introduces the two acceleration components.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p6_kinematics_example",
      "page": 6,
      "bbox": {
        "x0": 0.145,
        "y0": 0.234,
        "x1": 0.851,
        "y1": 0.736
      },
      "type": "example",
      "label": "Example 6.1: circular motion with a cubic angle function",
      "semantic_ids": [
        "acceleration_components"
      ],
      "source_text_excerpt": "Example 6.1 Circular Motion Kinematics",
      "parent_region_id": null,
      "related_region_ids": [
        "p6_example_velocity",
        "p6_example_acceleration",
        "p6_zero_centripetal"
      ],
      "layer": "structure",
      "grounding_note": "Complete worked example from its heading through the zero-centripetal-acceleration result.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p6_example_velocity",
      "page": 6,
      "bbox": {
        "x0": 0.346,
        "y0": 0.486,
        "x1": 0.656,
        "y1": 0.525
      },
      "type": "formula",
      "label": "Velocity for the cubic angle function",
      "semantic_ids": [
        "tangent_velocity"
      ],
      "source_text_excerpt": "v⃗(t) = R(dθ(t)/dt)θ̂(t) = R(3At² − B)θ̂(t).",
      "parent_region_id": "p6_kinematics_example",
      "related_region_ids": [
        "p6_example_acceleration"
      ],
      "layer": "formulas",
      "grounding_note": "Centered velocity formula in the worked solution.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p6_example_acceleration",
      "page": 6,
      "bbox": {
        "x0": 0.346,
        "y0": 0.574,
        "x1": 0.657,
        "y1": 0.654
      },
      "type": "formula",
      "label": "Tangential and radial acceleration in the worked example",
      "semantic_ids": [
        "acceleration_components"
      ],
      "source_text_excerpt": "a⃗(t) = R(d²θ(t)/dt²)θ̂(t) − R(dθ(t)/dt)²r̂(t) = R(6At)θ̂(t) − R(3At² − B)²r̂(t)",
      "parent_region_id": "p6_kinematics_example",
      "related_region_ids": [
        "p6_example_velocity",
        "p6_zero_centripetal"
      ],
      "layer": "formulas",
      "grounding_note": "Two-line displayed acceleration calculation separates tangential and radial terms.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p6_zero_centripetal",
      "page": 6,
      "bbox": {
        "x0": 0.381,
        "y0": 0.71,
        "x1": 0.622,
        "y1": 0.733
      },
      "type": "formula",
      "label": "Time when centripetal acceleration vanishes",
      "semantic_ids": [
        "acceleration_components"
      ],
      "source_text_excerpt": "3At₁² − B = 0 ⇒ t₁ = √(B/3A).",
      "parent_region_id": "p6_kinematics_example",
      "related_region_ids": [
        "p6_example_acceleration"
      ],
      "layer": "formulas",
      "grounding_note": "Final centered equation of the example sets the angular rate to zero.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p6_uniform_condition",
      "page": 6,
      "bbox": {
        "x0": 0.145,
        "y0": 0.813,
        "x1": 0.857,
        "y1": 0.857
      },
      "type": "definition",
      "label": "Zero tangential force implies zero tangential acceleration",
      "semantic_ids": [
        "uniform_motion"
      ],
      "source_text_excerpt": "If the object is constrained to move in a circle and the total tangential force acting on the object is zero, F_θᵗᵒᵗᵃˡ = 0, then (Newton’s Second Law), the tangential acceleration is zero,",
      "parent_region_id": null,
      "related_region_ids": [
        "p6_zero_tangential"
      ],
      "layer": "structure",
      "grounding_note": "Opening paragraph of section 6.4 below the worked example.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p6_zero_tangential",
      "page": 6,
      "bbox": {
        "x0": 0.468,
        "y0": 0.875,
        "x1": 0.856,
        "y1": 0.897
      },
      "type": "formula",
      "label": "Vanishing tangential acceleration",
      "semantic_ids": [
        "uniform_motion"
      ],
      "source_text_excerpt": "a_θ = 0. (6.4.1)",
      "parent_region_id": null,
      "related_region_ids": [
        "p6_uniform_condition"
      ],
      "layer": "formulas",
      "grounding_note": "Bottom displayed equation states the uniform-motion tangential condition.",
      "confidence": "high",
      "excerpt_verified": false
    }
  ],
  "diagnostics": [
    "regions[13].plain_text",
    "regions[14].plain_text"
  ]
}
```

Browser observations: {"success": true, "source_selected": {"region_id": "p4_acceleration_decomposition", "focus": "acceleration_components"}, "focus_preserved": true, "source_view_unchanged": true, "canonical_value_changed": true, "linked_chart_changed": true, "post_compilation_response_attempts": 0, "post_compilation_network_delta": 0, "error": null}

Stability raw/normalized comparison:

```json
{
  "material_id": "circular",
  "accepted": [
    true,
    false,
    false
  ],
  "identical_complete_request_sha256": "adf53525fe6c9d8bafd26a26a6ebf9db847212fa16dc8115809cc55988e0d955",
  "raw_contract_declarations": [
    {
      "version": "1.1",
      "preferred": "dynamic",
      "focus_ids": [
        "position_basis",
        "basis_derivatives",
        "tangent_velocity",
        "acceleration_components",
        "uniform_motion",
        "orbit_measures"
      ],
      "source_pages": [
        1,
        2,
        4,
        5,
        6,
        7,
        8
      ],
      "features": {
        "equations": true,
        "continuous_parameters": true,
        "time_dynamics": true,
        "spatial_relations": true,
        "finite_outcomes": false,
        "set_relations": false,
        "ordered_collection": false,
        "transitions": false,
        "analogy_suitable": false,
        "structure": true,
        "interaction_value": true
      },
      "process": {
        "collections": [],
        "states": [],
        "transitions": [],
        "annotations": []
      },
      "execution": null
    },
    {
      "version": "1.1",
      "preferred": "dynamic",
      "focus_ids": [
        "position_basis",
        "basis_derivatives",
        "tangent_velocity",
        "acceleration_components",
        "uniform_motion",
        "orbit_measures"
      ],
      "source_pages": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8
      ],
      "features": {
        "equations": true,
        "continuous_parameters": true,
        "time_dynamics": true,
        "spatial_relations": true,
        "finite_outcomes": false,
        "set_relations": false,
        "ordered_collection": false,
        "transitions": false,
        "analogy_suitable": false,
        "structure": true,
        "interaction_value": true
      },
      "process": {
        "collections": [],
        "states": [],
        "transitions": [],
        "annotations": []
      },
      "execution": null
    },
    {
      "version": "1.1",
      "preferred": "dynamic",
      "focus_ids": [
        "position_basis",
        "basis_derivatives",
        "tangent_velocity",
        "acceleration_components",
        "uniform_motion",
        "orbit_measures"
      ],
      "source_pages": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8
      ],
      "features": {
        "equations": true,
        "continuous_parameters": true,
        "time_dynamics": true,
        "spatial_relations": true,
        "finite_outcomes": false,
        "set_relations": false,
        "ordered_collection": false,
        "transitions": false,
        "analogy_suitable": false,
        "structure": true,
        "interaction_value": true
      },
      "process": {
        "collections": [],
        "states": [],
        "transitions": [],
        "annotations": []
      },
      "execution": null
    }
  ],
  "raw_contract_differences": {
    "version": false,
    "preferred": false,
    "focus_ids": false,
    "source_pages": true,
    "features": false,
    "process": false,
    "execution": false
  },
  "normalized_differences": {
    "bindings": false,
    "domain_constraints": false,
    "duration_policy": false,
    "fixed_adjustable": false,
    "inverse_bindings": false,
    "parameter_ids": false,
    "quantities": false,
    "quantity_kinds": false,
    "ranges": false,
    "representation_structure": false,
    "source_pages": false,
    "validator_outcome": true
  },
  "not_measured": [
    "parameter generation",
    "quantity kinds",
    "domain constraints",
    "fixed/adjustable generation",
    "ranges",
    "quantities",
    "bindings",
    "inverse bindings",
    "duration policy"
  ],
  "limitation": "No spatial/probability compiler was selected. Native Lab declarations remain in the fixed main analysis; empty planner fields are not evidence of parameter-generation stability. With fewer than two accepted outputs, normalized stability cannot be established.",
  "A": "HUMAN_REVIEW_PENDING"
}
```

**Human A verdict: PENDING.**

## harmonic

The Lab varies stiffness, mass, initial_position and initial_velocity. It renders an analytic position curve, with no compiled spatial object or direct handle. The frozen prospective list names mass/stiffness/amplitude/phase; initial conditions in the actual declaration require review against the general solution on original pp.8–9. time is the Lab x variable, not a parameter.

Original planner declaration (including rejected declarations):

```json
{
  "version": "1.1",
  "focus_ids": [
    "restoring_force",
    "motion_equation",
    "verify_sinusoid",
    "combine_solutions",
    "apply_initial_conditions",
    "amplitude_phase"
  ],
  "source_pages": [
    2,
    3,
    4,
    5,
    6,
    7,
    8
  ],
  "features": {
    "equations": true,
    "continuous_parameters": true,
    "time_dynamics": true,
    "spatial_relations": true,
    "finite_outcomes": false,
    "set_relations": false,
    "ordered_collection": false,
    "transitions": false,
    "analogy_suitable": false,
    "structure": true,
    "interaction_value": true
  },
  "preferred": "dynamic",
  "reason": "Use the ready numeric lab to compare position curves for a frictionless, one-dimensional spring–mass system. Vary positive k and m and initial conditions x₀ and vₓ,₀ using ω₀ = √(k/m) and x(t) = x₀ cos(ω₀t) + (vₓ,₀/ω₀) sin(ω₀t). Parameter comparison reveals how k/m controls the period while initial conditions determine amplitude and phase. Connect the curves to Fₓ = −kx, x″ = −(k/m)x, and the sine",
  "process": {
    "collections": [],
    "states": [],
    "transitions": [],
    "annotations": []
  },
  "execution": null
}
```

Deep source-to-runtime objective observation:

```json
{
  "material_id": "harmonic",
  "A": "HUMAN_REVIEW_PENDING",
  "B": "PASS",
  "browser_status": "PENDING_REAL_BROWSER",
  "browser_errors": "NOT_EVALUATED",
  "context_jumps": "NOT_EVALUATED",
  "direct_manipulation": {
    "available": false,
    "targets": [],
    "absence_is_not_automatic_failure": true
  },
  "post_compilation_api_delta": 0,
  "atlas_status": "accepted",
  "regions": 22,
  "atlas_diagnostics": [],
  "selected_region": "p2_restoring_force_statement",
  "selected_semantic_id": "restoring_force",
  "semantic_identity_continuity": true,
  "source_grounding": "Validated Atlas link; semantic support/location needs human review",
  "target_ownership": true,
  "linked_support": {
    "semantic_id": "restoring_force",
    "source_region_ids": [
      "p3_force_diagram",
      "p3_force_vector",
      "p3_displacement_arrow",
      "p3_force_formula",
      "p3_newton_formula",
      "p2_spring_diagram",
      "p2_restoring_force_statement"
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
        "region_id": "p3_newton_formula",
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
        "region_id": "p2_restoring_force_statement",
        "page": 2,
        "kind": "estimated_region",
        "confidence": "high"
      }
    ],
    "representation_ids": [],
    "manipulation_target_ids": [],
    "formal_parameter_ids": [],
    "manipulable": false,
    "reason_not_manipulable": "No validated direct manipulation is available; use the formal view and existing controls."
  },
  "interaction": "existing Numeric Lab canonical slider callbacks",
  "commit_accepted": true,
  "linked_projection": [
    {
      "demo_id": "spring_initial_conditions",
      "parameter_id": "stiffness",
      "canonical_value": 10.0,
      "baseline": 4.0,
      "curve_changed": true,
      "stale_callback_rejected": true,
      "comparison_rows": [
        {
          "id": "stiffness",
          "label": "Spring constant k",
          "unit": "N/m",
          "baseline": 4.0,
          "current": 10.0,
          "delta": 6.0,
          "generated_range": true
        }
      ]
    }
  ],
  "baseline_current_separation": "Compiled defaults retained; callback updates existing Lab store only",
  "atomic_rejection": "Stale callback rejection tested; arbitrary out-of-range callback injection not claimed",
  "source_roundtrip": {
    "focus_preserved": true,
    "supporting_region": "p2_restoring_force_statement",
    "selected_source_context_preserved": true
  },
  "source_immutable": true
}
```

Actual generated Source Atlas regions (estimated boxes/transcriptions, requiring human location/semantic review):

```json
{
  "atlas_version": "1.0",
  "processed_pages": [
    1,
    2,
    3
  ],
  "regions": [
    {
      "region_id": "p3_force_diagram",
      "page": 3,
      "bbox": {
        "x0": 0.373,
        "y0": 0.094,
        "x1": 0.636,
        "y1": 0.191
      },
      "type": "diagram",
      "label": "Free-body diagram and restoring-force expression",
      "semantic_ids": [
        "restoring_force"
      ],
      "source_text_excerpt": "",
      "parent_region_id": null,
      "related_region_ids": [
        "p3_force_vector",
        "p3_displacement_arrow",
        "p3_force_formula"
      ],
      "layer": "structure",
      "grounding_note": "Figure 23.3 shows a block, a leftward spring force, a rightward displacement indicator, and a vector equation beneath.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p3_force_vector",
      "page": 3,
      "bbox": {
        "x0": 0.506,
        "y0": 0.105,
        "x1": 0.569,
        "y1": 0.128
      },
      "type": "vector",
      "label": "Leftward spring-force vector",
      "semantic_ids": [
        "restoring_force"
      ],
      "source_text_excerpt": "Fₛ",
      "parent_region_id": "p3_force_diagram",
      "related_region_ids": [
        "p3_displacement_arrow",
        "p3_force_formula"
      ],
      "layer": "vectors",
      "grounding_note": "The force arrow points left from beside the displaced block; its force label is included.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p3_displacement_arrow",
      "page": 3,
      "bbox": {
        "x0": 0.51,
        "y0": 0.135,
        "x1": 0.614,
        "y1": 0.158
      },
      "type": "arrow",
      "label": "Rightward displacement from equilibrium",
      "semantic_ids": [
        "restoring_force"
      ],
      "source_text_excerpt": "x(t)",
      "parent_region_id": "p3_force_diagram",
      "related_region_ids": [
        "p3_force_vector"
      ],
      "layer": "vectors",
      "grounding_note": "A horizontal arrow below the surface extends rightward from an origin marker and is labeled x(t).",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p3_force_formula",
      "page": 3,
      "bbox": {
        "x0": 0.411,
        "y0": 0.162,
        "x1": 0.601,
        "y1": 0.191
      },
      "type": "formula",
      "label": "Vector restoring-force law",
      "semantic_ids": [
        "restoring_force"
      ],
      "source_text_excerpt": "F⃗ₛ = −Fₛ î = −kx î",
      "parent_region_id": "p3_force_diagram",
      "related_region_ids": [
        "p3_newton_formula"
      ],
      "layer": "formulas",
      "grounding_note": "The displayed vector equation sits directly beneath the free-body diagram. Transcription is not independently verified.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p3_newton_formula",
      "page": 3,
      "bbox": {
        "x0": 0.44,
        "y0": 0.281,
        "x1": 0.858,
        "y1": 0.324
      },
      "type": "formula",
      "label": "Newton's second law for the spring–mass system",
      "semantic_ids": [
        "motion_equation",
        "restoring_force"
      ],
      "source_text_excerpt": "−kx = m d²x/dt². (23.2.1)",
      "parent_region_id": null,
      "related_region_ids": [
        "p3_force_formula",
        "p3_sho_formula"
      ],
      "layer": "formulas",
      "grounding_note": "The centered equation below the Newton's-law introduction equates spring force to mass times acceleration.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p3_sho_formula",
      "page": 3,
      "bbox": {
        "x0": 0.442,
        "y0": 0.428,
        "x1": 0.858,
        "y1": 0.471
      },
      "type": "formula",
      "label": "Simple harmonic oscillator differential equation",
      "semantic_ids": [
        "motion_equation"
      ],
      "source_text_excerpt": "d²x/dt² = −(k/m)x. (23.2.2)",
      "parent_region_id": null,
      "related_region_ids": [
        "p3_newton_formula",
        "p3_cosine_trial"
      ],
      "layer": "formulas",
      "grounding_note": "The second displayed equation isolates the second time derivative of position.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p3_cosine_trial",
      "page": 3,
      "bbox": {
        "x0": 0.351,
        "y0": 0.683,
        "x1": 0.858,
        "y1": 0.706
      },
      "type": "formula",
      "label": "Cosine trial solution with undetermined angular frequency",
      "semantic_ids": [
        "verify_sinusoid"
      ],
      "source_text_excerpt": "x(t) = A cos((2π/T)t) = A cos(ω₀t), (23.2.3)",
      "parent_region_id": null,
      "related_region_ids": [
        "p3_sho_formula"
      ],
      "layer": "formulas",
      "grounding_note": "The lower displayed equation proposes a cosine solution. This page does not yet display ω₀ = √(k/m).",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p1_sine_formula",
      "page": 1,
      "bbox": {
        "x0": 0.415,
        "y0": 0.159,
        "x1": 0.858,
        "y1": 0.181
      },
      "type": "formula",
      "label": "Sinusoidal function with amplitude and period",
      "semantic_ids": [],
      "source_text_excerpt": "y(t) = A sin(2πt/T) (23.1.1)",
      "parent_region_id": null,
      "related_region_ids": [
        "p1_time_graph",
        "p1_periodicity_formula"
      ],
      "layer": "formulas",
      "grounding_note": "The first displayed equation appears above the graph. No supplied semantic ID directly describes this page's formula.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p1_time_graph",
      "page": 1,
      "bbox": {
        "x0": 0.249,
        "y0": 0.282,
        "x1": 0.751,
        "y1": 0.506
      },
      "type": "graph_region",
      "label": "Sinusoidal time graph",
      "semantic_ids": [],
      "source_text_excerpt": "",
      "parent_region_id": null,
      "related_region_ids": [
        "p1_sine_curve",
        "p1_period_arrow",
        "p1_positive_amplitude",
        "p1_negative_amplitude"
      ],
      "layer": "structure",
      "grounding_note": "Figure 23.1 contains a sinusoidal curve, time and position axes, amplitude markings, and a repeat-interval arrow.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p1_sine_curve",
      "page": 1,
      "bbox": {
        "x0": 0.251,
        "y0": 0.3,
        "x1": 0.749,
        "y1": 0.491
      },
      "type": "curve",
      "label": "Repeating sine-wave trace",
      "semantic_ids": [],
      "source_text_excerpt": "",
      "parent_region_id": "p1_time_graph",
      "related_region_ids": [
        "p1_sine_formula",
        "p1_period_arrow"
      ],
      "layer": "structure",
      "grounding_note": "This bounding region encloses the oscillating trace across the graph, not an isolated mask of the curve.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p1_period_arrow",
      "page": 1,
      "bbox": {
        "x0": 0.497,
        "y0": 0.283,
        "x1": 0.664,
        "y1": 0.302
      },
      "type": "arrow",
      "label": "Horizontal period interval T",
      "semantic_ids": [],
      "source_text_excerpt": "T",
      "parent_region_id": "p1_time_graph",
      "related_region_ids": [
        "p1_periodicity_formula",
        "p1_frequency_formula"
      ],
      "layer": "vectors",
      "grounding_note": "The double-ended horizontal arrow above the waveform marks one repeat interval.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p1_positive_amplitude",
      "page": 1,
      "bbox": {
        "x0": 0.457,
        "y0": 0.294,
        "x1": 0.492,
        "y1": 0.313
      },
      "type": "label",
      "label": "Positive amplitude level",
      "semantic_ids": [],
      "source_text_excerpt": "+A",
      "parent_region_id": "p1_time_graph",
      "related_region_ids": [
        "p1_negative_amplitude"
      ],
      "layer": "labels",
      "grounding_note": "The +A label is visible immediately left of the vertical axis at the upper extremum level.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p1_negative_amplitude",
      "page": 1,
      "bbox": {
        "x0": 0.459,
        "y0": 0.477,
        "x1": 0.494,
        "y1": 0.496
      },
      "type": "label",
      "label": "Negative amplitude level",
      "semantic_ids": [],
      "source_text_excerpt": "−A",
      "parent_region_id": "p1_time_graph",
      "related_region_ids": [
        "p1_positive_amplitude"
      ],
      "layer": "labels",
      "grounding_note": "The −A label is visible immediately left of the vertical axis at the lower extremum level.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p1_periodicity_formula",
      "page": 1,
      "bbox": {
        "x0": 0.225,
        "y0": 0.622,
        "x1": 0.858,
        "y1": 0.668
      },
      "type": "formula",
      "label": "Periodicity identity",
      "semantic_ids": [],
      "source_text_excerpt": "y(t + T) = A sin[(2π/T)(t + T)] = A sin[(2π/T)t + 2π] = A sin[(2π/T)t] = y(t).",
      "parent_region_id": null,
      "related_region_ids": [
        "p1_sine_formula",
        "p1_period_arrow"
      ],
      "layer": "formulas",
      "grounding_note": "The wide displayed equation below the graph demonstrates invariance after a time shift T. Transcription is not independently verified.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p1_frequency_formula",
      "page": 1,
      "bbox": {
        "x0": 0.46,
        "y0": 0.704,
        "x1": 0.858,
        "y1": 0.726
      },
      "type": "formula",
      "label": "Frequency as reciprocal period",
      "semantic_ids": [],
      "source_text_excerpt": "f ≡ 1/T. (23.1.3)",
      "parent_region_id": null,
      "related_region_ids": [
        "p1_period_arrow",
        "p1_angular_frequency_formula"
      ],
      "layer": "formulas",
      "grounding_note": "The short displayed frequency definition is located below the periodicity identity.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p1_angular_frequency_formula",
      "page": 1,
      "bbox": {
        "x0": 0.416,
        "y0": 0.791,
        "x1": 0.858,
        "y1": 0.815
      },
      "type": "formula",
      "label": "Angular frequency in terms of period and frequency",
      "semantic_ids": [],
      "source_text_excerpt": "ω₀ ≡ 2π/T = 2πf, (23.1.4)",
      "parent_region_id": null,
      "related_region_ids": [
        "p1_frequency_formula",
        "p2_equivalent_sinusoids"
      ],
      "layer": "formulas",
      "grounding_note": "The displayed angular-frequency definition appears near the bottom of the page; it is not the spring-specific frequency condition.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p2_equivalent_sinusoids",
      "page": 2,
      "bbox": {
        "x0": 0.303,
        "y0": 0.197,
        "x1": 0.858,
        "y1": 0.22
      },
      "type": "formula",
      "label": "Equivalent period, frequency, and angular-frequency forms",
      "semantic_ids": [],
      "source_text_excerpt": "y(t) = A sin(2πt/T) = A sin(2πft) = A sin(ω₀t). (23.1.5)",
      "parent_region_id": null,
      "related_region_ids": [
        "p1_sine_formula",
        "p1_angular_frequency_formula"
      ],
      "layer": "formulas",
      "grounding_note": "The displayed equation near the top of page 2 collects three equivalent sinusoidal expressions.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p2_spring_diagram",
      "page": 2,
      "bbox": {
        "x0": 0.313,
        "y0": 0.329,
        "x1": 0.576,
        "y1": 0.568
      },
      "type": "diagram",
      "label": "Spring–object system at equilibrium and stretched",
      "semantic_ids": [
        "restoring_force"
      ],
      "source_text_excerpt": "",
      "parent_region_id": null,
      "related_region_ids": [
        "p2_equilibrium_configuration",
        "p2_stretched_configuration",
        "p2_restoring_force_statement"
      ],
      "layer": "structure",
      "grounding_note": "Figure 23.2 contrasts equilibrium and extension, providing the displacement convention used by the restoring-force law.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p2_equilibrium_configuration",
      "page": 2,
      "bbox": {
        "x0": 0.314,
        "y0": 0.329,
        "x1": 0.575,
        "y1": 0.44
      },
      "type": "diagram",
      "label": "Equilibrium configuration with x = 0",
      "semantic_ids": [],
      "source_text_excerpt": "equilibrium position",
      "parent_region_id": "p2_spring_diagram",
      "related_region_ids": [
        "p2_stretched_configuration"
      ],
      "layer": "structure",
      "grounding_note": "The upper configuration shows the wall, spring, block, equilibrium-length arrow, origin label, and positive direction.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p2_stretched_configuration",
      "page": 2,
      "bbox": {
        "x0": 0.314,
        "y0": 0.455,
        "x1": 0.573,
        "y1": 0.568
      },
      "type": "diagram",
      "label": "Stretched configuration with positive displacement",
      "semantic_ids": [],
      "source_text_excerpt": "stretched position",
      "parent_region_id": "p2_spring_diagram",
      "related_region_ids": [
        "p2_equilibrium_configuration",
        "p2_displacement_arrow"
      ],
      "layer": "structure",
      "grounding_note": "The lower configuration shows a longer spring and the block to the right of the equilibrium origin.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p2_displacement_arrow",
      "page": 2,
      "bbox": {
        "x0": 0.439,
        "y0": 0.518,
        "x1": 0.543,
        "y1": 0.539
      },
      "type": "arrow",
      "label": "Displacement x(t) measured from equilibrium",
      "semantic_ids": [],
      "source_text_excerpt": "x(t)",
      "parent_region_id": "p2_stretched_configuration",
      "related_region_ids": [
        "p3_displacement_arrow"
      ],
      "layer": "vectors",
      "grounding_note": "The black rightward arrow beneath the stretched block begins at the equilibrium-position marker.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p2_restoring_force_statement",
      "page": 2,
      "bbox": {
        "x0": 0.146,
        "y0": 0.751,
        "x1": 0.783,
        "y1": 0.775
      },
      "type": "definition",
      "label": "Linear restoring-force statement",
      "semantic_ids": [
        "restoring_force"
      ],
      "source_text_excerpt": "force acting on the spring is a linear restoring force, Fₓ = −kx (Figure 23.3).",
      "parent_region_id": null,
      "related_region_ids": [
        "p2_spring_diagram",
        "p3_force_formula"
      ],
      "layer": "formulas",
      "grounding_note": "The lower paragraph contains the force law inline. The box deliberately includes the surrounding explanatory sentence.",
      "confidence": "high",
      "excerpt_verified": false
    }
  ],
  "diagnostics": []
}
```

Browser observations: {"success": true, "source_selected": {"region_id": "p2_restoring_force_statement", "focus": "restoring_force"}, "focus_preserved": true, "source_view_unchanged": true, "canonical_value_changed": true, "linked_chart_changed": true, "post_compilation_response_attempts": 0, "post_compilation_network_delta": 0, "error": null}

Stability raw/normalized comparison:

```json
{
  "material_id": "harmonic",
  "accepted": [
    false,
    false,
    false
  ],
  "identical_complete_request_sha256": "11d80613c08c79e0717be5de0dc9ed7b9c54d7e3d5e7aff4c177c344dcef4f60",
  "raw_contract_declarations": [
    {
      "version": "1.1",
      "preferred": "dynamic",
      "focus_ids": [
        "restoring_force",
        "motion_equation",
        "verify_sinusoid",
        "combine_solutions",
        "apply_initial_conditions",
        "amplitude_phase"
      ],
      "source_pages": [
        2,
        3,
        4,
        5,
        6,
        7,
        8
      ],
      "features": {
        "equations": true,
        "continuous_parameters": true,
        "time_dynamics": true,
        "spatial_relations": true,
        "finite_outcomes": false,
        "set_relations": false,
        "ordered_collection": false,
        "transitions": false,
        "analogy_suitable": false,
        "structure": true,
        "interaction_value": true
      },
      "process": {
        "collections": [],
        "states": [],
        "transitions": [],
        "annotations": []
      },
      "execution": null
    },
    {
      "version": "1.1",
      "preferred": "dynamic",
      "focus_ids": [
        "restoring_force",
        "motion_equation",
        "verify_sinusoid",
        "combine_solutions",
        "apply_initial_conditions",
        "amplitude_phase"
      ],
      "source_pages": [
        2,
        3,
        4,
        5,
        6,
        7,
        8
      ],
      "features": {
        "equations": true,
        "continuous_parameters": true,
        "time_dynamics": true,
        "spatial_relations": true,
        "finite_outcomes": false,
        "set_relations": false,
        "ordered_collection": false,
        "transitions": false,
        "analogy_suitable": false,
        "structure": true,
        "interaction_value": true
      },
      "process": {
        "collections": [],
        "states": [],
        "transitions": [],
        "annotations": []
      },
      "execution": null
    },
    {
      "version": "1.1",
      "preferred": "dynamic",
      "focus_ids": [
        "restoring_force",
        "motion_equation",
        "verify_sinusoid",
        "combine_solutions",
        "apply_initial_conditions",
        "amplitude_phase"
      ],
      "source_pages": [
        2,
        3,
        4,
        5,
        6,
        7,
        8
      ],
      "features": {
        "equations": true,
        "continuous_parameters": true,
        "time_dynamics": true,
        "spatial_relations": true,
        "finite_outcomes": false,
        "set_relations": false,
        "ordered_collection": false,
        "transitions": false,
        "analogy_suitable": false,
        "structure": true,
        "interaction_value": true
      },
      "process": {
        "collections": [],
        "states": [],
        "transitions": [],
        "annotations": []
      },
      "execution": null
    }
  ],
  "raw_contract_differences": {
    "version": false,
    "preferred": false,
    "focus_ids": false,
    "source_pages": false,
    "features": false,
    "process": false,
    "execution": false
  },
  "normalized_differences": {
    "validator_outcome": false
  },
  "not_measured": [
    "parameter generation",
    "quantity kinds",
    "domain constraints",
    "fixed/adjustable generation",
    "ranges",
    "quantities",
    "bindings",
    "inverse bindings",
    "duration policy"
  ],
  "limitation": "No spatial/probability compiler was selected. Native Lab declarations remain in the fixed main analysis; empty planner fields are not evidence of parameter-generation stability. With fewer than two accepted outputs, normalized stability cannot be established.",
  "A": "HUMAN_REVIEW_PENDING"
}
```

**Human A verdict: PENDING.**

## circuits

The main output contains a voltage-response Lab varying input_voltage, initial_voltage and the lumped time_constant; R and C are not separate controls. The first planner was rejected. time is the Lab x variable, not a parameter. The displayed example defaults and hypothetical explorations must be distinguished by the human reviewer.

Original planner declaration (including rejected declarations):

```json
{
  "version": "1.1",
  "focus_ids": [
    "form_equation",
    "find_particular",
    "find_homogeneous",
    "combine_solutions",
    "apply_initial",
    "complete_response"
  ],
  "source_pages": [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8
  ],
  "features": {
    "equations": true,
    "continuous_parameters": true,
    "time_dynamics": true,
    "spatial_relations": false,
    "finite_outcomes": false,
    "set_relations": false,
    "ordered_collection": false,
    "transitions": false,
    "analogy_suitable": false,
    "structure": true,
    "interaction_value": true
  },
  "preferred": "dynamic",
  "reason": "The ready numeric lab can compare curves for the source-supported response vC(t) = VI + (V0 − VI)e^(−t/RC), with R > 0, C > 0 and t ≥ 0. Varying VI and V0 reveals the final and initial voltages; varying R or C reveals how τ = RC controls the approach rate. Compare the source examples charging from 0 V toward 5 V and discharging from 5 V toward 0 V. Connect these curves to RC dvC/dt + vC = VI, theC",
  "process": {
    "collections": [],
    "states": [],
    "transitions": [],
    "annotations": []
  },
  "execution": null
}
```

Deep source-to-runtime objective observation:

```json
{
  "material_id": "circuits",
  "A": "HUMAN_REVIEW_PENDING",
  "B": "PASS",
  "browser_status": "PENDING_REAL_BROWSER",
  "browser_errors": "NOT_EVALUATED",
  "context_jumps": "NOT_EVALUATED",
  "direct_manipulation": {
    "available": false,
    "targets": [],
    "absence_is_not_automatic_failure": true
  },
  "post_compilation_api_delta": 0,
  "atlas_status": "accepted",
  "regions": 21,
  "atlas_diagnostics": [],
  "selected_region": "p1_circuit",
  "selected_semantic_id": "form_equation",
  "semantic_identity_continuity": true,
  "source_grounding": "Validated Atlas link; semantic support/location needs human review",
  "target_ownership": true,
  "linked_support": {
    "semantic_id": "form_equation",
    "source_region_ids": [
      "p1_circuit",
      "p1_thevenin_boundary",
      "p1_node_equation",
      "p1_rc_equation",
      "p1_initial_conditions",
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
        "region_id": "p1_thevenin_boundary",
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
        "region_id": "p1_initial_conditions",
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
    "representation_ids": [],
    "manipulation_target_ids": [],
    "formal_parameter_ids": [],
    "manipulable": false,
    "reason_not_manipulable": "No validated direct manipulation is available; use the formal view and existing controls."
  },
  "interaction": "existing Numeric Lab canonical slider callbacks",
  "commit_accepted": true,
  "linked_projection": [
    {
      "demo_id": "rc_voltage_response",
      "parameter_id": "input_voltage",
      "canonical_value": 3.0,
      "baseline": 5.0,
      "curve_changed": true,
      "stale_callback_rejected": true,
      "comparison_rows": [
        {
          "id": "input_voltage",
          "label": "Constant input VI",
          "unit": "V",
          "baseline": 5.0,
          "current": 3.0,
          "delta": -2.0,
          "generated_range": true
        }
      ]
    }
  ],
  "baseline_current_separation": "Compiled defaults retained; callback updates existing Lab store only",
  "atomic_rejection": "Stale callback rejection tested; arbitrary out-of-range callback injection not claimed",
  "source_roundtrip": {
    "focus_preserved": true,
    "supporting_region": "p1_circuit",
    "selected_source_context_preserved": true
  },
  "source_immutable": true
}
```

Actual generated Source Atlas regions (estimated boxes/transcriptions, requiring human location/semantic review):

```json
{
  "atlas_version": "1.0",
  "processed_pages": [
    1,
    6,
    8
  ],
  "regions": [
    {
      "region_id": "p1_circuit",
      "page": 1,
      "bbox": {
        "x0": 0.185,
        "y0": 0.185,
        "x1": 0.83,
        "y1": 0.385
      },
      "type": "diagram",
      "label": "RC circuit with input source and capacitor voltage polarity",
      "semantic_ids": [
        "form_equation"
      ],
      "source_text_excerpt": "v_I(t), R, C, v_C(t)",
      "parent_region_id": null,
      "related_region_ids": [
        "p1_node_equation"
      ],
      "layer": "structure",
      "grounding_note": "The circuit visibly contains a voltage source, series resistor, capacitor, ground, and marked output polarity.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p1_thevenin_boundary",
      "page": 1,
      "bbox": {
        "x0": 0.505,
        "y0": 0.13,
        "x1": 0.585,
        "y1": 0.405
      },
      "type": "annotation",
      "label": "Dashed Thévenin boundary with left-pointing arrow",
      "semantic_ids": [
        "form_equation"
      ],
      "source_text_excerpt": "",
      "parent_region_id": null,
      "related_region_ids": [
        "p1_circuit"
      ],
      "layer": "relationships",
      "grounding_note": "A vertical dashed line crosses the circuit, with a left-pointing arrow at its upper end.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p1_node_equation",
      "page": 1,
      "bbox": {
        "x0": 0.22,
        "y0": 0.545,
        "x1": 0.565,
        "y1": 0.63
      },
      "type": "formula",
      "label": "Node-current balance",
      "semantic_ids": [
        "form_equation"
      ],
      "source_text_excerpt": "(v_C − v_I)/R + C dv_C/dt = 0",
      "parent_region_id": null,
      "related_region_ids": [
        "p1_circuit",
        "p1_rc_equation"
      ],
      "layer": "formulas",
      "grounding_note": "The first displayed equation below the node-method heading expresses the current balance.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p1_rc_equation",
      "page": 1,
      "bbox": {
        "x0": 0.235,
        "y0": 0.654,
        "x1": 0.575,
        "y1": 0.736
      },
      "type": "formula",
      "label": "First-order RC voltage equation",
      "semantic_ids": [
        "form_equation"
      ],
      "source_text_excerpt": "RC dv_C/dt + v_C = v_I",
      "parent_region_id": null,
      "related_region_ids": [
        "p1_node_equation",
        "p1_initial_conditions",
        "p1_time_units"
      ],
      "layer": "formulas",
      "grounding_note": "The lower equation has its RC coefficient enclosed by a dashed circle.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p1_initial_conditions",
      "page": 1,
      "bbox": {
        "x0": 0.59,
        "y0": 0.647,
        "x1": 0.89,
        "y1": 0.746
      },
      "type": "annotation",
      "label": "Time domain and given initial capacitor voltage",
      "semantic_ids": [
        "form_equation"
      ],
      "source_text_excerpt": "t ≥ t_0; v_C(t_0) given",
      "parent_region_id": null,
      "related_region_ids": [
        "p1_rc_equation"
      ],
      "layer": "relationships",
      "grounding_note": "A brace to the right of the differential equation groups the time restriction and given initial voltage.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p1_time_units",
      "page": 1,
      "bbox": {
        "x0": 0.195,
        "y0": 0.652,
        "x1": 0.365,
        "y1": 0.867
      },
      "type": "annotation",
      "label": "RC has units of time",
      "semantic_ids": [
        "form_equation"
      ],
      "source_text_excerpt": "units of time",
      "parent_region_id": null,
      "related_region_ids": [
        "p1_rc_equation"
      ],
      "layer": "relationships",
      "grounding_note": "The upward arrow connects the units-of-time note to the circled RC coefficient.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p8_charging_graph",
      "page": 8,
      "bbox": {
        "x0": 0.03,
        "y0": 0.075,
        "x1": 0.465,
        "y1": 0.389
      },
      "type": "graph_region",
      "label": "Charging response from 0 V toward 5 V",
      "semantic_ids": [
        "complete_response"
      ],
      "source_text_excerpt": "v_C, 5V, 0V, t",
      "parent_region_id": null,
      "related_region_ids": [
        "p8_charging_curve",
        "p8_charging_formula",
        "p8_charging_input"
      ],
      "layer": "structure",
      "grounding_note": "The upper-left graph has voltage and time axes, a dashed 5 V level, and a rising green curve.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p8_charging_curve",
      "page": 8,
      "bbox": {
        "x0": 0.095,
        "y0": 0.161,
        "x1": 0.41,
        "y1": 0.376
      },
      "type": "curve",
      "label": "Rising exponential charging curve",
      "semantic_ids": [
        "complete_response"
      ],
      "source_text_excerpt": "",
      "parent_region_id": "p8_charging_graph",
      "related_region_ids": [
        "p8_charging_formula"
      ],
      "layer": "structure",
      "grounding_note": "The green curve begins at the origin and flattens near the dashed 5 V level; its box includes the curve's interior span.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p8_charging_formula",
      "page": 8,
      "bbox": {
        "x0": 0.23,
        "y0": 0.225,
        "x1": 0.39,
        "y1": 0.287
      },
      "type": "formula",
      "label": "Printed charging expression with a plus sign",
      "semantic_ids": [
        "complete_response"
      ],
      "source_text_excerpt": "5 + 5e^(−t/RC)",
      "parent_region_id": "p8_charging_graph",
      "related_region_ids": [
        "p8_charging_curve",
        "p8_charging_input"
      ],
      "layer": "formulas",
      "grounding_note": "The image visibly prints a plus sign. This expression is inconsistent with the adjacent curve and stated zero initial voltage; it is preserved rather than corrected.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p8_charging_input",
      "page": 8,
      "bbox": {
        "x0": 0.083,
        "y0": 0.415,
        "x1": 0.418,
        "y1": 0.507
      },
      "type": "annotation",
      "label": "Charging initial value and upward input step",
      "semantic_ids": [
        "complete_response"
      ],
      "source_text_excerpt": "V_0 = 0V; V_I = 5V",
      "parent_region_id": null,
      "related_region_ids": [
        "p8_charging_graph"
      ],
      "layer": "relationships",
      "grounding_note": "Below the charging graph, the initial and input voltages appear beside a step sketch rising from 0 to 5.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p8_discharging_graph",
      "page": 8,
      "bbox": {
        "x0": 0.517,
        "y0": 0.075,
        "x1": 0.952,
        "y1": 0.389
      },
      "type": "graph_region",
      "label": "Discharging response from 5 V toward 0 V",
      "semantic_ids": [
        "complete_response"
      ],
      "source_text_excerpt": "v_C, 5V, 0V, t",
      "parent_region_id": null,
      "related_region_ids": [
        "p8_discharging_curve",
        "p8_discharging_formula",
        "p8_discharging_input",
        "p8_time_constant"
      ],
      "layer": "structure",
      "grounding_note": "The upper-right graph shows a falling green response and a dashed initial tangent.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p8_discharging_curve",
      "page": 8,
      "bbox": {
        "x0": 0.584,
        "y0": 0.163,
        "x1": 0.908,
        "y1": 0.376
      },
      "type": "curve",
      "label": "Falling exponential discharge curve",
      "semantic_ids": [
        "complete_response"
      ],
      "source_text_excerpt": "",
      "parent_region_id": "p8_discharging_graph",
      "related_region_ids": [
        "p8_discharging_formula"
      ],
      "layer": "structure",
      "grounding_note": "The green curve starts at 5 V on the vertical axis and approaches the horizontal axis.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p8_discharging_formula",
      "page": 8,
      "bbox": {
        "x0": 0.706,
        "y0": 0.222,
        "x1": 0.806,
        "y1": 0.284
      },
      "type": "formula",
      "label": "Discharging exponential expression",
      "semantic_ids": [
        "complete_response"
      ],
      "source_text_excerpt": "5e^(−t/RC)",
      "parent_region_id": "p8_discharging_graph",
      "related_region_ids": [
        "p8_discharging_curve"
      ],
      "layer": "formulas",
      "grounding_note": "The expression is printed inside the right-hand graph above the falling curve.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p8_discharging_input",
      "page": 8,
      "bbox": {
        "x0": 0.582,
        "y0": 0.418,
        "x1": 0.941,
        "y1": 0.507
      },
      "type": "annotation",
      "label": "Discharging initial value and downward input step",
      "semantic_ids": [
        "complete_response"
      ],
      "source_text_excerpt": "V_0 = 5V; V_I = 0V",
      "parent_region_id": null,
      "related_region_ids": [
        "p8_discharging_graph"
      ],
      "layer": "relationships",
      "grounding_note": "Below the right graph, the initial and input voltages accompany a step sketch falling from 5 to 0.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p8_time_constant",
      "page": 8,
      "bbox": {
        "x0": 0.576,
        "y0": 0.166,
        "x1": 0.714,
        "y1": 0.584
      },
      "type": "annotation",
      "label": "Initial tangent and time-constant construction",
      "semantic_ids": [
        "complete_response"
      ],
      "source_text_excerpt": "τ = RC",
      "parent_region_id": null,
      "related_region_ids": [
        "p8_discharging_graph"
      ],
      "layer": "relationships",
      "grounding_note": "The broad box covers the dashed tangent, blue vertical guides, double-headed horizontal arrow, and τ = RC label.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p8_repeated_waveform",
      "page": 8,
      "bbox": {
        "x0": 0.345,
        "y0": 0.659,
        "x1": 0.903,
        "y1": 0.823
      },
      "type": "graph_region",
      "label": "Repeated exponential charging and discharging waveform",
      "semantic_ids": [
        "complete_response"
      ],
      "source_text_excerpt": "B",
      "parent_region_id": null,
      "related_region_ids": [
        "p8_charging_graph",
        "p8_discharging_graph"
      ],
      "layer": "structure",
      "grounding_note": "The lower green waveform alternates rising and falling segments between two dashed horizontal reference levels.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p6_solution_sum",
      "page": 6,
      "bbox": {
        "x0": 0.312,
        "y0": 0.121,
        "x1": 0.568,
        "y1": 0.159
      },
      "type": "formula",
      "label": "Sum of particular and homogeneous solutions",
      "semantic_ids": [
        "combine_solutions"
      ],
      "source_text_excerpt": "v_C = v_CP + v_CH",
      "parent_region_id": null,
      "related_region_ids": [
        "p6_general_solution"
      ],
      "layer": "formulas",
      "grounding_note": "The first equation beneath the total-solution heading adds the two solution components.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p6_general_solution",
      "page": 6,
      "bbox": {
        "x0": 0.313,
        "y0": 0.173,
        "x1": 0.589,
        "y1": 0.241
      },
      "type": "formula",
      "label": "Constant-input solution with unknown amplitude",
      "semantic_ids": [
        "combine_solutions"
      ],
      "source_text_excerpt": "v_C = V_I + Ae^(−t/RC)",
      "parent_region_id": null,
      "related_region_ids": [
        "p6_solution_sum",
        "p6_initial_derivation"
      ],
      "layer": "formulas",
      "grounding_note": "The second equation explicitly substitutes the constant particular solution and exponential homogeneous term.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p6_initial_derivation",
      "page": 6,
      "bbox": {
        "x0": 0.14,
        "y0": 0.387,
        "x1": 0.675,
        "y1": 0.572
      },
      "type": "process_step",
      "label": "Initial condition determines the transient amplitude",
      "semantic_ids": [
        "apply_initial"
      ],
      "source_text_excerpt": "Given, v_C = V_0 at t = 0; so, V_0 = V_I + A; or A = V_0 − V_I",
      "parent_region_id": null,
      "related_region_ids": [
        "p6_general_solution",
        "p6_complete_voltage"
      ],
      "layer": "formulas",
      "grounding_note": "Three vertically arranged lines apply the initial voltage and solve for A.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p6_complete_voltage",
      "page": 6,
      "bbox": {
        "x0": 0.314,
        "y0": 0.601,
        "x1": 0.742,
        "y1": 0.685
      },
      "type": "formula",
      "label": "Highlighted complete capacitor-voltage response",
      "semantic_ids": [
        "complete_response"
      ],
      "source_text_excerpt": "v_C = V_I + (V_0 − V_I)e^(−t/RC)",
      "parent_region_id": null,
      "related_region_ids": [
        "p6_initial_derivation",
        "p6_capacitor_current"
      ],
      "layer": "formulas",
      "grounding_note": "The complete voltage expression is visibly emphasized by a gray rectangular background.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p6_capacitor_current",
      "page": 6,
      "bbox": {
        "x0": 0.335,
        "y0": 0.718,
        "x1": 0.827,
        "y1": 0.802
      },
      "type": "formula",
      "label": "Capacitor current derived from the voltage response",
      "semantic_ids": [
        "complete_response"
      ],
      "source_text_excerpt": "i_C = C dv_C/dt = −((V_0 − V_I)/R)e^(−t/RC)",
      "parent_region_id": null,
      "related_region_ids": [
        "p6_complete_voltage"
      ],
      "layer": "formulas",
      "grounding_note": "The bottom equation gives the derivative-based capacitor current and its exponential expression.",
      "confidence": "high",
      "excerpt_verified": false
    }
  ],
  "diagnostics": []
}
```

Browser observations: {"success": true, "source_selected": {"region_id": "p1_circuit", "focus": "form_equation"}, "focus_preserved": true, "source_view_unchanged": true, "canonical_value_changed": true, "linked_chart_changed": true, "post_compilation_response_attempts": 0, "post_compilation_network_delta": 0, "error": null}

Stability raw/normalized comparison:

```json
{
  "material_id": "circuits",
  "accepted": [
    true,
    true,
    true
  ],
  "identical_complete_request_sha256": "8d42c4de0db2d9f3cd430654b422559760d7589bd780e0e88ca2d6fbe0ec398f",
  "raw_contract_declarations": [
    {
      "version": "1.1",
      "preferred": "dynamic",
      "focus_ids": [
        "form_equation",
        "find_particular",
        "find_homogeneous",
        "combine_solutions",
        "apply_initial",
        "complete_response"
      ],
      "source_pages": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8
      ],
      "features": {
        "equations": true,
        "continuous_parameters": true,
        "time_dynamics": true,
        "spatial_relations": false,
        "finite_outcomes": false,
        "set_relations": false,
        "ordered_collection": false,
        "transitions": false,
        "analogy_suitable": false,
        "structure": true,
        "interaction_value": true
      },
      "process": {
        "collections": [],
        "states": [],
        "transitions": [],
        "annotations": []
      },
      "execution": null
    },
    {
      "version": "1.1",
      "preferred": "dynamic",
      "focus_ids": [
        "form_equation",
        "find_particular",
        "find_homogeneous",
        "combine_solutions",
        "apply_initial",
        "complete_response"
      ],
      "source_pages": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8
      ],
      "features": {
        "equations": true,
        "continuous_parameters": true,
        "time_dynamics": true,
        "spatial_relations": false,
        "finite_outcomes": false,
        "set_relations": false,
        "ordered_collection": false,
        "transitions": false,
        "analogy_suitable": false,
        "structure": true,
        "interaction_value": true
      },
      "process": {
        "collections": [],
        "states": [],
        "transitions": [],
        "annotations": []
      },
      "execution": null
    },
    {
      "version": "1.1",
      "preferred": "dynamic",
      "focus_ids": [
        "form_equation",
        "find_particular",
        "find_homogeneous",
        "combine_solutions",
        "apply_initial",
        "complete_response"
      ],
      "source_pages": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8
      ],
      "features": {
        "equations": true,
        "continuous_parameters": true,
        "time_dynamics": true,
        "spatial_relations": false,
        "finite_outcomes": false,
        "set_relations": false,
        "ordered_collection": false,
        "transitions": false,
        "analogy_suitable": false,
        "structure": true,
        "interaction_value": true
      },
      "process": {
        "collections": [],
        "states": [],
        "transitions": [],
        "annotations": []
      },
      "execution": null
    }
  ],
  "raw_contract_differences": {
    "version": false,
    "preferred": false,
    "focus_ids": false,
    "source_pages": false,
    "features": false,
    "process": false,
    "execution": false
  },
  "normalized_differences": {
    "bindings": false,
    "domain_constraints": false,
    "duration_policy": false,
    "fixed_adjustable": false,
    "inverse_bindings": false,
    "parameter_ids": false,
    "quantities": false,
    "quantity_kinds": false,
    "ranges": false,
    "representation_structure": false,
    "source_pages": false,
    "validator_outcome": false
  },
  "not_measured": [
    "parameter generation",
    "quantity kinds",
    "domain constraints",
    "fixed/adjustable generation",
    "ranges",
    "quantities",
    "bindings",
    "inverse bindings",
    "duration policy"
  ],
  "limitation": "No spatial/probability compiler was selected. Native Lab declarations remain in the fixed main analysis; empty planner fields are not evidence of parameter-generation stability. With fewer than two accepted outputs, normalized stability cannot be established.",
  "A": "HUMAN_REVIEW_PENDING"
}
```

**Human A verdict: PENDING.**

## signals

The Lab holds component frequencies at 440 and 880 Hz in expressions and varies amplitudes and a sine phase. It does not resynthesize the recorded bell/violin data. The additional phase control needs source-support review as an explicitly hypothetical exploration.

Original planner declaration (including rejected declarations):

```json
{
  "version": "1.1",
  "focus_ids": [
    "time_signal",
    "apply_dft",
    "component_spectrum",
    "sum_components",
    "reconstructed_signal"
  ],
  "source_pages": [
    1,
    2,
    3,
    4,
    5
  ],
  "features": {
    "equations": true,
    "continuous_parameters": true,
    "time_dynamics": true,
    "spatial_relations": false,
    "finite_outcomes": false,
    "set_relations": false,
    "ordered_collection": false,
    "transitions": true,
    "analogy_suitable": false,
    "structure": true,
    "interaction_value": true
  },
  "preferred": "dynamic",
  "reason": "The source defines sine and cosine signals through frequency, amplitude, and phase offset, and explains their addition. The ready numeric lab can compare component curves and their summed waveform while learners vary these continuous parameters, starting with the supplied 440 Hz cosine and 880 Hz sine example. This makes the relationship between components and waveform shape directly observable; a",
  "process": {
    "collections": [],
    "states": [],
    "transitions": [],
    "annotations": []
  },
  "execution": null
}
```

**Human A verdict: PENDING.**

## regression

corr is adjustable from -0.6 to 0.6, with the observed correlation -0.499 as its default. The expression consequently changes the fitted slope while sample means and standard deviations are numeric constants. Frozen expectations permit prediction input variation and preserve the sample statistic/fitted result; they do not preauthorize an adjustable trial fit.

Original planner declaration (including rejected declarations):

```json
{
  "version": "1.1",
  "focus_ids": [
    "summary_stats",
    "compute_slope",
    "anchor_line",
    "fitted_equation",
    "interpret_model"
  ],
  "source_pages": [
    4,
    5,
    6
  ],
  "features": {
    "equations": true,
    "continuous_parameters": true,
    "time_dynamics": false,
    "spatial_relations": true,
    "finite_outcomes": false,
    "set_relations": false,
    "ordered_collection": true,
    "transitions": false,
    "analogy_suitable": false,
    "structure": true,
    "interaction_value": true
  },
  "preferred": "dynamic",
  "reason": "The ready numeric lab can connect the ordered derivation to meaningful parameter exploration: b₁ = (sᵧ/sₓ)R, b₀ = ȳ − b₁x̄, and ŷ = b₀ + b₁x. Comparing valid summary-statistic inputs shows how correlation and the standard-deviation ratio change the slope while the fitted line remains anchored at (x̄, ȳ). This makes the slope, intercept, and predictions easier to interpret without requiring time or",
  "process": {
    "collections": [],
    "states": [],
    "transitions": [],
    "annotations": []
  },
  "execution": null
}
```

**Human A verdict: PENDING.**

## probability

The selected family is dynamic Numeric Lab, not probability_sets. prob_a and prob_b vary between 0.25 and 0.5; overlap is the plotted x variable. No shared finite-outcome/event-membership declaration, exact set runtime or Monte Carlo scene was compiled. Compare the hypothetical probability sliders with frozen source event memberships and outcome weights.

Original planner declaration (including rejected declarations):

```json
{
  "version": "1.1",
  "focus_ids": [
    "event_probability",
    "sample_space",
    "events",
    "disjoint",
    "intersection",
    "union_rule",
    "disjoint_rule",
    "distribution",
    "complement"
  ],
  "source_pages": [
    1,
    2,
    4,
    5,
    6,
    7,
    8
  ],
  "features": {
    "equations": true,
    "continuous_parameters": true,
    "time_dynamics": false,
    "spatial_relations": false,
    "finite_outcomes": true,
    "set_relations": true,
    "ordered_collection": true,
    "transitions": false,
    "analogy_suitable": false,
    "structure": true,
    "interaction_value": true
  },
  "preferred": "dynamic",
  "reason": "Use the ready numeric lab to compare valid probability parameters in P(A ∪ B) = P(A) + P(B) − P(A ∩ B) and P(Aᶜ) = 1 − P(A). Varying overlap reveals why simple addition double-counts shared outcomes and why disjoint events are the zero-overlap case. Keep comparisons within valid probability constraints and connect them to the source's die and card examples. Distribution probabilities must remain e",
  "process": {
    "collections": [],
    "states": [],
    "transitions": [],
    "annotations": []
  },
  "execution": null
}
```

Deep source-to-runtime objective observation:

```json
{
  "material_id": "probability",
  "A": "HUMAN_REVIEW_PENDING",
  "B": "PASS",
  "browser_status": "PENDING_REAL_BROWSER",
  "browser_errors": "NOT_EVALUATED",
  "context_jumps": "NOT_EVALUATED",
  "direct_manipulation": {
    "available": false,
    "targets": [],
    "absence_is_not_automatic_failure": true
  },
  "post_compilation_api_delta": 0,
  "atlas_status": "accepted",
  "regions": 19,
  "atlas_diagnostics": [],
  "selected_region": "p5_addition_rule",
  "selected_semantic_id": "union_rule",
  "semantic_identity_continuity": true,
  "source_grounding": "Validated Atlas link; semantic support/location needs human review",
  "target_ownership": true,
  "linked_support": {
    "semantic_id": "union_rule",
    "source_region_ids": [
      "p5_card_formula",
      "p5_addition_rule",
      "p5_addition_formula",
      "p5_inclusive_or",
      "p5_loan_diagram"
    ],
    "source_pages": [
      5
    ],
    "support": [
      {
        "region_id": "p5_card_formula",
        "page": 5,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p5_addition_rule",
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
        "region_id": "p5_inclusive_or",
        "page": 5,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p5_loan_diagram",
        "page": 5,
        "kind": "estimated_region",
        "confidence": "medium"
      }
    ],
    "representation_ids": [],
    "manipulation_target_ids": [],
    "formal_parameter_ids": [],
    "manipulable": false,
    "reason_not_manipulable": "No validated direct manipulation is available; use the formal view and existing controls."
  },
  "interaction": "existing Numeric Lab canonical slider callbacks",
  "commit_accepted": true,
  "linked_projection": [
    {
      "demo_id": "overlap_lab",
      "parameter_id": "prob_a",
      "canonical_value": 0.4,
      "baseline": 0.3333333333333333,
      "curve_changed": true,
      "stale_callback_rejected": true,
      "comparison_rows": [
        {
          "id": "prob_a",
          "label": "p_A = P(A)",
          "unit": "probability",
          "baseline": 0.3333333333333333,
          "current": 0.4,
          "delta": 0.06666666666666671,
          "generated_range": true
        }
      ]
    }
  ],
  "baseline_current_separation": "Compiled defaults retained; callback updates existing Lab store only",
  "atomic_rejection": "Stale callback rejection tested; arbitrary out-of-range callback injection not claimed",
  "source_roundtrip": {
    "focus_preserved": true,
    "supporting_region": "p5_addition_rule",
    "selected_source_context_preserved": true
  },
  "source_immutable": true
}
```

Actual generated Source Atlas regions (estimated boxes/transcriptions, requiring human location/semantic review):

```json
{
  "atlas_version": "1.0",
  "processed_pages": [
    5,
    6,
    8
  ],
  "regions": [
    {
      "region_id": "p5_card_formula",
      "page": 5,
      "bbox": {
        "x0": 0.295,
        "y0": 0.109,
        "x1": 0.706,
        "y1": 0.182
      },
      "type": "formula",
      "label": "Card probability calculation correcting double counting",
      "semantic_ids": [
        "union_rule",
        "intersection"
      ],
      "source_text_excerpt": "P(A or B) = P(♦ or face card)\n= P(♦) + P(face card) − P(♦ and face card)\n= 13/52 + 12/52 − 3/52\n= 22/52 = 11/26",
      "parent_region_id": null,
      "related_region_ids": [
        "p5_addition_rule"
      ],
      "layer": "formulas",
      "grounding_note": "The centered four-line calculation is visible above the highlighted rule.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p5_addition_rule",
      "page": 5,
      "bbox": {
        "x0": 0.147,
        "y0": 0.223,
        "x1": 0.853,
        "y1": 0.344
      },
      "type": "definition",
      "label": "General Addition Rule box",
      "semantic_ids": [
        "union_rule"
      ],
      "source_text_excerpt": "GENERAL ADDITION RULE",
      "parent_region_id": null,
      "related_region_ids": [
        "p5_addition_formula",
        "p5_card_formula",
        "p5_disjoint_practice"
      ],
      "layer": "structure",
      "grounding_note": "Gray highlighted box contains the rule statement, equation, and explanation of the intersection term.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p5_addition_formula",
      "page": 5,
      "bbox": {
        "x0": 0.346,
        "y0": 0.29,
        "x1": 0.655,
        "y1": 0.309
      },
      "type": "formula",
      "label": "Union probability with intersection subtraction",
      "semantic_ids": [
        "union_rule",
        "intersection"
      ],
      "source_text_excerpt": "P(A or B) = P(A) + P(B) − P(A and B)",
      "parent_region_id": "p5_addition_rule",
      "related_region_ids": [
        "p5_loan_diagram"
      ],
      "layer": "formulas",
      "grounding_note": "Centered equation inside the General Addition Rule box.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p5_inclusive_or",
      "page": 5,
      "bbox": {
        "x0": 0.147,
        "y0": 0.359,
        "x1": 0.853,
        "y1": 0.419
      },
      "type": "annotation",
      "label": "Inclusive meaning of or",
      "semantic_ids": [
        "union_rule"
      ],
      "source_text_excerpt": "TIP: “or” is inclusive",
      "parent_region_id": null,
      "related_region_ids": [
        "p5_addition_rule"
      ],
      "layer": "structure",
      "grounding_note": "Blue outlined tip immediately below the rule box.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p5_disjoint_practice",
      "page": 5,
      "bbox": {
        "x0": 0.128,
        "y0": 0.444,
        "x1": 0.855,
        "y1": 0.529
      },
      "type": "example",
      "label": "Disjoint-event simplification exercise",
      "semantic_ids": [
        "disjoint",
        "disjoint_rule"
      ],
      "source_text_excerpt": "GUIDED PRACTICE 3.13 START",
      "parent_region_id": null,
      "related_region_ids": [
        "p5_addition_rule"
      ],
      "layer": "structure",
      "grounding_note": "First blue-marked guided practice asks why the intersection probability is zero for disjoint events.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p5_loan_diagram",
      "page": 5,
      "bbox": {
        "x0": 0.651,
        "y0": 0.881,
        "x1": 0.852,
        "y1": 0.93
      },
      "type": "diagram",
      "label": "Loan attributes Venn diagram",
      "semantic_ids": [
        "intersection",
        "union_rule"
      ],
      "source_text_excerpt": "applicant had a mortgage     joint application\n3839     950     545",
      "parent_region_id": null,
      "related_region_ids": [
        "p5_addition_formula"
      ],
      "layer": "structure",
      "grounding_note": "Small boxed overlapping-ellipse diagram in the bottom footnotes. The whole diagram is grounded; individual tiny counts and overlap boundaries are not separately boxed.",
      "confidence": "medium",
      "excerpt_verified": true
    },
    {
      "region_id": "p6_distribution_definition",
      "page": 6,
      "bbox": {
        "x0": 0.146,
        "y0": 0.095,
        "x1": 0.854,
        "y1": 0.126
      },
      "type": "definition",
      "label": "Definition of a probability distribution",
      "semantic_ids": [
        "distribution"
      ],
      "source_text_excerpt": "A probability distribution is a table of all disjoint outcomes and their associated probabilities.",
      "parent_region_id": null,
      "related_region_ids": [
        "p6_dice_table",
        "p6_distribution_rules"
      ],
      "layer": "structure",
      "grounding_note": "Opening paragraph beneath the Probability distributions section heading.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p6_dice_table",
      "page": 6,
      "bbox": {
        "x0": 0.258,
        "y0": 0.14,
        "x1": 0.742,
        "y1": 0.178
      },
      "type": "table",
      "label": "Two-dice sum probability distribution",
      "semantic_ids": [
        "distribution",
        "event_probability"
      ],
      "source_text_excerpt": "Dice sum 2 3 4 5 6 7 8 9 10 11 12\nProbability 1/36 2/36 3/36 4/36 5/36 6/36 5/36 4/36 3/36 2/36 1/36",
      "parent_region_id": null,
      "related_region_ids": [
        "p6_distribution_rules",
        "p8_complement_practice"
      ],
      "layer": "structure",
      "grounding_note": "Two-row ruled table above the Figure 3.5 caption; fractions are displayed vertically in the source.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p6_distribution_rules",
      "page": 6,
      "bbox": {
        "x0": 0.147,
        "y0": 0.235,
        "x1": 0.853,
        "y1": 0.363
      },
      "type": "definition",
      "label": "Three validity requirements for probability distributions",
      "semantic_ids": [
        "distribution"
      ],
      "source_text_excerpt": "1. The outcomes listed must be disjoint.\n2. Each probability must be between 0 and 1.\n3. The probabilities must total 1.",
      "parent_region_id": null,
      "related_region_ids": [
        "p6_dice_table",
        "p6_income_table"
      ],
      "layer": "structure",
      "grounding_note": "Gray highlighted rules box in the upper-middle portion of the page.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p6_income_table",
      "page": 6,
      "bbox": {
        "x0": 0.282,
        "y0": 0.491,
        "x1": 0.718,
        "y1": 0.555
      },
      "type": "table",
      "label": "Three proposed household-income distributions",
      "semantic_ids": [
        "distribution"
      ],
      "source_text_excerpt": "Income Range $0-25k $25k-50k $50k-100k $100k+\n(a) 0.18 0.39 0.33 0.16\n(b) 0.38 -0.27 0.52 0.37\n(c) 0.28 0.27 0.29 0.16",
      "parent_region_id": null,
      "related_region_ids": [
        "p6_distribution_rules"
      ],
      "layer": "structure",
      "grounding_note": "Ruled table with rows (a), (b), and (c), directly above the Figure 3.6 caption.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p6_sample_complement_definition",
      "page": 6,
      "bbox": {
        "x0": 0.146,
        "y0": 0.791,
        "x1": 0.855,
        "y1": 0.897
      },
      "type": "definition",
      "label": "Die sample space and event complement",
      "semantic_ids": [
        "sample_space",
        "complement"
      ],
      "source_text_excerpt": "Let D = {2, 3} represent the event that the outcome of a die roll is 2 or 3.",
      "parent_region_id": null,
      "related_region_ids": [
        "p8_complement_diagram"
      ],
      "layer": "structure",
      "grounding_note": "Two paragraphs beneath Complement of an event define S, D, and Dᶜ and refer to Figure 3.9.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p8_complement_diagram",
      "page": 8,
      "bbox": {
        "x0": 0.311,
        "y0": 0.07,
        "x1": 0.679,
        "y1": 0.139
      },
      "type": "diagram",
      "label": "Die outcomes partitioned into an event and its complement",
      "semantic_ids": [
        "sample_space",
        "complement"
      ],
      "source_text_excerpt": "",
      "parent_region_id": null,
      "related_region_ids": [
        "p6_sample_complement_definition",
        "p8_complement_rule"
      ],
      "layer": "structure",
      "grounding_note": "Figure 3.9 shows the blue enclosing sample space, red dotted event, and green dashed complement.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p8_sample_space_boundary",
      "page": 8,
      "bbox": {
        "x0": 0.34,
        "y0": 0.071,
        "x1": 0.677,
        "y1": 0.138
      },
      "type": "component",
      "label": "Sample-space enclosure containing all six outcomes",
      "semantic_ids": [
        "sample_space"
      ],
      "source_text_excerpt": "",
      "parent_region_id": "p8_complement_diagram",
      "related_region_ids": [
        "p8_sample_space_label",
        "p8_event_component",
        "p8_complement_component"
      ],
      "layer": "structure",
      "grounding_note": "Blue rounded enclosure surrounds outcomes 1 through 6.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p8_sample_space_label",
      "page": 8,
      "bbox": {
        "x0": 0.311,
        "y0": 0.093,
        "x1": 0.33,
        "y1": 0.112
      },
      "type": "label",
      "label": "Sample-space label S",
      "semantic_ids": [
        "sample_space"
      ],
      "source_text_excerpt": "S",
      "parent_region_id": "p8_complement_diagram",
      "related_region_ids": [
        "p8_sample_space_boundary"
      ],
      "layer": "labels",
      "grounding_note": "Blue S is clearly visible immediately left of the enclosing boundary.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p8_event_component",
      "page": 8,
      "bbox": {
        "x0": 0.411,
        "y0": 0.091,
        "x1": 0.512,
        "y1": 0.118
      },
      "type": "component",
      "label": "Event D containing outcomes 2 and 3",
      "semantic_ids": [
        "complement"
      ],
      "source_text_excerpt": "2 3",
      "parent_region_id": "p8_complement_diagram",
      "related_region_ids": [
        "p8_complement_component"
      ],
      "layer": "structure",
      "grounding_note": "Red dotted oval encloses 2 and 3; this is the event whose complement is shown in green.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p8_complement_component",
      "page": 8,
      "bbox": {
        "x0": 0.366,
        "y0": 0.088,
        "x1": 0.651,
        "y1": 0.131
      },
      "type": "component",
      "label": "Complement Dᶜ containing outcomes 1, 4, 5, and 6",
      "semantic_ids": [
        "complement"
      ],
      "source_text_excerpt": "",
      "parent_region_id": "p8_complement_diagram",
      "related_region_ids": [
        "p8_event_component"
      ],
      "layer": "structure",
      "grounding_note": "Green dashed nonconvex boundary wraps around 1 and 4–6 while excluding 2 and 3. Its rectangular bounding box also spans the excluded event.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p8_complement_rule",
      "page": 8,
      "bbox": {
        "x0": 0.147,
        "y0": 0.398,
        "x1": 0.853,
        "y1": 0.493
      },
      "type": "definition",
      "label": "Complement rule box",
      "semantic_ids": [
        "complement"
      ],
      "source_text_excerpt": "COMPLEMENT",
      "parent_region_id": null,
      "related_region_ids": [
        "p8_complement_diagram",
        "p8_complement_formula"
      ],
      "layer": "structure",
      "grounding_note": "Gray highlighted box defines the complement and states the probability relationship.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p8_complement_formula",
      "page": 8,
      "bbox": {
        "x0": 0.337,
        "y0": 0.465,
        "x1": 0.664,
        "y1": 0.484
      },
      "type": "formula",
      "label": "Event and complement probabilities sum to one",
      "semantic_ids": [
        "complement"
      ],
      "source_text_excerpt": "P(A) + P(Aᶜ) = 1, i.e. P(A) = 1 − P(Aᶜ)",
      "parent_region_id": "p8_complement_rule",
      "related_region_ids": [
        "p8_complement_practice"
      ],
      "layer": "formulas",
      "grounding_note": "Centered equation at the bottom of the highlighted Complement box.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p8_complement_practice",
      "page": 8,
      "bbox": {
        "x0": 0.128,
        "y0": 0.55,
        "x1": 0.855,
        "y1": 0.636
      },
      "type": "example",
      "label": "Two-dice complement calculation exercise",
      "semantic_ids": [
        "complement",
        "event_probability"
      ],
      "source_text_excerpt": "GUIDED PRACTICE 3.19 START",
      "parent_region_id": null,
      "related_region_ids": [
        "p8_complement_formula",
        "p6_dice_table"
      ],
      "layer": "structure",
      "grounding_note": "Blue-marked exercise asks about the complement of a two-dice total less than 12 and explicitly references Figure 3.5.",
      "confidence": "high",
      "excerpt_verified": true
    }
  ],
  "diagnostics": []
}
```

Browser observations: {"success": true, "source_selected": {"region_id": "p5_addition_rule", "focus": "union_rule"}, "focus_preserved": true, "source_view_unchanged": true, "canonical_value_changed": true, "linked_chart_changed": true, "post_compilation_response_attempts": 0, "post_compilation_network_delta": 0, "error": null}

Stability raw/normalized comparison:

```json
{
  "material_id": "probability",
  "accepted": [
    true,
    true,
    true
  ],
  "identical_complete_request_sha256": "67407df68e25a23980df95c2cb826f7140155fb2bc4d70b84dbc5beec68f3f21",
  "raw_contract_declarations": [
    {
      "version": "1.1",
      "preferred": "dynamic",
      "focus_ids": [
        "event_probability",
        "sample_space",
        "events",
        "disjoint",
        "intersection",
        "union_rule",
        "disjoint_rule",
        "distribution",
        "complement"
      ],
      "source_pages": [
        1,
        2,
        4,
        5,
        6,
        7,
        8
      ],
      "features": {
        "equations": true,
        "continuous_parameters": true,
        "time_dynamics": false,
        "spatial_relations": false,
        "finite_outcomes": true,
        "set_relations": true,
        "ordered_collection": false,
        "transitions": false,
        "analogy_suitable": false,
        "structure": true,
        "interaction_value": true
      },
      "process": {
        "collections": [],
        "states": [],
        "transitions": [],
        "annotations": []
      },
      "execution": null
    },
    {
      "version": "1.1",
      "preferred": "structural",
      "focus_ids": [
        "event_probability",
        "sample_space",
        "events",
        "disjoint",
        "intersection",
        "union_rule",
        "disjoint_rule",
        "distribution",
        "complement"
      ],
      "source_pages": [
        1,
        2,
        4,
        5,
        6,
        7,
        8
      ],
      "features": {
        "equations": true,
        "continuous_parameters": true,
        "time_dynamics": false,
        "spatial_relations": true,
        "finite_outcomes": true,
        "set_relations": true,
        "ordered_collection": false,
        "transitions": false,
        "analogy_suitable": false,
        "structure": true,
        "interaction_value": true
      },
      "process": {
        "collections": [],
        "states": [],
        "transitions": [],
        "annotations": []
      },
      "execution": null
    },
    {
      "version": "1.1",
      "preferred": "dynamic",
      "focus_ids": [
        "event_probability",
        "sample_space",
        "events",
        "disjoint",
        "intersection",
        "union_rule",
        "disjoint_rule",
        "distribution",
        "complement"
      ],
      "source_pages": [
        1,
        2,
        4,
        5,
        6,
        7,
        8
      ],
      "features": {
        "equations": true,
        "continuous_parameters": true,
        "time_dynamics": false,
        "spatial_relations": false,
        "finite_outcomes": true,
        "set_relations": true,
        "ordered_collection": false,
        "transitions": false,
        "analogy_suitable": false,
        "structure": true,
        "interaction_value": true
      },
      "process": {
        "collections": [],
        "states": [],
        "transitions": [],
        "annotations": []
      },
      "execution": null
    }
  ],
  "raw_contract_differences": {
    "version": false,
    "preferred": true,
    "focus_ids": false,
    "source_pages": false,
    "features": true,
    "process": false,
    "execution": false
  },
  "normalized_differences": {
    "bindings": false,
    "domain_constraints": false,
    "duration_policy": false,
    "fixed_adjustable": false,
    "inverse_bindings": false,
    "parameter_ids": false,
    "quantities": false,
    "quantity_kinds": false,
    "ranges": false,
    "representation_structure": true,
    "source_pages": false,
    "validator_outcome": false
  },
  "not_measured": [
    "parameter generation",
    "quantity kinds",
    "domain constraints",
    "fixed/adjustable generation",
    "ranges",
    "quantities",
    "bindings",
    "inverse bindings",
    "duration policy"
  ],
  "limitation": "No spatial/probability compiler was selected. Native Lab declarations remain in the fixed main analysis; empty planner fields are not evidence of parameter-generation stability. With fewer than two accepted outputs, normalized stability cannot be established.",
  "A": "HUMAN_REVIEW_PENDING"
}
```

**Human A verdict: PENDING.**

## search

The frozen PDF contains basic Python-operation/loop analysis on original p.226 and search algorithms on p.227. The actual selected Lab varies body-cost exponent a and fixed factor k in loop-growth curves; no bisection/linear-search process was compiled. This is an observed focus difference for human review, not a final source-correctness verdict.

Original planner declaration (including rejected declarations):

```json
{
  "version": "1.1",
  "focus_ids": [
    "runtime_analysis",
    "growth_order",
    "basic_costs",
    "loop_cost",
    "dictionary_costs",
    "linear_search",
    "bisection_search"
  ],
  "source_pages": [
    1,
    2
  ],
  "features": {
    "equations": true,
    "continuous_parameters": true,
    "time_dynamics": false,
    "spatial_relations": false,
    "finite_outcomes": false,
    "set_relations": false,
    "ordered_collection": true,
    "transitions": false,
    "analogy_suitable": false,
    "structure": true,
    "interaction_value": true
  },
  "preferred": "dynamic",
  "reason": "Use the ready numeric lab to compare illustrative constant, linear, and logarithmic growth curves and vary their leading coefficients. This makes the distinction between growth order and constant factors visible and connects loop cost to iteration count. Input size represents an integer count; smooth curves are scaling illustrations, not measured Python timings or exact consequences of Big-O alone",
  "process": {
    "collections": [],
    "states": [],
    "transitions": [],
    "annotations": []
  },
  "execution": null
}
```

Deep source-to-runtime objective observation:

```json
{
  "material_id": "search",
  "A": "HUMAN_REVIEW_PENDING",
  "B": "PASS",
  "browser_status": "PENDING_REAL_BROWSER",
  "browser_errors": "NOT_EVALUATED",
  "context_jumps": "NOT_EVALUATED",
  "direct_manipulation": {
    "available": false,
    "targets": [],
    "absence_is_not_automatic_failure": true
  },
  "post_compilation_api_delta": 0,
  "atlas_status": "accepted",
  "regions": 18,
  "atlas_diagnostics": [],
  "selected_region": "p1_append_formula",
  "selected_semantic_id": "list_costs",
  "semantic_identity_continuity": true,
  "source_grounding": "Validated Atlas link; semantic support/location needs human review",
  "target_ownership": true,
  "linked_support": {
    "semantic_id": "list_costs",
    "source_region_ids": [
      "p1_list_costs",
      "p1_append_formula"
    ],
    "source_pages": [
      1
    ],
    "support": [
      {
        "region_id": "p1_list_costs",
        "page": 1,
        "kind": "estimated_region",
        "confidence": "high"
      },
      {
        "region_id": "p1_append_formula",
        "page": 1,
        "kind": "estimated_region",
        "confidence": "high"
      }
    ],
    "representation_ids": [],
    "manipulation_target_ids": [],
    "formal_parameter_ids": [],
    "manipulable": false,
    "reason_not_manipulable": "No validated direct manipulation is available; use the formal view and existing controls."
  },
  "interaction": "existing Numeric Lab canonical slider callbacks",
  "commit_accepted": true,
  "linked_projection": [
    {
      "demo_id": "loop_growth_demo",
      "parameter_id": "a",
      "canonical_value": 1.2,
      "baseline": 1.0,
      "curve_changed": true,
      "stale_callback_rejected": true,
      "comparison_rows": [
        {
          "id": "a",
          "label": "Body-cost exponent a",
          "unit": "dimensionless",
          "baseline": 1.0,
          "current": 1.2,
          "delta": 0.19999999999999996,
          "generated_range": true
        }
      ]
    }
  ],
  "baseline_current_separation": "Compiled defaults retained; callback updates existing Lab store only",
  "atomic_rejection": "Stale callback rejection tested; arbitrary out-of-range callback injection not claimed",
  "source_roundtrip": {
    "focus_preserved": true,
    "supporting_region": "p1_append_formula",
    "selected_source_context_preserved": true
  },
  "source_immutable": true
}
```

Actual generated Source Atlas regions (estimated boxes/transcriptions, requiring human location/semantic review):

```json
{
  "atlas_version": "1.0",
  "processed_pages": [
    1,
    2
  ],
  "regions": [
    {
      "region_id": "p1_heading",
      "page": 1,
      "bbox": {
        "x0": 0.14,
        "y0": 0.107,
        "x1": 0.585,
        "y1": 0.126
      },
      "type": "label",
      "label": "Analysis of basic Python operations",
      "semantic_ids": [
        "runtime_analysis"
      ],
      "source_text_excerpt": "B.2 Analysis of basic Python operations",
      "parent_region_id": null,
      "related_region_ids": [],
      "layer": "labels",
      "grounding_note": "Bold section heading near the top of the page.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p1_basic_costs",
      "page": 1,
      "bbox": {
        "x0": 0.14,
        "y0": 0.139,
        "x1": 0.79,
        "y1": 0.24
      },
      "type": "definition",
      "label": "Arithmetic and indexing costs",
      "semantic_ids": [
        "basic_costs"
      ],
      "source_text_excerpt": "Indexing operations—reading or writing elements in a sequence or dictionary—are also constant time, regardless of the size of the data structure.",
      "parent_region_id": null,
      "related_region_ids": [],
      "layer": "structure",
      "grounding_note": "The first two paragraphs explain arithmetic costs, the large-integer exception, and indexing.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p1_loop_example",
      "page": 1,
      "bbox": {
        "x0": 0.14,
        "y0": 0.249,
        "x1": 0.79,
        "y1": 0.345
      },
      "type": "example",
      "label": "Linear traversal and list-summing code",
      "semantic_ids": [
        "loop_cost"
      ],
      "source_text_excerpt": "total = 0\nfor x in t:\n    total += x",
      "parent_region_id": null,
      "related_region_ids": [
        "p1_sum_constant_factor",
        "p1_loop_growth"
      ],
      "layer": "structure",
      "grounding_note": "Paragraph introducing linear traversal followed by a three-line indented code example.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p1_sum_constant_factor",
      "page": 1,
      "bbox": {
        "x0": 0.14,
        "y0": 0.35,
        "x1": 0.79,
        "y1": 0.395
      },
      "type": "annotation",
      "label": "Built-in sum and smaller leading coefficient",
      "semantic_ids": [
        "growth_order"
      ],
      "source_text_excerpt": "it has a smaller leading coefficient.",
      "parent_region_id": null,
      "related_region_ids": [
        "p1_loop_example"
      ],
      "layer": "structure",
      "grounding_note": "Paragraph immediately below the code compares implementations with the same linear growth.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p1_loop_growth",
      "page": 1,
      "bbox": {
        "x0": 0.14,
        "y0": 0.404,
        "x1": 0.79,
        "y1": 0.492
      },
      "type": "formula",
      "label": "Loop growth rules and constant iteration factors",
      "semantic_ids": [
        "loop_cost",
        "growth_order"
      ],
      "source_text_excerpt": "As a rule of thumb, if the body of a loop is in O(nᵃ) then the whole loop is in O(nᵃ⁺¹).",
      "parent_region_id": null,
      "related_region_ids": [
        "p1_loop_example"
      ],
      "layer": "formulas",
      "grounding_note": "Two paragraphs contain inline growth expressions and discuss k and n/k iteration counts. The box includes their explanatory prose; formula transcription is not independently verified.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p1_sequence_costs",
      "page": 1,
      "bbox": {
        "x0": 0.14,
        "y0": 0.5,
        "x1": 0.79,
        "y1": 0.641
      },
      "type": "definition",
      "label": "Sequence, slice, concatenation, and string-method costs",
      "semantic_ids": [
        "sequence_costs"
      ],
      "source_text_excerpt": "The string method join is linear; the run time depends on the total length of the strings.",
      "parent_region_id": null,
      "related_region_ids": [],
      "layer": "structure",
      "grounding_note": "Three consecutive paragraphs between the loop rules and the list-method discussion.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p1_list_costs",
      "page": 1,
      "bbox": {
        "x0": 0.14,
        "y0": 0.65,
        "x1": 0.79,
        "y1": 0.775
      },
      "type": "definition",
      "label": "List-method exceptions and average append cost",
      "semantic_ids": [
        "list_costs"
      ],
      "source_text_excerpt": "Most list methods are linear, but there are some exceptions:",
      "parent_region_id": null,
      "related_region_ids": [
        "p1_append_formula"
      ],
      "layer": "structure",
      "grounding_note": "Introductory line and three bullets discuss append, removal from the end, and sorting.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p1_append_formula",
      "page": 1,
      "bbox": {
        "x0": 0.18,
        "y0": 0.708,
        "x1": 0.66,
        "y1": 0.725
      },
      "type": "formula",
      "label": "Total O(n) cost and average O(1) append cost",
      "semantic_ids": [
        "list_costs"
      ],
      "source_text_excerpt": "operations is O(n), so the average time for each operation is O(1).",
      "parent_region_id": "p1_list_costs",
      "related_region_ids": [],
      "layer": "formulas",
      "grounding_note": "Final line of the first list-method bullet contains both asymptotic cost expressions.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p1_dictionary_costs",
      "page": 1,
      "bbox": {
        "x0": 0.14,
        "y0": 0.786,
        "x1": 0.79,
        "y1": 0.886
      },
      "type": "definition",
      "label": "Dictionary costs and iterator exceptions",
      "semantic_ids": [
        "dictionary_costs"
      ],
      "source_text_excerpt": "Most dictionary operations and methods are constant time, but there are some exceptions:",
      "parent_region_id": null,
      "related_region_ids": [
        "p2_dictionary_continuation",
        "p2_hashtable_costs"
      ],
      "layer": "structure",
      "grounding_note": "Bottom paragraph and two bullets explain update and keys, values, and items.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p2_dictionary_continuation",
      "page": 2,
      "bbox": {
        "x0": 0.21,
        "y0": 0.109,
        "x1": 0.861,
        "y1": 0.139
      },
      "type": "annotation",
      "label": "Continuation of dictionary performance discussion",
      "semantic_ids": [
        "dictionary_costs"
      ],
      "source_text_excerpt": "We will see how they work in Section B.4.",
      "parent_region_id": null,
      "related_region_ids": [
        "p1_dictionary_costs"
      ],
      "layer": "structure",
      "grounding_note": "Two-line paragraph above Exercise B.2 continues the preceding page's dictionary discussion.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p2_sorting_exercise",
      "page": 2,
      "bbox": {
        "x0": 0.21,
        "y0": 0.141,
        "x1": 0.862,
        "y1": 0.416
      },
      "type": "annotation",
      "label": "Sorting-algorithm exercise",
      "semantic_ids": [],
      "source_text_excerpt": "Exercise B.2.",
      "parent_region_id": null,
      "related_region_ids": [],
      "layer": "structure",
      "grounding_note": "Exercise introduction and seven numbered questions occupy the upper-middle page. No catalog entity specifically identifies this sorting exercise.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p2_search_heading",
      "page": 2,
      "bbox": {
        "x0": 0.211,
        "y0": 0.452,
        "x1": 0.589,
        "y1": 0.472
      },
      "type": "label",
      "label": "Analysis of search algorithms",
      "semantic_ids": [
        "runtime_analysis"
      ],
      "source_text_excerpt": "B.3 Analysis of search algorithms",
      "parent_region_id": null,
      "related_region_ids": [
        "p2_search_definition"
      ],
      "layer": "labels",
      "grounding_note": "Bold section heading below the exercise; distinct from the running header at the top.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p2_search_definition",
      "page": 2,
      "bbox": {
        "x0": 0.21,
        "y0": 0.485,
        "x1": 0.862,
        "y1": 0.516
      },
      "type": "definition",
      "label": "Collection-and-target search definition",
      "semantic_ids": [
        "runtime_analysis"
      ],
      "source_text_excerpt": "A search is an algorithm that takes a collection and a target item and determines whether the target is in the collection, often returning the index of the target.",
      "parent_region_id": null,
      "related_region_ids": [
        "p2_linear_search",
        "p2_bisection_search"
      ],
      "layer": "structure",
      "grounding_note": "First paragraph directly below the B.3 section heading.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p2_linear_search",
      "page": 2,
      "bbox": {
        "x0": 0.21,
        "y0": 0.525,
        "x1": 0.862,
        "y1": 0.613
      },
      "type": "definition",
      "label": "Linear search and sequence membership",
      "semantic_ids": [
        "linear_search"
      ],
      "source_text_excerpt": "In the worst case it has to traverse the entire collection, so the run time is linear.",
      "parent_region_id": null,
      "related_region_ids": [
        "p2_bisection_comparison"
      ],
      "layer": "structure",
      "grounding_note": "Two paragraphs describe sequential traversal and its use by in, find, and count. No explicit O(n) formula is printed here.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p2_bisection_search",
      "page": 2,
      "bbox": {
        "x0": 0.21,
        "y0": 0.622,
        "x1": 0.862,
        "y1": 0.732
      },
      "type": "process_step",
      "label": "Ordered-sequence bisection and repeated halving",
      "semantic_ids": [
        "bisection_search"
      ],
      "source_text_excerpt": "Either way, you cut the number of remaining items in half.",
      "parent_region_id": null,
      "related_region_ids": [
        "p2_bisection_formula",
        "p2_bisection_comparison"
      ],
      "layer": "structure",
      "grounding_note": "Paragraph explains checking the middle item and selecting one half. This is prose, not a visual flow diagram.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p2_bisection_formula",
      "page": 2,
      "bbox": {
        "x0": 0.211,
        "y0": 0.639,
        "x1": 0.28,
        "y1": 0.655
      },
      "type": "formula",
      "label": "Bisection search complexity O(log n)",
      "semantic_ids": [
        "bisection_search"
      ],
      "source_text_excerpt": "O(log n).",
      "parent_region_id": "p2_bisection_search",
      "related_region_ids": [],
      "layer": "formulas",
      "grounding_note": "Inline complexity expression at the start of the second line of the bisection paragraph.",
      "confidence": "high",
      "excerpt_verified": true
    },
    {
      "region_id": "p2_bisection_comparison",
      "page": 2,
      "bbox": {
        "x0": 0.21,
        "y0": 0.741,
        "x1": 0.862,
        "y1": 0.814
      },
      "type": "example",
      "label": "Million-item search comparison and ordering requirement",
      "semantic_ids": [
        "bisection_search",
        "linear_search"
      ],
      "source_text_excerpt": "If the sequence has 1,000,000 items, it will take about 20 steps to find the word or conclude that it’s not there.",
      "parent_region_id": null,
      "related_region_ids": [
        "p2_linear_search",
        "p2_bisection_search"
      ],
      "layer": "structure",
      "grounding_note": "Two paragraphs give a numerical comparison and explain the prerequisite of ordered data.",
      "confidence": "high",
      "excerpt_verified": false
    },
    {
      "region_id": "p2_hashtable_costs",
      "page": 2,
      "bbox": {
        "x0": 0.21,
        "y0": 0.823,
        "x1": 0.862,
        "y1": 0.886
      },
      "type": "definition",
      "label": "Hashtable implementation and constant-time dictionary search",
      "semantic_ids": [
        "dictionary_costs"
      ],
      "source_text_excerpt": "Python dictionaries are implemented using hashtables, which is why most dictionary operations, including the in operator, are constant time.",
      "parent_region_id": null,
      "related_region_ids": [
        "p1_dictionary_costs"
      ],
      "layer": "structure",
      "grounding_note": "Final paragraph at the bottom of the page introduces hashtables and dictionary membership costs.",
      "confidence": "high",
      "excerpt_verified": true
    }
  ],
  "diagnostics": []
}
```

Browser observations: {"success": true, "source_selected": {"region_id": "p1_append_formula", "focus": "list_costs"}, "focus_preserved": true, "source_view_unchanged": true, "canonical_value_changed": true, "linked_chart_changed": true, "post_compilation_response_attempts": 0, "post_compilation_network_delta": 0, "error": null}

**Human A verdict: PENDING.**

## complexity

The Lab varies coefficient a from 2 to 200 (source-example default 100) and plots a*n+1 against n**2+n+1. Frozen expectations keep source coefficients fixed and permit integer input size n; the generated plot samples n continuously and labels integer sizes as the algorithmic interpretation.

Original planner declaration (including rejected declarations):

```json
{
  "version": "1.1",
  "focus_ids": [
    "runtime_functions",
    "algorithm_example",
    "crossover",
    "leading_terms",
    "growth_classes",
    "practical_limits"
  ],
  "source_pages": [
    2,
    3
  ],
  "features": {
    "equations": true,
    "continuous_parameters": true,
    "time_dynamics": false,
    "spatial_relations": false,
    "finite_outcomes": false,
    "set_relations": true,
    "ordered_collection": true,
    "transitions": false,
    "analogy_suitable": false,
    "structure": true,
    "interaction_value": true
  },
  "preferred": "dynamic",
  "reason": "The ready numeric lab can compare the source-supported curves 100n + 1 and n² + n + 1 while learners vary the input-size range. Their positive crossover is n = 99, illustrating why a linear algorithm can cost more for small inputs yet scale better for large inputs. Comparing the supplied linear examples 2n, 100n, and n + 1 also distinguishes practical coefficients from growth-class membership. Use",
  "process": {
    "collections": [],
    "states": [],
    "transitions": [],
    "annotations": []
  },
  "execution": null
}
```

**Human A verdict: PENDING.**

## spectrum

The selected family is static and the main analysis contains no Lab. This exercises a table/concept presentation rather than frequency/wavelength conversion controls. The frozen expectation permits an honest static table.

Original planner declaration (including rejected declarations):

```json
{
  "version": "1.1",
  "focus_ids": [
    "radiation",
    "frequency",
    "wavelength",
    "energy",
    "meter_scale",
    "equivalent_units",
    "scientific_notation",
    "size_references"
  ],
  "source_pages": [
    1
  ],
  "features": {
    "equations": false,
    "continuous_parameters": false,
    "time_dynamics": false,
    "spatial_relations": false,
    "finite_outcomes": false,
    "set_relations": true,
    "ordered_collection": false,
    "transitions": false,
    "analogy_suitable": true,
    "structure": true,
    "interaction_value": false
  },
  "preferred": "static",
  "reason": "Use a structured comparison linking radio and microwaves to frequency in Hertz, infrared and visible light to wavelength in meters, and X-rays and gamma rays to energy in electron volts. Highlight that a common wavelength scale in meters enables comparison across these conventions, with scientific notation and size references aiding interpretation. The supplied excerpt lacks complete conversion120",
  "process": {
    "collections": [],
    "states": [],
    "transitions": [],
    "annotations": []
  },
  "execution": null
}
```

**Human A verdict: PENDING.**

## debugging

The selected family is static, with a concept map and no Numeric Lab. There is no drag/slider expectation for this source. The interpreter/code examples remain source data and were not executed.

Original planner declaration (including rejected declarations):

```json
{
  "version": "1.1",
  "focus_ids": [
    "debugging",
    "syntax",
    "runtime",
    "semantic",
    "location",
    "inspection",
    "checklist",
    "running_code"
  ],
  "source_pages": [
    1,
    2
  ],
  "features": {
    "equations": false,
    "continuous_parameters": false,
    "time_dynamics": false,
    "spatial_relations": false,
    "finite_outcomes": true,
    "set_relations": false,
    "ordered_collection": true,
    "transitions": false,
    "analogy_suitable": false,
    "structure": true,
    "interaction_value": false
  },
  "preferred": "static",
  "reason": "Use a structured comparison of syntax, runtime, and semantic errors, paired with a syntax-debugging checklist. Distinguish when each error is detected and what its symptoms indicate. Connect syntax errors to cautious interpretation of reported locations, close inspection of recent or copied code, common structural checks, and verification that the edited file is executed. The numbered checks are a",
  "process": {
    "collections": [],
    "states": [],
    "transitions": [],
    "annotations": []
  },
  "execution": null
}
```

Browser observations: {"success": true, "source_selected": null, "focus_preserved": true, "source_view_unchanged": null, "canonical_value_changed": null, "linked_chart_changed": null, "post_compilation_response_attempts": 0, "post_compilation_network_delta": 0, "error": null}

**Human A verdict: PENDING.**
