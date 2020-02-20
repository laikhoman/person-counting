from flask import render_template, redirect, url_for, abort, flash, request, \
    current_app, make_response, g, Response
from .forms import AddCameraForm, AddPlaceForm, CoordinateForm, EditPlaceForm, DateForm
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from . import main
from .. import db
from ..models import Place, Cctv, Line, User, Event
import os
import requests
import subprocess
import sys
import pickle
import datetime
from datetime import datetime
from os import path
import json
from sqlalchemy import func

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from ..camera_opencv import Camera

@main.route('/', methods=['GET'])
@login_required
def index():
    place_list = Place.query.filter_by(user_id=current_user.id).all()

    dict_arr_of_place = []
    for i in range(len(place_list)):
        tmp_dict = {}
        tmp_dict['id'] = place_list[i].id
        tmp_dict['name'] = place_list[i].name
        tmp_dict['city'] = place_list[i].city
        dict_arr_of_place.append(tmp_dict)

    add_edit_place = ""
    if len(place_list) > 0:
        add_edit_place = "Edit_Place"
    else:
        add_edit_place = "Add_Place"

    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    in_event_list = db.session.query(Event.event, Event.timestamp, func.count(Event.event)).filter(Event.timestamp >= todays_datetime, Event.event=='in').group_by(Event.hour).all()
    out_event_list = db.session.query(Event.event, Event.timestamp, func.count(Event.event)).filter(Event.timestamp >= todays_datetime, Event.event == 'out').group_by(Event.hour).all()

    in_datetime_list = []
    in_count_list = []
    out_datetime_list = []
    out_count_list = []

    for i in range(len(in_event_list)):
        in_datetime_list.append(in_event_list[i].timestamp.replace(minute=0).replace(second=0).strftime("%Y-%m-%d %H:%M:%S"))
        in_count_list.append(in_event_list[i][2])

    for i in range(len(out_event_list)):
        out_datetime_list.append(out_event_list[i].timestamp.replace(minute=0).replace(second=0).strftime("%Y-%m-%d %H:%M:%S"))
        out_count_list.append(out_event_list[i][2])

    print("in_datetime_list", in_datetime_list)
    print("in_count_list", in_count_list)
    print("out_datetime_list", out_datetime_list)
    print("out_count_list", out_count_list)

    total_in = sum(in_count_list)
    total_out = sum(out_count_list)
    total_entries = total_in + total_out
    # return render_template('index.html', place=dict_arr_of_place)
    # return render_template('index.html', place=dict_arr_of_place, add_edit_string=add_edit_place)
    return render_template('index.html',
                           in_datetime_list=json.dumps(in_datetime_list),
                           in_count_list=json.dumps(in_count_list),
                           out_datetime_list=json.dumps(out_datetime_list),
                           out_count_list=json.dumps(out_count_list),
                           total_in = total_in,
                           total_out = total_out,
                           total_entries = total_entries,
                           add_edit_string=add_edit_place)

@main.route('/add_place/<string:add_edit_string>', methods=['GET', 'POST'])
@login_required
def add_place(add_edit_string):
    form = AddPlaceForm()
    if (form.validate_on_submit()):
        place = Place(name=form.name.data,
                      city=form.city.data,
                      user_id=current_user.id)
        db.session.add(place)
        db.session.commit()
        db.session.flush()
        db.session.refresh(place)
        print("inserted id", place.id)
        return redirect(url_for('main.cctv', place_id=place.id, add_edit_string="Add_Camera_On_Place"))
        # return render_template(url_for('main.html', place_id=place.id, add_edit_string="Add_Camera_On_Place"))
    else:
        print('error validation', form.errors)
    return render_template('places.html', form=form, add_edit_string=add_edit_string)

@main.route('/edit_place/<string:add_edit_string>', methods=['GET', 'POST'])
@login_required
def edit_place(add_edit_string):
    place_list = Place.query.filter_by(user_id=current_user.id).all()
    place_id = place_list[0].id
    place = Place.query.get_or_404(place_id)
    place_name = place.name
    place_city = place.city
    print(place_name, place_city)
    form = EditPlaceForm()
    if (form.validate_on_submit()):
        place = db.session.query(Place).filter(Place.id==place_id).first()

        name = request.form['name']
        city = request.form['city']

        place.name = name
        place.city = city

        db.session.commit()

        cctv_list = Cctv.query.filter_by(place_id=place_id).all()
        cctv_id = cctv_list[0].id
        cctv = Cctv.query.get_or_404(cctv_id)
        cctv_label = cctv.label
        cctv_url = cctv.url
        print("cctv_label",cctv_label)
        print("cctv_url", cctv_url)

        return redirect(url_for('main.cctv', cctv_label=cctv_label, cctv_url=cctv_url, place_id=place.id, add_edit_string="Edit_Camera_On_Place"))
    else:
        print('error validation', form.errors)
    return render_template('places.html', form=form, place_name=place_name, place_city=place_city, add_edit_string=add_edit_string)

@main.route('/get_cameras', methods=['GET', 'POST'])
@login_required
def get_cameras():
    form = AddPlaceForm()
    return render_template('places.html', form=form)

@main.route('/cctv', methods=['GET'])
@login_required
def cctv():
    form = AddCameraForm()
    place_id = request.args.get('place_id', None)
    add_edit_string = request.args.get('add_edit_string', None)
    cctv_label = request.args.get('cctv_label', None)
    cctv_url = request.args.get('cctv_url', None)
    return render_template('cctv.html', place_id=place_id, form=form, cctv_label=cctv_label, cctv_url=cctv_url, add_edit_string=add_edit_string)

@main.route('/add_cctv/<int:place_id>/<string:add_edit_string>', methods=['POST'])
@login_required
def add_cctv(place_id,add_edit_string):
    print("success place_id",place_id)
    form = AddCameraForm()
    if(form.validate_on_submit()):
        camera = Cctv(label=form.label.data,
                        url=form.url.data,
                        place_id=place_id)
        db.session.add(camera)
        db.session.commit()
        db.session.flush()
        db.session.refresh(camera)
        print("inserted id", camera.id)
        return render_template('streaming.html', cctv_id=camera.id, place_id=place_id, add_edit_string=add_edit_string)
    else:
        print('error validation', form.errors)
    return render_template('cctv.html', place_id=place_id, add_edit_string=add_edit_string)

@main.route('/edit_cctv/<int:place_id>/<string:add_edit_string>', methods=['GET', 'POST'])
@login_required
def edit_cctv(place_id,add_edit_string):
    cctv_list = Cctv.query.filter_by(place_id=place_id).all()
    cctv_id = cctv_list[0].id
    cctv = Cctv.query.get_or_404(cctv_id)
    cctv_label = cctv.label
    cctv_url = cctv.url

    form = AddCameraForm()
    if(form.validate_on_submit()):
        cctv = db.session.query(Cctv).filter(Cctv.id == cctv_id).first()

        label = request.form['label']
        url = request.form['url']

        cctv.label = label
        cctv.url = url

        db.session.commit()
        return render_template('streaming.html', cctv_id=cctv_id, place_id=place_id, add_edit_string=add_edit_string)
    else:
        print('error validation', form.errors)
    return render_template('cctv.html', form=form, cctv_label=cctv_label, cctv_url=cctv_url, add_edit_string=add_edit_string)

@main.route('/cctv_by_place/<int:place_id>/<string:place_name>', methods=['GET'])
@login_required
def cctv_by_place(place_id, place_name):
    cctv_list = Cctv.query.filter_by(place_id=place_id).all()

    dict_arr_of_cctv = []
    for i in range(len(cctv_list)):
        tmp_dict = {}
        tmp_dict['id'] = cctv_list[i].id
        tmp_dict['label'] = cctv_list[i].label
        tmp_dict['url'] = cctv_list[i].url
        dict_arr_of_cctv.append(tmp_dict)

    # return render_template('index.html', place=dict_arr_of_place)
    return render_template('cctv_by_place.html', cctv=dict_arr_of_cctv)

@main.route('/line', methods=['GET'])
def line():
    form = CoordinateForm()
    cctv_id = request.args.get('cctv_id', None)
    place_id = request.args.get('place_id', None)
    add_edit_string = request.args.get('add_edit_string', None)
    line_list = Line.query.filter_by(cctv_id=cctv_id).all()
    if len(line_list) > 0:
        x1 = line_list[0].x1
        y1 = line_list[0].y1
        x2 = line_list[0].x2
        y2 = line_list[0].y2
        return render_template('line.html', cctv_id=cctv_id, place_id=place_id, form=form,
                               add_edit_string=add_edit_string, x1=x1, y1=y1, x2=x2, y2=y2)
    return render_template('line.html', cctv_id=cctv_id, place_id=place_id, form=form, add_edit_string=add_edit_string)

@main.route('/do_restreaming/<string:channel>', methods=['GET'])
def do_restreaming(channel):
    return requests.get('http://0.0.0.0:5001/video_feed/' + channel)

@main.route('/add_line/<int:cctv_id>/<int:place_id>', methods=['GET', 'POST'])
def add_line(cctv_id,place_id):
    print("success cctv_id", cctv_id)
    form = CoordinateForm()
    if (form.validate_on_submit()):
        line = Line(cctv_id=cctv_id,
                      x1=int(int(form.x1.data) * 300/640),
                      y1=int(int(form.y1.data) * 300/360),
                      x2=int(int(form.x2.data) * 300/640),
                      y2=int(int(form.y2.data) * 300/360))
        db.session.add(line)
        db.session.commit()
        db.session.flush()
        db.session.refresh(line)
        place_list = Place.query.filter_by(id=place_id).all()
        place_name = place_list[0].name
        city = place_list[0].city
        cctv_list = Cctv.query.filter_by(place_id=place_id).all()
        dict_arr_of_cctv = []
        for i in range(len(cctv_list)):
            tmp_dict = {}
            tmp_dict['id'] = cctv_list[i].id
            tmp_dict['label'] = cctv_list[i].label
            tmp_dict['url'] = cctv_list[i].url
            dict_arr_of_cctv.append(tmp_dict)
        # return render_template('list_cctv.html', cctv=dict_arr_of_cctv, cctv_id=cctv_id, place_name=place_name, city=city)
        # call service restreaming and pass the url
        url = cctv_list[0].url
        cctv_url_string_split = url.split("/")
        do_restreaming(cctv_url_string_split[len(cctv_url_string_split)-1])
        return redirect(url_for('main.index'))
    else:
        print('error validation', form.errors)
    return render_template('cctv.html')

@main.route('/edit_line/<int:cctv_id>/<int:place_id>', methods=['GET', 'POST'])
@login_required
def edit_line(cctv_id,place_id):
    cctv_list = Cctv.query.filter_by(place_id=place_id).all()
    cctv_id = cctv_list[0].id
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0
    line_list = Line.query.filter_by(cctv_id=cctv_id).all()
    if len(line_list) > 0:
        x1 = line_list[0].x1
        y1 = line_list[0].y1
        x2 = line_list[0].x2
        y2 = line_list[0].y2

    form = CoordinateForm()
    if(form.validate_on_submit()):
        line = db.session.query(Line).filter(Cctv.id == cctv_id).first()

        x1 = int(int(request.form['x1']) * 300 / 640)
        y1 = int(int(request.form['y1']) * 300 / 360)
        x2 = int(int(request.form['x2']) * 300 / 640)
        y2 = int(int(request.form['y2']) * 300 / 360)
        print(x1, y1, x2, y2)

        line.x1 = x1
        line.y1 = y1
        line.x2 = x2
        line.y2 = y2

        db.session.commit()

        # call service restreaming and pass the url
        url = cctv_list[0].url
        cctv_url_string_split = url.split("/")
        myList = [str(current_user.id), str(line.id), url, str(x1), str(y1), str(x2), str(y2)]
        p = subprocess.Popen([sys.executable, 'for_run.py'] + myList)

        # do_restreaming(cctv_url_string_split[len(cctv_url_string_split) - 1])
        # return redirect(url_for('main.index'))
        return redirect(url_for('main.list_cctv', cctv_id=cctv_id))
    else:
        print('error validation', form.errors)
    return render_template('line.html', cctv_id=cctv_id, place_id=place_id, form=form, x1=x1, y1=y1, x2=x2, y2=y2)

@main.route('/get_channel', methods=['GET'])
def get_channel():
    place_list = Place.query.filter_by(user_id=current_user.id).all()
    place_id = place_list[0].id
    cctv_list = Cctv.query.filter_by(place_id=place_id).all()
    cctv_channel_string_split = cctv_list[0].url.split("/")
    cctv_channel_string = cctv_channel_string_split[len(cctv_channel_string_split) - 1]
    return cctv_channel_string

@main.route('/list_places',  methods=['GET'])
@login_required
def list_places():
    return render_template('list_place.html')

@main.route('/list_cctv/<int:cctv_id>',  methods=['GET'])
@login_required
def list_cctv(cctv_id):
    cctv_list = Cctv.query.filter_by(id=cctv_id).all()
    place_id = cctv_list[0].place_id

    place_list = Place.query.filter_by(id=place_id).all()
    place_name = place_list[0].name
    city = place_list[0].city

    cctv_list_place_id = Cctv.query.filter_by(place_id=place_id).all()
    dict_arr_of_cctv = []
    for i in range(len(cctv_list_place_id)):
        tmp_dict = {}
        tmp_dict['id'] = cctv_list_place_id[i].id
        tmp_dict['label'] = cctv_list_place_id[i].label
        tmp_dict['url'] = cctv_list_place_id[i].url
        dict_arr_of_cctv.append(tmp_dict)

    # this is for retrieving line_id to know status_line of core runner
    line_list = Line.query.filter_by(cctv_id=cctv_list_place_id[0].id).all()
    line_id = line_list[0].id

    with open("app/main/status_line/" + str(line_id) + ".txt", "r") as mytxt:
        for line in mytxt:
            status_line = int(line)
    mytxt.close()
    on_off = ""
    if status_line == 0:
        on_off = "off"
    else:
        on_off = "on"

    return render_template('list_cctv.html', cctv=dict_arr_of_cctv, cctv_id=cctv_id, place_name=place_name, city=city, on_off=on_off)

@main.route('/get_cctv_channel', methods=['GET'])
def get_cctv_channel():
    cctv_list = Cctv.query.filter_by(id=1).all()
    cctv_channel_string_split = cctv_list[0].url.split("/")
    cctv_channel_string = cctv_channel_string_split[len(cctv_channel_string_split)-1]
    return cctv_channel_string

@main.route('/list_report_by_cctv_id/<int:cctv_id>',  methods=['GET'])
@login_required
def list_report_by_cctv_id(cctv_id):
    cctv_list = Cctv.query.filter_by(id=cctv_id).all()
    place_id = cctv_list[0].place_id

    place_list = Place.query.filter_by(id=place_id).all()
    place_name = place_list[0].name
    city = place_list[0].city

    cctv_list_place_id = Cctv.query.filter_by(place_id=place_id).all()
    dict_arr_of_cctv = []
    for i in range(len(cctv_list_place_id)):
        tmp_dict = {}
        tmp_dict['id'] = cctv_list_place_id[i].id
        tmp_dict['label'] = cctv_list_place_id[i].label
        tmp_dict['url'] = cctv_list_place_id[i].url
        dict_arr_of_cctv.append(tmp_dict)

    return render_template('list_report.html', cctv=dict_arr_of_cctv, cctv_id=cctv_id, place_name=place_name, city=city)

@main.route('/view_chart/<int:cctv_id>', methods=['GET'])
@login_required
def view_chart(cctv_id):
    cctv_list = Cctv.query.filter_by(id=cctv_id).all()
    place_id = cctv_list[0].place_id
    cctv_label = cctv_list[0].label

    place_list = Place.query.filter_by(id=place_id).all()
    place_name = place_list[0].name
    city = place_list[0].city

    cctv_list_place_id = Cctv.query.filter_by(place_id=place_id).all()
    dict_arr_of_cctv = []
    for i in range(len(cctv_list_place_id)):
        tmp_dict = {}
        tmp_dict['id'] = cctv_list_place_id[i].id
        tmp_dict['label'] = cctv_list_place_id[i].label
        tmp_dict['url'] = cctv_list_place_id[i].url
        dict_arr_of_cctv.append(tmp_dict)

    # get line(s) id
    line_list = Line.query.filter_by(cctv_id=cctv_id).all()
    line_id = line_list[0].id

    return render_template('view_chart.html', line_id=line_id, cctv_label=cctv_label, cctv=dict_arr_of_cctv, cctv_id=cctv_id, place_name=place_name, city=city)

@main.route('/activate_cctv/<int:cctv_id>/<int:active>', methods=['GET', 'POST'])
@login_required
def activate_cctv(cctv_id,active):
    data_from_js = cctv_id
    line_list = Line.query.filter_by(cctv_id=data_from_js).all()
    line_id = line_list[0].id

    # input multi items
    global core_runner_list
    file_path = path.relpath("app/main/abc" + str(current_user.id) + ".bin")
    with open(file_path, "rb") as f:
        core_runner_list = pickle.load(f)
    f.close()
    for i in range(len(core_runner_list)):
        if core_runner_list[i].line_id == str(line_id):
            if active == 0:
                core_runner_list[i].stop()
            elif active == 1:
                core_runner_list[i].start()
    return render_template('index.html')

def toDate(dateString):
    return datetime.strptime(dateString, "%Y-%m-%d %H:%M:%S")

@main.route('/get_event/<string:line_id>/<string:in_out>/<string:dateandtime>', methods=['GET'])
def get_event(line_id, in_out, dateandtime):
    event_up = Event(line_id=int(line_id),
                     event=in_out,
                     timestamp=toDate(dateandtime))
    db.session.add(event_up)
    db.session.commit()
    db.session.flush()
    db.session.refresh(event_up)
    return str(event_up.id)

@main.route('/get_rtsp_image_by_address/<int:cctv_id>')
def get_rtsp_image_by_address(cctv_id):
    """Video streaming route. Put this in the src attribute of an img tag."""
    cctv = Cctv.query.filter_by(id=cctv_id).all()
    cctv_url_split = cctv[0].url.split('/')
    cctv_channel = cctv_url_split[len(cctv_url_split) - 1]
    camera = Camera(cctv_channel)
    camera.set_video_source(cctv[0].url)
    return Response(gen_once(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_once(camera):
    """Video streaming generator function."""
    frame = camera.get_frame()
    # frame = cv2.resize(camera.get_frame(), (300,300))
    yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@main.route('/first_last', methods=['GET'])
def first_last():
    return render_template('first_last.html')

@main.route('/get_first_last/<string:date_string>', methods=['GET', 'POST'])
def get_first_last(date_string):
    return render_template('index.html', date_string=date_string)
    # return redirect(url_for('main.first_last'))

@main.route('/query_date', methods=['GET'])
def query_date():
    form = DateForm()
    if (form.validate_on_submit()):
        print(form.date)
        return redirect(url_for('main.get_first_last', date_string=form.date))
        # return render_template(url_for('main.html', place_id=place.id, add_edit_string="Add_Camera_On_Place"))
    else:
        print('error validation', form.errors)
    return render_template('first_last.html')

@main.route('/camera/<int:id>')
@login_required
def get_camera():
    return render_template('places.html')

@main.route('/add-camera', methods=['GET', 'POST'])
@login_required
def add_camera():
    data = request.form
    return render_template('places.html', data=data)

@main.route('/edit-camera/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_camera():
    return render_template('edit_camera.html')

@main.route('/remove-camera/<int:id>', methods=['POST'])
@login_required
def remove_camera():
    return redirect('index')

@main.route('/just_test', methods=['GET'])
@login_required
def just_test():
    return render_template('just_test.html')
