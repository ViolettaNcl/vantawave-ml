from vantawave.lab.comparison import compare_feature_windows

def test_compare_feature_windows():
    result = compare_feature_windows(
        {"event_rate": 1.0, "auth_rate": 0.1},
        {"event_rate": 2.0, "auth_rate": 0.2},
    )
    by_name = {item.feature: item for item in result}
    assert by_name["event_rate"].absolute_change == 1.0
    assert by_name["event_rate"].percent_change == 100.0
