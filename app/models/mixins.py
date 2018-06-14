from ..ext import db
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime


class BaseMixin(object):


    @classmethod
    def create(cls, **kwargs):
        session = db.session
        if 'id' in kwargs:
            obj = session.query(cls).get('id')
            if obj:
                return obj
        obj = cls(**kwargs)
        session.add(obj)
        session.commit()
        return obj


class DateTimeMixin(object):
    @declared_attr
    def timestamp(self):
        return db.Column(db.DateTime, default=datetime.utcnow)

    @declared_attr
    def updated(self):
        return db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


