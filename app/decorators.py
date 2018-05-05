from flask_login import current_user
from app.models import Permission
from flask import abort, request, jsonify
from functools import wraps
import blinker

def use_signal(signal):
    assert isinstance(signal, blinker.NamedSignal)

    def decorator(func):
        signal.connect(func)
        return func
    return decorator


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def wrapper(*args,**kwargs):
            if current_user.can(permission):
                return f(*args,**kwargs)
            abort(403)
        return wrapper
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)

def require_ajax(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        if not request.is_xhr:
            return jsonify(
                {
                    'error':'Bad Request',
                    'code':400
                }
            )
        return f(*args,**kwargs)
    return wrapper





