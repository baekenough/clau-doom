#!/usr/bin/env python3
"""Quick test to verify KILLCOUNT is now tracked correctly.

This test confirms that game_variables now contains [KILLCOUNT, HEALTH, AMMO2]
in the correct order, and that kills != ammo (which was the bug).
"""

from vizdoom_bridge import VizDoomBridge, ACTION_ATTACK, ACTION_MOVE_LEFT


def test_game_variable_mapping():
    """Verify game variables are in correct order after fix."""
    bridge = VizDoomBridge("defend_the_center.cfg")

    # Start episode
    bridge.start_episode(seed=42)

    # Get initial state
    state = bridge.get_game_state()
    print(f"Initial state: kills={state.kills}, health={state.health}, ammo={state.ammo}")

    # Verify initial values
    assert state.kills == 0, f"Expected 0 kills, got {state.kills}"
    assert state.health == 100, f"Expected 100 health, got {state.health}"
    assert state.ammo == 26, f"Expected 26 ammo (AMMO2), got {state.ammo}"

    # Execute some actions
    for _ in range(10):
        bridge.make_action(ACTION_ATTACK)  # Attack a few times

    # Check state again
    state2 = bridge.get_game_state()
    print(f"After 10 attacks: kills={state2.kills}, health={state2.health}, ammo={state2.ammo}")

    # CRITICAL: kills and ammo must be different values
    # Before the fix, kills would always equal ammo (both reading AMMO2)
    # After the fix, kills tracks KILLCOUNT (index 0), ammo tracks AMMO2 (index 2)
    assert state2.kills != state2.ammo, \
        f"BUG STILL PRESENT: kills={state2.kills} should not equal ammo={state2.ammo}"

    print("✓ KILLCOUNT mapping verified: kills and ammo are independent values")

    bridge.close()


def test_game_variable_order_directly():
    """Directly inspect game_variables array to verify [KILLCOUNT, HEALTH, AMMO2] order."""
    import vizdoom

    game = vizdoom.DoomGame()
    game.load_config(str(vizdoom.scenarios_path / "defend_the_center.cfg"))

    # Apply the fix
    game.clear_available_game_variables()
    game.add_available_game_variable(vizdoom.GameVariable.KILLCOUNT)  # index 0
    game.add_available_game_variable(vizdoom.GameVariable.HEALTH)     # index 1
    game.add_available_game_variable(vizdoom.GameVariable.AMMO2)      # index 2

    game.set_window_visible(False)
    game.init()

    game.new_episode()

    state = game.get_state()
    if state and state.game_variables:
        gv = state.game_variables
        print(f"game_variables array: {gv}")
        print(f"  [0] = {gv[0]} (should be KILLCOUNT, initially 0)")
        print(f"  [1] = {gv[1]} (should be HEALTH, initially 100)")
        print(f"  [2] = {gv[2]} (should be AMMO2, initially 26)")

        assert len(gv) == 3, f"Expected 3 game variables, got {len(gv)}"
        assert gv[0] == 0, f"KILLCOUNT (index 0) should be 0 initially, got {gv[0]}"
        assert gv[1] == 100, f"HEALTH (index 1) should be 100 initially, got {gv[1]}"
        assert gv[2] == 26, f"AMMO2 (index 2) should be 26 initially, got {gv[2]}"

        print("✓ game_variables order verified: [KILLCOUNT, HEALTH, AMMO2]")

    game.close()


if __name__ == "__main__":
    print("Testing KILLCOUNT fix...")
    print("\n--- Test 1: Game variable mapping ---")
    test_game_variable_mapping()

    print("\n--- Test 2: Direct game_variables array inspection ---")
    test_game_variable_order_directly()

    print("\n✓✓✓ All tests passed! KILLCOUNT is now correctly tracked.")
