#!/usr/bin/python
from OpenOversight.app import create_app
# from OpenOversight.app.models import db

app = create_app()
app.app_context().push()
app.db.create_all()
