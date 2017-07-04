from flask import Flask
from flask import request
from obj_finder import ObjFinder
import sys
app = Flask(__name__)


@app.route('/')
def hello_world():
    return app.send_static_file('index.html')

@app.route('/new')
def index_new():
    return app.send_static_file('index_ajax.html')


@app.route('/query')
def query():
    usage_info = "Unknown parameter, usage: \"http://10.10.10.22:8088/query?t=[engine or proxy]&v=[version code]&a=[address list, like:0x11000,0x20000]\""
    args = request.args
    keys = args.keys()

    if 'v' not in keys or 't' not in keys or 'a' not in keys:
        return usage_info

    t = args['t']
    v = args['v']
    a = args['a']

    try:
        obj_finder = ObjFinder(version_code=v)
        query_result = obj_finder.query_address(t,a)
    except Exception,error:
        return str(error.message)

    return str(query_result)






if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8088)
