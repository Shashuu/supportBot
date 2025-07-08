from flask import jsonify, make_response

def build_response(statusCode, data):
    flag = 0
    if statusCode == 200:
        flag = 1
    return make_response(jsonify({"flag": flag, "data": data}), statusCode)
