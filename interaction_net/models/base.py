from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import os

db_uri = os.environ["DATABASE_URL"].replace("postgresql://", "cockroachdb://")
ENGINE = create_engine(
    db_uri, connect_args={"application_name": "docs_simplecrud_sqlalchemy"}, echo=True
)
Base = declarative_base()
