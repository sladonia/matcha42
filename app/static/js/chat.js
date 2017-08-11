/**
 * Created by sladonia on 7/23/17.
 */

$(function () {

    // Add server-sent event
    var source = new EventSource('/chat_updater/' + other_user.id);
    source.onmessage = function (event) {
        var data = JSON.parse(event.data);

        for (var i = 0; i < data.length; i++) {
            ctreate_msg(other_user.login, data[i]['msg'], data[i]['date_time'], other_user.sm_avatar_path);

        }
    }

});

function not_empty(txt) {
    var pattern = /\w+/i;

    var n = txt.search(pattern);
    return n;
}

function new_msg() {
    var txt = document.getElementById('msg_body').value;

    if (not_empty(txt) == -1) {
        return;
    }

    var date_time = new Date();
    var formated_date = moment(date_time).format('MMM Do, HH:mm');

    ctreate_msg(this_user.login, txt, formated_date, this_user.sm_avatar_path);

    msg = {
        user_id: this_user.id,
        receiver_id: other_user.id,
        msg: txt
    };

    $.ajax({
        type: "POST",
        url: "/chat_add",
        data: JSON.stringify(msg),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            if (data['response'] === 'OK')
                console.log('msg_saved');
        },
        failure: function () {
            console.log('kill em all!');
        }
    });
    document.getElementById('msg_body').value = '';


}

function ctreate_msg(username, msg, date_time_str, avatar_url) {
    var msg_outer_div = document.createElement('DIV');
    msg_outer_div.classList.add('msg_container', 'row', 'ma-l-1', 'ma-r-1', 'ma-b-10');

    var avatar_div = document.createElement('DIV');
    avatar_div.classList.add('col-sm-2', 'col-xs-3', 'display_inline', 'text-center', 'pa-5');

    var avatar_img = document.createElement('IMG');
    avatar_img.classList.add('img-circle');
    avatar_img.setAttribute('src', avatar_url);
    avatar_img.setAttribute('width', '50');
    avatar_img.setAttribute('height', '50');

    var content_div = document.createElement('DIV');
    content_div.classList.add('col-sm-10', 'col-xs-9', 'display_inline', 'text-justify', 'pa-5');

    var date_time_p = document.createElement('P');
    date_time_p.classList.add('text-color-2', 'ma-0');
    date_time_p.textContent = date_time_str;

    var username_p = document.createElement('P');
    username_p.classList.add('text-color-2', 'ma-0');
    username_p.textContent = username;

    var text_p = document.createElement('span');
    username_p.classList.add('ma-0', 'ma-b-0', 'pa-0');
    text_p.textContent = msg;

    // adding children
    content_div.appendChild(date_time_p);
    content_div.appendChild(username_p);
    content_div.appendChild(text_p);

    avatar_div.appendChild(avatar_img);

    msg_outer_div.appendChild(avatar_div);
    msg_outer_div.appendChild(content_div);

    var chat_container = document.getElementById('chat_container');
    chat_container.appendChild(msg_outer_div);

    document.getElementById('footer').scrollIntoView();
}

$('#msg_body').on('keypress', function (e) {
   var key = e.keyCode;

   if (key == 13) {
       new_msg();
   }
});