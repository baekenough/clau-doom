# KILLCOUNT Variable Mapping Bug Fix

## Summary

**Critical bug fixed**: `vizdoom_bridge.py` was reading the wrong game variable index, causing all "kills" values in experiments to actually be AMMO2 (ammo count) instead of actual kill count.

## Root Cause

The `defend_the_center.cfg` scenario file defines:
```
available_game_variables = { AMMO2 HEALTH }
```

This means `state.game_variables` returns only 2 elements: `[AMMO2, HEALTH]`

However, the bridge code at line 132-135 assumed:
```python
game_vars = state.game_variables  # [KILLCOUNT, HEALTH, AMMO2]  ← WRONG!
kills = int(game_vars[0])   # Actually reads AMMO2 (always 26)!
health = int(game_vars[1])  # Correctly reads HEALTH
ammo = int(game_vars[2])    # Index out of range (only 2 vars)!
```

**Result**: All experiments recorded `kills=26` (the ammo count) instead of actual kill counts. KILLCOUNT was never tracked.

## Fix Applied

Modified `_configure_game()` to explicitly set game variables in the correct order **before** calling `init()`:

```python
def _configure_game(self) -> None:
    # ... existing config ...

    # CRITICAL FIX: Override game variables to ensure correct index mapping
    # The defend_the_center.cfg defines: available_game_variables = { AMMO2 HEALTH }
    # which would give us only [AMMO2, HEALTH] (2 elements, missing KILLCOUNT!)
    # We MUST explicitly set the correct order BEFORE init()
    self._game.clear_available_game_variables()
    self._game.add_available_game_variable(self._vizdoom.GameVariable.KILLCOUNT)  # index 0
    self._game.add_available_game_variable(self._vizdoom.GameVariable.HEALTH)     # index 1
    self._game.add_available_game_variable(self._vizdoom.GameVariable.AMMO2)      # index 2

    self._game.init()
```

## Additional Changes

1. **Updated default ammo**: Changed from 52 to 26 (actual AMMO2 starting value in defend_the_center)
2. **Updated all ammo references**: Changed all hardcoded `52` to `26` throughout the file
3. **Added TODO**: Documented that AMMO2 tracks cell ammo, but pistol uses bullet ammo (AMMO5). shots_fired calculation via AMMO2 delta won't work accurately for pistol-only scenarios.

## Files Modified

- `glue/vizdoom_bridge.py`: Applied fix

## Verification

Run the verification test:
```bash
cd glue
python test_vizdoom_fix.py
```

Expected output:
```
✓ KILLCOUNT mapping verified: kills and ammo are independent values
✓ game_variables order verified: [KILLCOUNT, HEALTH, AMMO2]
✓✓✓ All tests passed! KILLCOUNT is now correctly tracked.
```

## Impact on Existing Experiments

**All previous experiments (DOE-001 through DOE-005) are INVALID** because:
- `kills` values were actually AMMO2 counts (always 26)
- Real kill counts were never recorded
- Any statistical analysis based on "kills" was analyzing ammo counts instead

**Action required**:
1. Mark all previous experiment results as INVALID
2. Re-run all experiments with the fixed code
3. Update RESEARCH_LOG.md to document this critical data quality issue

## Related Issues

- AMMO2 vs AMMO5 tracking: The current code tracks AMMO2 (cell ammo) but defend_the_center uses a pistol (bullet ammo, tracked by AMMO5). shots_fired calculation may still be inaccurate.
- Consider adding AMMO5 tracking if precise shots_fired metrics are needed.

## Commit Message Template

```
fix(glue): correctly track KILLCOUNT instead of AMMO2

The defend_the_center.cfg only defines {AMMO2, HEALTH} in
available_game_variables, causing game_variables[0] to be AMMO2
instead of KILLCOUNT. All "kills" values in experiments were
actually ammo counts (always 26).

Fix: Explicitly override game variables before init() to ensure
correct mapping: [KILLCOUNT, HEALTH, AMMO2].

BREAKING: All previous experiment data is invalid and must be re-run.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```
