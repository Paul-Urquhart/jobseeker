from flask import Flask, render_template
from . import app
import requests
from requests.auth import HTTPBasicAuth
import json
import os
from app.db import Session
from app.models import CandidateJob


@app.route("/")
def main():
 
    db_session = Session()
    app.logger.info("connected to database")
    try:
        data = db_session.query(CandidateJob).order_by(CandidateJob.date_posted.desc()).all()
        app.logger.info("results retrieved")
    except Exception:
        app.logger.exception("exception occured.")
    finally:
        db_session.close()

    app.logger.info(f"Raw results: {len(data)}")

    return render_template('index.html', data=data)
