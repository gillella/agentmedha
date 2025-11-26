from agent_medha.workers.pet_manager import (
    check_litterbox_status,
    start_petkit_clean_cycle,
    run_petkit_odor_removal,
    set_petkit_auto_clean_delay,
    toggle_petkit_sleep_mode,
)


def test_status_tool_returns_summary():
    result = check_litterbox_status()
    assert isinstance(result, str)
    assert "Litter box status" in result


def test_clean_cycle_and_settings_tools():
    assert "Clean cycle started" in start_petkit_clean_cycle()
    assert "Odor removal engaged" in run_petkit_odor_removal(5)
    assert "Auto-clean delay updated" in set_petkit_auto_clean_delay(6)
    assert "Sleep mode enabled" in toggle_petkit_sleep_mode(True)
