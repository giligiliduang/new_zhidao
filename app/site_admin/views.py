import os
from flask_admin import BaseView,expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin

from flask_login import login_required, current_user
# from ..models import Permission
from .forms import  CKTextAreaField,AdminLoginForm


# class MyView(BaseView):
#     """自定义视图"""
#
# #这里类似于app.route()，处理url请求
#     @login_required
#     @admin_required
#     @expose('/')
#     def index(self):
#         return self.render('site_admin/index.html')











class CustomModelView(ModelView):
    """自定义模型类管理"""
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_administrator()



class PostView(CustomModelView):
    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']

    form_overrides = {
        'body': CKTextAreaField
    }
    column_searchable_list = ('title','body')
    column_filters = ('timestamp','tags')

class AnswerView(CustomModelView):
    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']

    form_overrides = {
        'body': CKTextAreaField
    }
    column_searchable_list = ('body',)
    column_filters = ('timestamp',)
class QuestionView(CustomModelView):
    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']

    form_overrides = {
        'description': CKTextAreaField
    }
    column_searchable_list = ('title',)
    column_filters = ('timestamp',)
class CommentView(CustomModelView):
    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']

    form_overrides = {
        'body': CKTextAreaField
    }
    column_searchable_list = ('body',)
    column_filters = ('timestamp',)




class CustomFileAdmin(FileAdmin):
    pass


