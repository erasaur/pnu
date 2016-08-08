from flask import render_template, redirect, url_for, request
from app import app

@app.route('/')
def index_view():
    return render_template('index.html')


@app.route('/map')
def map_view():
    qs = str(request.query_string)
    if qs:
        for char in ['=', ',']:
            if char not in qs:
                print("CHAR: {} not in data!".format(char))
                return redirect(url_for('index_view'))

        return render_template('map.html')
    else:
        return redirect(url_for('index_view'))


@app.route('/locations', methods=['POST', 'GET'])
def locations():
    if request.method == 'POST':
        city = request.args.get('city')
        # search for city!
    return render_template('locations.html')


@app.route('/')
@app.route('/<path:path>')
def catch_all(path=None):
    return redirect(url_for('index_view'))
