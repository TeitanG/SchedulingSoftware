from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable
from sqlmodel import SQLModel

import App.db.models  # noqa: F401

print(sorted(SQLModel.metadata.tables.keys()))
for table in SQLModel.metadata.sorted_tables:
    print(CreateTable(table).compile(dialect=postgresql.dialect()))
