# damage_curves/ — moved to the `damage_modeling` repo

**This work has been relocated.** The damage-curve foundations + implementation library no longer live in
`Hazard_modeling`; they are now their own repo, **`damage_modeling`**, a *sibling* of this one.

Damage modeling is a separate discipline that **feeds** hazard modeling's M3 stage — it is not part of the
hazard engine. (Reasoning: the scope-and-story, linked below.)

## Where everything went

| Was here (`Hazard_modeling/docs/extra/discussion/damage_curves/`) | Now in `damage_modeling/` |
|---|---|
| `SCOPE_AND_STORY.md` | `docs/damage_curves/SCOPE_AND_STORY.md` ← **the anchor** |
| `damage_curve_foundations/` | `docs/damage_curves/damage_curve_foundations/` |
| `damage_curve_implementation/` | `docs/damage_curves/damage_curve_implementation/` |
| the `00`–`07` scaffold + `assumptions.md` | `docs/damage_curves/` (superseded by the foundations) |

## Open it

```
infrasure_git_codes/damage_modeling/docs/damage_curves/SCOPE_AND_STORY.md
```

Relative from here (via the `damage_modeling/` symlink now at this repo's root):
[`../../../../damage_modeling/docs/damage_curves/SCOPE_AND_STORY.md`](../../../../damage_modeling/docs/damage_curves/SCOPE_AND_STORY.md)

## Why moved, not copied

One home, no drift — the platform's prior bug was version drift between two copies of a model. The damage
section is maintained **only** in `damage_modeling` now. This tombstone stays so existing links into
`damage_curves/` don't dangle.

— relocated 2026-06-21.
