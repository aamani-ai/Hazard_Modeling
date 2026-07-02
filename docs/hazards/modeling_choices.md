# Hazard Modeling Choices

This is the convention for each hazard's `modeling_choices.md` file.

The hazard folder now has four distinct records:

| File | Question it answers |
|---|---|
| `README.md` | What is the hazard, how does M0-M4 work at a readable level, what is the current state, and where do I go next? |
| `fundamentals_before_m0.md` | What physics and data-source reality must I understand before opening M0? |
| `source_selection.md` | Which sources did we choose for V1, and why not the others? |
| `modeling_choices.md` | Which M0-M4 modeling choices do we make, why, what caveats do they carry, and when do we revisit them? |

The README should explain the main M0-M4 flow in plain language. `modeling_choices.md` is the modeling-centric
choice ledger beside `source_selection.md`: it gives the rationale behind the M0-M4 choices without becoming a
notebook transcript or duplicating the full `docs/plans/*/decisions.md` register. It should be the fastest way
to answer:

```text
What exactly does M1 emit, and why that shape?
What distribution choices are we making, and why?
Where does the asset enter, and why there?
What does M2 change, and what does it deliberately leave unchanged?
What does M3 consume and return, and why that curve family?
How does M4 sample annual losses, and why this aggregation rule?
Which assumptions are load-bearing?
Where are we unsure, and what better modeling path might replace the V1 choice?
What would make us revisit each choice?
```

It should not replace the README's model story, duplicate a notebook, or become the full decision register. It
should summarize each choice and link to the authoritative plan, assumption, notebook, and asset pages.

---

## Required Shape

Each hazard-level `modeling_choices.md` should use this structure.

### 1. Modeling State

State whether this is built on main, a preview from a branch, planned, or deferred. Name the built asset cells
and the screening-grid status.

### 2. M0-M4 Choice Table

Use one compact table:

| Layer | This hazard's model object | Main choices and rationale |
|---|---|---|
| M0 | source evidence | source grain, access, raw-vs-derived boundary |
| M1 | event model / hazard profile | count process, severity process, distribution choices |
| M2 | coupling | areal / field-intensity / site-conditioned; what changes frequency, intensity, exposure |
| M3 | damage | intensity variable, curve family, value basis, uncertainty |
| M4 | annual loss | count draws, event-loss draws, AEP/OEP, metrics, aggregation rules |

### 3. Event Model Choices

Spell out the M1 object and why it is valid in the terms of
[`m0_m4_event_loss_contract.md`](m0_m4_event_loss_contract.md):

```text
event count process:
  distribution / source / fitted or read / dispersion

conditional severity process:
  distribution / source / units / bounds / tail treatment

event identity / dependence:
  available, approximated, or deferred
```

For multi-sub-peril hazards, split this section by sub-peril.

### 4. Coupling Choices

State the M2 coupling type, why it applies, and whether M2 changes:

```text
lambda
local intensity
exposed fraction
event family / correlation
```

### 5. Damage Choices

State what M3 consumes/emits and why the current curve form is acceptable for V1:

```text
input intensity
damage ratio curve
value allocation / TIV basis
deterministic mean vs conditional distribution
confidence and calibration status
```

### 6. M4 Sampling And Aggregation Choices

State exactly how annual losses are sampled and why:

```text
counts
event severities
coupling
M3 application
AEP/OEP vectors
metrics read from vectors
```

Also state the aggregation doctrine:

```text
EAL can be additive by source/sub-peril.
Tail metrics are read from the joint annual-loss distribution.
Never collapse event loss to expected loss for PML/VaR/TVaR.
```

### 7. Open Questions And Better Ways

Write the honest review notes here. This is where the hazard owner records:

```text
open questions
  what we are not fully sure about yet

better-way candidates
  methods or sources that may replace the V1 choice

review checks
  notebook behavior / validation evidence needed before promotion
```

These are not random TODOs. They should be tied to a load-bearing modeling choice above.

### 8. Assumptions, Caveats, And Revisit Triggers

Carry only the load-bearing modeling assumptions. Link to the full registers.

### 9. Built Numbers And Confidence

List headline proof-of-flow numbers only when they exist. Label them as reportable, screening, provisional, or
directional.

---

## Naming

The file is always:

```text
docs/hazards/<hazard>/modeling_choices.md
```

The hazard anchor should include the readable M0-M4 story itself and then link to this file near the top and in
`Go deeper`.

Per-asset pages should link back to it when explaining M2-M4 mechanics.
