import flask

app = flask.Flask(__name__)

@app.route('/farmceo')
def farmCEO():
    return flask.send_file("./build/web/index.html")

@app.route('/farm_ceo.apk')
def farmApk():
    return flask.send_file('./build/web/farm_ceo.apk')

app.run(host='0.0.0.0')