from flask import Flask
import logging

app = Flask(__name__)

app.logger.setLevel(logging.INFO)

from . import routes