from wtforms import Field
from wtforms.widgets import TextInput

from app.models import Tag


class TagListField(Field):
    widget = TextInput()

    def __init__(self, label=None, validators=None,
                 **kwargs):
        super(TagListField, self).__init__(label, validators, **kwargs)

    def _value(self):
        if self.data:
            r = u''
            for obj in self.data:
                r += self.obj_to_str(obj)
            return u''
        else:
            return u''

    def process_formdata(self, valuelist):
        print('process_formdata..')
        print(valuelist)
        if valuelist:
            tags = self._remove_duplicates([x.strip() for x in valuelist[0].split(',')])
            self.data = [self.str_to_obj(tag) for tag in tags]
        else:
            self.data = None

    def pre_validate(self, form):
        pass

    @classmethod
    def _remove_duplicates(cls, seq):
        """去重"""
        d = {}
        for item in seq:
            if item.lower() not in d:
                d[item.lower()] = True
                yield item

    @classmethod
    def str_to_obj(cls, tag):
        """将字符串转换位obj对象"""
        tag_obj = Tag.query.filter_by(title=tag).first()
        if tag_obj is None:
            tag_obj = Tag.create(title=tag)
        return tag_obj

    @classmethod
    def obj_to_str(cls, obj):
        """将对象转换为字符串"""
        if obj:
            return obj.title
        else:
            return u''
