from importlib.resources import files


def test_dashboard_assets_exist_in_package():
    web = files("vantawave.web")
    assert web.joinpath("index.html").is_file()
    assert web.joinpath("app.css").is_file()
    assert web.joinpath("app.js").is_file()
