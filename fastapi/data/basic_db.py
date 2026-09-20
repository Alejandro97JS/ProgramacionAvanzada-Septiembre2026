from sqlalchemy import create_engine, text
import sqlalchemy

engine = create_engine('sqlite:///people.db', echo=True)

conn = engine.connect()

# Ejecutar el comando
conn.execute(text("CREATE TABLE IF NOT EXISTS people (name str, age int)"))

# aplicarlo
conn.commit()

from sqlalchemy.orm import Session

session = Session(engine)
session.execute(text('INSERT INTO people (name, age) VALUES ("Mike",30);'))
session.commit()