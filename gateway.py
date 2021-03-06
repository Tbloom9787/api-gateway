#
# Simple API gateway in Python
#
# Inspired by <https://github.com/vishnuvardhan-kumar/loadbalancer.py>
#
#   $ python3 -m pip install Flask python-dotenv
#

import sys
import flask
import requests
from itertools import cycle
from flask_basicauth import BasicAuth

app = flask.Flask(__name__)
app.config.from_envvar('APP_CONFIG')

upstream = app.config['UPSTREAM']

users = cycle(app.config['USERS'])
users_endpoints = app.config['USERS_ENDPOINTS']

timelines = cycle(app.config['TIMELINES'])
timelines_endpoints = app.config['TIMELINES_ENDPOINTS']

# Override of check_credentials for custom authentication with route
def over_check_credentials(self, user, pass):
    response = requests.post((next(users) + '/authenticate'), json={'username': user, 'pass': pass})

    if response.status_code == 200:
        return True
    else:
        return False

BasicAuth.check_credentials = over_check_credentials

basic_auth = BasicAuth(app)

# Start of round robin cycle attempt
def route_handler(path):
    if path in user_endpoints:
        return next(users) + path
    elif path in timelines_endpoints:
        return next(timelines) + path
    else:
        flask.abort(400, status="Bad Request")

@basic_auth.required
@app.errorhandler(404)
def route_page(err):
    try:
        response = requests.request(
            route_handler(flask.request.path),
            flask.request.method,
            upstream + flask.request.full_path,
            data=flask.request.get_data(),
            headers=flask.request.headers,
            cookies=flask.request.cookies,
            stream=True,
        )
    except requests.exceptions.RequestException as e:
        app.log_exception(sys.exc_info())
        return flask.json.jsonify({
            'method': e.request.method,
            'url': e.request.url,
            'exception': type(e).__name__,
        }), 503

    headers = remove_item(
        response.headers,
        'Transfer-Encoding',
        'chunked'
    )

    return flask.Response(
        response=response.content,
        status=response.status_code,
        headers=headers,
        direct_passthrough=True,
    )


def remove_item(d, k, v):
    if k in d:
        if d[k].casefold() == v.casefold():
            del d[k]
    return dict(d)