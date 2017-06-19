from flask import Flask
from flask import request
from obj_finder import ObjFinder

app = Flask(__name__)


@app.route('/')
def hello_world():
    args = request.args
    print args
    return 'Hello World!'

@app.route('/query')
def query():
    usage_info = "Unknown parameter, usage: \"http://10.10.10.22:8088/query?t=[engine or proxy]&v=[version code]&a=[address list, like:0x11000,0x20000]\""
    args = request.args
    keys = args.keys()
    query_result = ''

    if 'v' not in keys or 't' not in keys or 'a' not in keys:
        return usage_info

    t = args['t']
    v = args['v']
    a = args['a']

    obj_finder = ObjFinder(version_code=v)
    query_result = obj_finder.query_address(t,a)


    return str(query_result)






if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8088)
