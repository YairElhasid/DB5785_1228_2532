from sqlalchemy import Column, Integer, String, Date, Numeric, DateTime, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declared_attr

Base = declarative_base()

def get_dynamic_model(table_name, engine):
    class DynamicModel(Base):
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True}

        @declared_attr
        def __table__(cls):
            inspector = inspect(engine)
            columns = []
            for column in inspector.get_columns(table_name):
                col_name = column['name']
                col_type = column['type']
                col_args = {}
                if column['primary_key']:
                    col_args['primary_key'] = True
                if 'INTEGER' in str(col_type):
                    col = Column(col_name, Integer, **col_args)
                elif 'NUMERIC' in str(col_type):
                    col = Column(col_name, Numeric, **col_args)
                elif 'DATE' in str(col_type):
                    col = Column(col_name, Date, **col_args)
                elif 'TIMESTAMP' in str(col_type):
                    col = Column(col_name, DateTime, **col_args)
                else:
                    col = Column(col_name, String, **col_args)
                columns.append(col)
            return Table(table_name, Base.metadata, *columns)

    return DynamicModel