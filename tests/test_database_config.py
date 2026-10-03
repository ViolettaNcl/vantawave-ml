from vantawave.db.config import DatabaseConfig


def test_postgresql_url_detection():
    assert DatabaseConfig("postgresql+psycopg://u:p@localhost/db").is_postgresql
    assert not DatabaseConfig("sqlite:///test.db").is_postgresql
