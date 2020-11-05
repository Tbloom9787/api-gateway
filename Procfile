gateway: FLASK_APP=gateway flask run -p $PORT
sandman: sandman2ctl -p $PORT sqlite+pysqlite:///mockroblog.db
datasette: datasette -p $PORT --reload mockroblog.db