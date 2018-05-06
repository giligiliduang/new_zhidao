from app import db
from app.main import main
from flask import request, render_template, redirect, url_for, current_app, flash, jsonify
from flask_login import login_required, current_user

from app.models import User, Message
from app.constants import MessageType, MessageStatus, DeleteStatus
from app.main.forms import MessageForm, SendMessageForm
from app.main.views.search import search
from app.decorators import require_ajax, admin_required


@main.route('/user/<id>/messages')
@login_required
def messages(id):
    s = search()
    if s:
        return s
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    type = request.args.get('type')
    user.set_messages_read()
    in_box_pagination = user.in_box_messages.order_by(Message.timestamp.desc()).paginate(page,
                                                                                         per_page=current_app.config[
                                                                                             'ZHIDAO_MESSAGE_PER_PAGE'],
                                                                                         error_out=False)

    send_box_pagination = user.send_box_messages.filter(Message.message_type != MessageType.system).order_by(
        Message.timestamp.desc()).paginate(page,
                                           per_page=
                                           current_app.config[
                                               'ZHIDAO_MESSAGE_PER_PAGE'],
                                           error_out=False)

    in_box_messages = in_box_pagination.items
    send_box_messages = send_box_pagination.items

    context = dict(in_box_pagination=in_box_pagination, send_box_pagination=send_box_pagination,
                   in_box_messages=in_box_messages, send_box_messages=send_box_messages, type=type)
    return render_template('message/messages.html', **context)


@main.route('/dialogue/<int:id>', methods=['GET', 'POST'])
@login_required
def dialogue(id):
    """
    显示我和其他人的对话
    可以在此页面回复
    :param id:该私信作者id
    :return:
    """
    s = search()
    if s:
        return s
    u = User.query.get_or_404(id)  # 发给我私信的人
    page = request.args.get('page', 1, type=int)
    form = MessageForm()
    if form.validate_on_submit():
        current_user.send_standard_message_to(form.body.data, to=u)
        flash('成功回复了{}'.format(u.username))
        return redirect(url_for('main.messages', id=current_user.id))
    pagination = current_user.dialogue_with(u).order_by(Message.timestamp.desc()).paginate(
        page, per_page=current_app.config['ZHIDAO_MESSAGE_PER_PAGE'], error_out=False
    )
    messages = pagination.items
    context = dict(pagination=pagination, messages=messages, sender=u, form=form)
    return render_template('message/dialogue.html', **context)


@main.route('/send_message', methods=['GET', 'POST'])
@login_required
def send_message():
    s = search()
    if s:
        return s
    form = SendMessageForm()
    if form.validate_on_submit():
        current_user.send_standard_message_to(content=form.body.data,
                                              to=form.user.data)
        flash('发送成功')
        return redirect(url_for('main.messages', id=current_user.id))

    context = dict(form=form)
    return render_template('message/send_message.html', **context)


@main.route('/send_system_message', methods=['GET', 'POST'])
@login_required
@admin_required
def send_system_msg():
    s = search()
    if s:
        return s
    form = MessageForm()
    if form.validate_on_submit():
        current_user.send_system_message(form.body.data)
        flash('系统消息发送成功')
        return redirect(url_for('main.messages', id=current_user.id))
    type = 'system'

    system_messages = Message.query.filter(Message.message_type == MessageType.system,
                                           Message.delete_status != DeleteStatus.author_delete).all()
    context = dict(form=form, type=type, system_messages=system_messages)
    return render_template('message/send_message.html', **context)


@main.route('/delete_snd_msg', methods=['POST'])
@login_required
@require_ajax
def delete_msg():
    msg_id = request.form.get('msg_id', type=int)
    mode = request.form.get('mode')
    if msg_id is None or mode is None or (mode not in ['author_delete', 'user_delete']):
        return jsonify(
            {
                'error': 'BAD REQUEST',
                'code': '400'
            }
        )
    msg = Message.query.get_or_404(msg_id)
    if mode == 'author_delete':
        msg.delete_status = DeleteStatus.author_delete
        db.session.add(msg)
        db.session.commit()
        return jsonify(
            {
                'success': 'OK',
                'code': '200'
            }
        )
    if mode == 'user_delete':
        msg.delete_status = DeleteStatus.user_delete
        db.session.add(msg)
        db.session.commit()
        return jsonify(
            {
                'success': 'OK',
                'code': '200'
            }
        )
    return jsonify(
        {
            'error': 'wrong id',
            'code': '401'
        }
    )
