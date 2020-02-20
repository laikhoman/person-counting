from flask import render_template, redirect, url_for, current_app, make_response
from flask_sqlalchemy import get_debug_queries
from . import main
from .. import db

@main.route('/', methods=['GET','POST'])
def index(): 
    return render_template('index.html')

@main.route('/cameras', methods=['GET','POST'])
def show_cameras():
    return render_template('')

