import os

if not "SQLALCHEMY_DATABASE_URI" in os.environ:
    URI = "postgres+psycopg2://openoversight:terriblepassword@localhost:5432/postgres"
    os.environ["SQLALCHEMY_DATABASE_URI"] = URI
    
import pandas as pd
from OpenOversight.app import models
from OpenOversight.app import create_app


app = create_app()
# with app.app_context() as ctx:
app.app_context().push()
session = app.db.session
