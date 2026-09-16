from flask import jsonify


def ok(data=None, status=200):
    payload = {"success": True}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status


def error(message, status=400, code=None):
    payload = {"success": False, "error": {"message": message}}
    if code:
        payload["error"]["code"] = code
    return jsonify(payload), status


def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions
