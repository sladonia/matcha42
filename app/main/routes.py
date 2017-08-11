from flask import render_template, redirect, request, g, flash, url_for, session, jsonify, current_app
from app.user_model.user_model import User
from app.notifications.chat import Chat
from app.visit_history.visit_history import VisitHistory
from app.notifications.notifications import Notifications, NotificationSteeings
from app.search_engine.forms import FilterForm
from app.search_engine.research import Research
from .forms import LoginForm, RegistrationForm, ProfileForm, EditProfileForm, \
    EditNotificationsForm, SendPasswordEmailForm, NewPasswdForm
from . import main_blueprint
from .pagination import Pagination

from functools import wraps


USER_REMOVED = "YOUR ACCOUNT DATA HAS BEEN REMOVED"
EMAIL_CONFIRMED = "NEW EMAIL HAS BEEN SET. YOU CAN NOW LOG IN"
UPDATED = "UPDATED"
NOT_AUTH_MSG = 'You need to log in before access the requested page'
FILL_IN_PROFILE_MSG = 'You need to fill in your profile before access the requested page'
ADD_PHOTO_MSG = 'You need to add your photo before performing this action'
ACCESS_DENIED = 'Access denied'
LOGGED_OUT_MSG = 'You are now logged out'
INVALID_USER = 'Login or password incorrect'
CONFIRMATION_EMAIL = 'Confirmation email has been sent. Please, follow the link in the email to finish registration'
UPDATE_EMAIL = 'Confirmation email has been sent. Please, follow the link in the email to confirm email change'
RESET_PASSWD_MAIL = 'Folow the link on your email to reset password'
RESET_PASSWD_CONFIRMED = 'You can now login with tour new password'
PER_PAGE = 10


def ssl_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if current_app.config.get("SSL"):
            if request.is_secure:
                return fn(*args, **kwargs)
            else:
                return redirect(request.url.replace("http://", "https://"))

        return fn(*args, **kwargs)

    return decorated_view


@main_blueprint.before_request
def before_request():
    g.permission = User.auth()
    if g.permission >= 2:
        g.this_user = User(session['id'], session['id'])
        g.sm_av_path = User.get_avatar_mini_path(session['id'])
        g.av_path = User.get_avatar_path(session['id'])
        g.connection_ids, g.requested_connection_ids, g.unconfirmed_connection_ids = \
            User.get_all_connection_ids(session['id'])
        g.all_connection_ids = list(set(g.connection_ids + g.requested_connection_ids + g.unconfirmed_connection_ids))


@ssl_required
@main_blueprint.route('/', methods=['GET', 'POST'])
@main_blueprint.route('/index', methods=['GET', 'POST'])
def landing_view():
    if g.permission > 0:
        return redirect('/cabinet')
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit() and User.verify_passwd(form.login.data,
                                                            form.passwd.data):
            User.log_in(form.login.data)
            return redirect('/cabinet')
        else:
            flash(INVALID_USER, 'text-danger')
            return redirect('/')
    return render_template('landing.html', title='Sign in', form=form)


@ssl_required
@main_blueprint.route('/registration', methods=['GET', 'POST'])
def registration_view():
    if g.permission > 0:
        return redirect('/cabinet')
    form = RegistrationForm()
    if form.validate_on_submit():
        User.register(form.login.data, form.email.data, form.passwd.data,
                      form.first_name.data, form.last_name.data, form.birth_date.data)
        User.send_registration_email(form.email.data, form.login.data)
        flash(CONFIRMATION_EMAIL, 'text-success')
        return redirect('/')
    return render_template('registration.html', form=form)


@ssl_required
@main_blueprint.route('/reset_passwd', methods=['GET', 'POST'])
def reset_password_view():
    if g.permission > 0:
        return redirect('/cabinet')
    form = SendPasswordEmailForm()
    if form.validate_on_submit():
        User.send_reset_passwd_email(form.email.data)
        flash(RESET_PASSWD_MAIL, 'text-success')
        return redirect('/')
    return render_template('reset_passwd.html', form=form)


@ssl_required
@main_blueprint.route('/new_passwd/<login>/<token>', methods=['GET', 'POST'])
def assign_new_passwd_view(login, token):
    if g.permission > 0:
        return redirect('/cabinet')
    if not User.check_login_token(login, token):
        flash('You shall not pass!', 'text-danger')
        return redirect('/')
    form = NewPasswdForm()
    if form.validate_on_submit():
        User.update_passwd(User.get_user_id(login), form.passwd.data)
        flash(RESET_PASSWD_CONFIRMED, 'text-success')
        return redirect('/')
    return render_template('new_passwd.html', form=form)


@ssl_required
@main_blueprint.route('/create_profile/<login>', methods=['GET', 'POST'])
def create_profile_view(login):
    form = ProfileForm()
    if form.validate_on_submit():
        User.update_access_status(login, 2)
        User.create_profile(User.get_user_id(login), form.gender.data,
                            form.preferences.data,
                            form.biography.data,
                            form.interests.data,
                            form.city.data,
                            form.show_location.data)
        User.log_in(login)
        User.create_user_folder(session['login'], session['id'])
        return redirect(url_for('routes.add_photo_view'))
    if User.accept_confirmation_email(login):
        User.update_access_status(login, 1)
        return render_template('create_profile.html', form=form)
    else:
        flash(ACCESS_DENIED, 'text-danger')
        return redirect('/')


@ssl_required
@main_blueprint.route('/add_photo', methods=['GET', 'POST'])
def add_photo_view():
    if g.permission == 2:
        if request.method == 'POST':
            user_photos = request.get_json()
            avatar_photo_id = int(user_photos['avatar_photo_id']) + 1
            del user_photos['avatar_photo_id']
            for key, val in user_photos.items():
                image_string = val.split(',')[1]
                User.save_photos(str(int(key) + 1), image_string, session['id'])
                User.update_sexuality(session['id'], 5)
            User.set_avatar(avatar_photo_id, session['id'], session['login'])
            User.update_access_status(session['login'], 3)
            data = {'response': 'OK'}
            return jsonify(data)
        else:
            return render_template('add_photo.html')
    elif g.permission in (0, 1):
        flash(ACCESS_DENIED, 'text-danger')
        return redirect('/')
    else:
        return redirect(url_for('routes.cabinet_view'))


@ssl_required
@main_blueprint.route('/cabinet')
def cabinet_view():
    if g.permission < 1:
        flash(NOT_AUTH_MSG, 'text-warning')
        return redirect('/')
    connections_confirmed = User.get_all_connections(g.connection_ids, session['id'])
    connections_requested = User.get_all_connections(g.requested_connection_ids, session['id'])
    connections_unconfirmed = User.get_all_connections(g.unconfirmed_connection_ids, session['id'])
    connections_unconfirmed = list(filter(lambda x: not x.is_blocked, connections_unconfirmed))
    user_photos = User.get_photos_path(session['id'])
    user_data = User.get_profile_settings_from_db(session['id'])
    visit_history = VisitHistory.get_visit_history(session['id'])
    return render_template('cabinet.html', user_photos=user_photos,
                           user_data=user_data, connections_confirmed=connections_confirmed,
                           connections_requested=connections_requested,
                           connections_unconfirmed=connections_unconfirmed,
                           visit_history=visit_history)


@ssl_required
@main_blueprint.route('/profile/<login>', methods=['GET', 'POST'])
def other_profile_view(login):
    if g.permission < 1:
        flash(NOT_AUTH_MSG, 'text-warning')
        return redirect('/')
    if login == g.this_user.login:
        return redirect(url_for('routes.cabinet_view'))
    user = User(User.get_user_id(login), session['id'])
    VisitHistory.add_item(user.id, session['id'], session['login'], g.this_user.homepage, 'view')
    if request.method == 'POST':
        settings = NotificationSteeings(user.id)
        if request.form['submit'] == '1' and (user.connection_status == 0 or user.connection_status == 2) \
                and not user.is_blocked:
            VisitHistory.add_item(user.id, session['id'], session['login'], g.this_user.homepage, 'like')
            User.set_connection(session['id'], user.id)
            User.update_sexuality(user.id, 20)
            if User.connection_requested(user.id, session['id']):
                Notifications(user.id, session['login'], g.this_user.homepage, settings, 'likes_me_back', session['id'])
                Notifications(session['id'], user.login, user.homepage, settings, 'likes_me_back', user.id)
            else:
                Notifications(user.id, session['login'], g.this_user.homepage, settings, 'likes_me', session['id'])
        elif request.form['submit'] == '0' and (user.connection_status == 1 or user.connection_status == 3):
            VisitHistory.add_item(user.id, session['id'], session['login'], g.this_user.homepage, 'dislike')
            User.unset_connection(session['id'], user.id)
            User.update_sexuality(user.id, -20)
            Notifications(user.id, session['login'], g.this_user.homepage, settings, 'unlikes_me', session['id'])
        elif request.form['submit'] == '2' and not user.is_blocked:
            User.block_user(session['id'], user.id)
            if user.connection_status == 1 or user.connection_status == 3:
                User.update_sexuality(user.id, -20)
        elif request.form['submit'] == '3' and user.is_blocked:
            User.unblock_user(session['id'], user.id)
        user = User(User.get_user_id(login), session['id'])
    connected = User.connection_requested(session['id'], user.id)
    if Notifications.viewed_profile_notification_allowed(user.id, session['id']):
        settings = NotificationSteeings(user.id)
        Notifications(user.id, session['login'],
                      g.this_user.homepage, settings, 'viewed_my_profile', session['id'])
    return render_template('other_profile.html', user=user, connected=connected)


@ssl_required
@main_blueprint.route('/browse/', methods=['GET', 'POST'], defaults={'page': 1})
@main_blueprint.route('/browse/<int:page>', methods=['GET', 'POST'])
def brows_view(page):
    if g.permission < 1:
        flash(NOT_AUTH_MSG, 'text-warning')
        return redirect('/')
    form = FilterForm()
    research = Research(session['id'])
    if request.method == 'GET':
        research.sort('weight')
    if form.validate_on_submit():
        research.sort(form.order_by.data)
        if form.enable_distance.data:
            research.filter('distance', form.distance.data)
        if form.enable_sexuality.data:
            research.filter('sexuality', form.sexuality.data)
        if form.enable_age.data:
            research.filter('age', (form.age_from.data, form.age_to.data))
        if form.enable_interests.data:
            interests_list = User.get_interests_from_user(form.common_interests.data)
            research.filter('interests', interests_list)
    count = len(research.offers)
    pagination = Pagination(page, PER_PAGE, count)
    research.get_users_per_page(page, PER_PAGE)
    return render_template('browse.html', offers=research.offers, form=form, pagination=pagination)


@ssl_required
@main_blueprint.route('/search/', methods=['GET', 'POST'], defaults={'page': 1})
@main_blueprint.route('/search/<int:page>', methods=['GET', 'POST'])
def search_view(page):
    if g.permission < 1:
        flash(NOT_AUTH_MSG, 'text-warning')
        return redirect('/')
    form = FilterForm()
    offers = list()
    if form.validate_on_submit() and (form.enable_age.data or form.enable_sexuality.data or
                                      form.enable_distance.data or form.enable_interests.data):
        research = Research(session['id'])
        if form.enable_age.data:
            research.filter('age', (form.age_from.data, form.age_to.data))
        if form.enable_sexuality.data:
            research.filter('sexuality', form.sexuality.data)
        if form.enable_distance.data:
            research.filter('distance', form.distance.data)
        if form.enable_interests.data:
            interests_list = User.get_interests_from_user(form.common_interests.data)
            research.filter('interests', interests_list)
        research.sort(form.order_by.data)
        offers = research.offers
    # count = len(offers)
    # pagination = Pagination(page, PER_PAGE, count)
    # offers = offers[(page * PER_PAGE - PER_PAGE):(page * PER_PAGE)]
    return render_template('search.html', form=form, offers=offers)


@ssl_required
@main_blueprint.route('/chat_with')
def chat_with_view():
    if g.permission < 1:
        flash(NOT_AUTH_MSG, 'text-warning')
        return redirect('/')
    connections = User.get_all_connections(g.connection_ids, session['id'])
    for user in connections:
        user.unread_msgs = Chat.get_count_unread_from(user.id, session['id'])
    return render_template('chat_with.html', connections=connections)


@ssl_required
@main_blueprint.route('/chat/<login>')
def chat_view(login):
    if g.permission < 1:
        flash(NOT_AUTH_MSG, 'text-warning')
        return redirect('/')
    user = User(User.get_user_id(login), session['id'])
    chat = Chat.get_all(session['id'], user.id)
    Chat.set_as_read(session['id'], user.id)
    return render_template('chat.html', user=user, chat=chat, current_usr=None, get_user_by_id=Chat.get_user_by_id)


@ssl_required
@main_blueprint.route('/settings/notification', methods=['GET', 'POST'])
def settings_notification_view():
    if g.permission < 1:
        flash(NOT_AUTH_MSG, 'text-warning')
        return redirect('/')
    form = EditNotificationsForm()
    if request.method == 'POST':
        User.update_notifications_settings(session['id'], form.likes_me.data,
                                            form.unlikes_me.data, form.likes_me_back.data,
                                            form.viewed_my_profile.data, form.incoming_massage.data)
        flash(UPDATED, 'text-success')
    results = User.get_notification_settings(session['id'])
    form.likes_me.data = results['likes_me']
    form.unlikes_me.data = results['unlikes_me']
    form.likes_me_back.data = results['likes_me_back']
    form.viewed_my_profile.data = results['viewed_my_profile']
    form.incoming_massage.data = results['incoming_massage']
    return render_template('settings_notifications.html', form=form)


@ssl_required
@main_blueprint.route('/update_email/<login>')
def update_email_view(login):
    if User.accept_update_email(login):
        User.update_email(login)
        flash(EMAIL_CONFIRMED, 'text-success')
        User.log_out()
        return redirect('/')
    flash(ACCESS_DENIED, 'text-danger')
    return redirect('/')


@ssl_required
@main_blueprint.route('/settings/profile', methods=['GET', 'POST'])
def settings_profile_view():
    if g.permission < 1:
        flash(NOT_AUTH_MSG, 'text-warning')
        return redirect('/')
    form = EditProfileForm()
    if form.validate_on_submit():
        User.update_profile(session['id'], form.login.data, form.first_name.data, form.last_name.data,
                            form.birth_date.data, form.gender.data, form.preferences.data, form.biography.data,
                            form.city.data, form.show_location.data)
        if form.passwd.data != '':
            User.update_passwd(session['id'], form.passwd.data)
        if form.email.data != User.get_email(session['id']):
            flash(UPDATE_EMAIL, 'text-success')
            User.send_update_email_rwquest(form.email.data, session['login'], session['id'])
        if form.interests.data != ', '.join(User.get_interests_list(session['id'])):
            User.update_interesrs(session['id'], form.interests.data)
        flash(UPDATED, 'text-success')
    User.fill_edit_profile_form_from_db(form, session['id'])
    return render_template('settings_profile.html', form=form)


@ssl_required
@main_blueprint.route('/settings/photo', methods=['GET', 'POST'])
def settings_photo_view():
    if g.permission < 1:
        flash(NOT_AUTH_MSG, 'text-warning')
        return redirect('/')
    if request.method == 'POST':
        user_photos = request.get_json()
        avatar_photo_id = user_photos['avatar_photo_id']
        photos_to_del = user_photos['photos_to_del']
        del user_photos['avatar_photo_id']
        del user_photos['photos_to_del']
        for photo_to_del in photos_to_del:
            User.delete_photo(int(photo_to_del), session['id'])
            User.update_sexuality(session['id'], -5)
        for key, val in user_photos.items():
            User.update_access_status(session['login'], 3)
            image_string = val.split(',')[1]
            User.save_photos(key, image_string, session['id'])
            User.update_sexuality(session['id'], 5)
        User.set_avatar(avatar_photo_id, session['id'], session['login'])
        flash(UPDATED, 'text-success')
        data = {'response': 'OK'}
        return jsonify(data)
    avatar_path = User.get_avatar_path(session['id'])
    photos = User.get_photos_path(session['id'])
    grep_img_funct = User.grep_image_number
    return render_template('settings_photos.html', avatar_path=avatar_path, photos=photos, grep_img_funct=grep_img_funct)


@ssl_required
@main_blueprint.route('/map')
def map_view():
    if g.permission < 1:
        flash(NOT_AUTH_MSG, 'text-warning')
        return redirect('/')
    locations = User.get_all_lat_lng_login(session['id'])
    return render_template('map.html', locations=locations)


@ssl_required
@main_blueprint.route('/about')
def about_view():
    return render_template('about.html')


@ssl_required
@main_blueprint.route('/user_agreament')
def user_agreement_view():
    return render_template('user_agreament.html')


@ssl_required
@main_blueprint.route('/logout')
def logout():
    User.log_out()
    flash(LOGGED_OUT_MSG, 'text-success')
    return redirect('/')


@ssl_required
@main_blueprint.route('/delete/<login>')
def remove_user(login):
    if g.permission < 1:
        flash(NOT_AUTH_MSG, 'text-warning')
        return redirect('/')
    User.remove_user(login)
    flash(USER_REMOVED, 'text-warning')
    return redirect('/')


@ssl_required
@main_blueprint.route('/report_fake', methods=['POST'])
def report_fake_account():
    if g.permission < 1:
        flash(NOT_AUTH_MSG, 'text-warning')
        return redirect('/')
    fake_json = request.get_json()
    User.report_fake_account(fake_json['reported'], fake_json['fake'])
    return jsonify({'response': 'OK'})


@ssl_required
@main_blueprint.route('/connections')
def connections():
    if g.permission < 1:
        flash(NOT_AUTH_MSG, 'text-warning')
        return redirect('/')
    connections_confirmed = User.get_all_connections(g.connection_ids, session['id'])
    connections_requested = User.get_all_connections(g.requested_connection_ids, session['id'])
    connections_unconfirmed = User.get_all_connections(g.unconfirmed_connection_ids, session['id'])
    connections_blocked = User.get_all_connections(User.get_all_blocked_ids(session['id']), session['id'])
    return render_template('connections.html', connections_confirmed=connections_confirmed,
                           connections_requested=connections_requested,
                           connections_unconfirmed=connections_unconfirmed,
                           connections_blocked=connections_blocked)
