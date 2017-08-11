from flask import request, Response, g, session, jsonify, url_for
from . import notifications_blueprint
from app.user_model.user_model import User
from .notifications import Notifications, NotificationSteeings
from .chat import Chat
import json


@notifications_blueprint.before_request
def before_request():
    g.permission = User.auth()
    if g.permission >= 2:
        g.this_user = User(session['id'], session['id'])


@notifications_blueprint.route('/updater')
def updater():
    data = "data: {}\n\n"
    if g.permission < 1:
        msg = 'you have no permission'
    else:
        Notifications.update_last_seen(session['id'])
        notifications_count = Notifications.count_unread(session['id'])
        msg_count = Chat.count_unread(session['id'])
        msg = {"notifications_count": notifications_count, "msg_count": msg_count}
        msg = json.dumps(msg)
    return Response(data.format(msg,), mimetype='text/event-stream')


@notifications_blueprint.route('/chat_add', methods=['POST'])
def chat_add():
    data = {'response': 'OK'}
    result = request.get_json()
    if User.connected(result['user_id'], result['receiver_id']):
        Chat.add(result['user_id'], result['receiver_id'], result['msg'])
        if Chat.chat_notification_allowed(result['receiver_id'], session['id']):
            settings = NotificationSteeings(result['receiver_id'])
            Notifications(result['receiver_id'], session['login'],
                          url_for('routes.chat_view', login=g.this_user.login), settings, 'incoming_massage', session['id'])
    return jsonify(data)
    

@notifications_blueprint.route('/chat_updater/<other_user_id>')
def chat_updater(other_user_id):
    data = "data: {}\n\n"
    if g.permission < 1:
        msg = 'you have no permission'
    else:
        unread_msgs = Chat.get_unread(session['id'], other_user_id)
        Chat.set_as_read(session['id'], other_user_id)
        msg = json.dumps(unread_msgs)
    return Response(data.format(msg, ), mimetype='text/event-stream')


@notifications_blueprint.route('/get_notifications')
def get_notifications():
    if g.permission < 1:
        msg = {'status': 'KO'}
    else:
        msg = {'status': 'OK', 'notif': Notifications.get_n(session['id'])}
        Notifications.set_as_read(session['id'])
    return jsonify(msg)
