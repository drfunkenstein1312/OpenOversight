import os

# os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
import pandas as pd
from OpenOversight.app import models
from OpenOversight.app import create_app
from OpenOversight.app.models import db


app = create_app("development")
ctx = app.app_context()
ctx.push()
db.app = app
# db.create_all()
session = db.session


def maybe_add_dept(session, name, short_name):
    q = session.query(models.Department).filter_by(name=name).all()
    if not q:
        dept = models.Department(name=name, short_name=short_name)
        session.add(dept)
        session.commit()
    else:
        assert len(q) == 1
        dept = q.pop()

    return dept


def maybe_add_unit(session, id, description, dept):
    q = session.query(models.Unit).filter_by(id=id).all()
    if not q:
        unit = models.Unit(id=id, descrip=description, department_id=dept.id)
        session.add(unit)
        session.commit()
    else:
        assert len(q) == 1
        unit = q.pop()

    return unit


def maybe_add_job(session, job_title, order, dept, is_sworn_officer=True):
    q = (
        session.query(models.Job)
        .filter_by(
            job_title=job_title,
            department_id=dept.id,
            is_sworn_officer=is_sworn_officer,
        )
        .all()
    )
    if not q:
        job = models.Job(
            job_title=job_title,
            order=order,
            department_id=dept.id,
            is_sworn_officer=is_sworn_officer,
        )
        session.add(job)
        session.commit()
    else:
        assert len(q) == 1
        job = q.pop()

    return job


def add_officer(session, last_name, first_name, middle_initial, dept):
    officer = models.Officer(
        last_name=last_name,
        first_name=first_name,
        middle_initial=middle_initial,
        department_id=dept.id,
    )
    session.add(officer)
    session.commit()

    return officer


SPD = maybe_add_dept(
    session, name="Seattle Police Department", short_name="SPD"
)

# Q = pd.read_csv("/usr/src/app/2016-SPD-roster.csv")
Q = pd.read_excel(
    "https://cdn.muckrock.com/foia_files/2016/02/04/Appeal_16-116_DailyStaffRoster-Name-W02__011116.xls"
)
Q = Q.iloc[:-2]

exclude_names = ["Chiefs Office Floor 8"]
Q = Q[~Q.Name.isin(exclude_names)]

sworn_officer_titles = [
    "Police Recruit",
    "Police - Reserve Officer",
    "Police Officer Probation",
    "Parking Enfor Officer",
    "Parking Enfor Officer, Spvsr",
    "Police Student Officer",
    "Police Officer",
    "Police Sergeant",
    "Acting Police Sergeant",
    "Police Officer Detective",
    "Acting Police Officer Detective",
    "Police Sergeant Detective",
    "Acting Police Sergeant Detective",
    "Police Lieutenant",
    "Acting Police Lieutenant",
    "Police Captain",
    "Assistant Chief Of Police",
    "Deputy Chief Of Police",
    "Chief Of Police",
    # "Fbi Agent",
    # "Atf",
]

ORDER = [
    "unknown",
    "Officer",
    "Sergeant",
    "Lieutenant",
    "Captain",
    "Assistant Chief",
    "Deputy Chief",
    "Chief Of Police",
]


def get_order(title):
    for i, order in enumerate(ORDER):
        if order in title:
            return i

    return 0


# Q = Q[Q["Rank/Title Description"].isin(sworn_officer_titles)]

for i, row in Q.iterrows():
    last_name, first_name = row.Name.split(",")
    last_name, first_name = last_name.strip(), first_name.strip()
    first_name_parsed = first_name.split()
    maybe_middle = first_name_parsed[-1]
    if len(maybe_middle) == 2 and maybe_middle[1] == ".":
        middle_initial = maybe_middle[0]
        first_name = " ".join(first_name_parsed[:-1])
    else:
        middle_initial = None

    officer = add_officer(
        session,
        last_name=last_name,
        first_name=first_name,
        middle_initial=middle_initial,
        dept=SPD,
        # serial_number=row.Serial,
    )

    job_title = row["Rank/Title Description"]

    job = maybe_add_job(
        session=session,
        job_title=job_title,
        order=get_order(job_title),
        dept=SPD,
        is_sworn_officer=job_title in sworn_officer_titles,
    )

    unit_id = row.Unit
    descriptions = Q[Q.Unit == unit_id].UnitDescription.unique()
    assert len(descriptions) == 1
    description = descriptions[0]
    unit = maybe_add_unit(
        session, id=unit_id, description=description, dept=SPD
    )

    models.Assignment(
        job_id=job.id, officer=officer, unit_id=unit.id, star_no=row.Serial
    )
