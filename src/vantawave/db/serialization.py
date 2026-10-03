from __future__ import annotations


def orm_to_dict(record) -> dict:
    data = {}
    for column in record.__table__.columns:
        value = getattr(record, column.name)
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        data[column.name] = value
    return data
