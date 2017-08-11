$(function () {


    // Toggle menu
    $('#menu_btn').click(function (event) {


        $("#wrapper").toggleClass("toggled");
        if (!$("#wrapper").hasClass("toggled")) {
            $(this).css('backgroundColor', '#E84855');
            $(this).css('color', 'white');
        }
        else {
            $(this).css('backgroundColor', 'white');
            $(this).css('color', '#E84855');
        }
    });

    // Collapse menu on blur
    $('#menu_btn').blur(function (event) {
        if ($("#wrapper").hasClass("toggled")) {
            $("#wrapper").toggleClass("toggled");
            $(this).css('backgroundColor', '#E84855');
            $(this).css('color', 'white');
        }

    });


    // Add server-sent event
    var source = new EventSource('/updater');
    source.onmessage = function (event) {
        var data_dict = JSON.parse(event.data);
        notifications_count = data_dict['notifications_count'];
        msg_count = data_dict['msg_count'];
        if (notifications_count == 0) {
            $('#notification_badge').css('display', 'none');
        } else {
            notification_badge = $('#notification_badge');
            notification_badge.css('display', 'inline-block');
            notification_badge.text(notifications_count);
        }
        if (msg_count == 0) {
            $('#comment_badge').css('display', 'none');
        } else {
            comment_badge = $('#comment_badge');
            comment_badge.css('display', 'inline-block');
            comment_badge.text(msg_count);
        }
    }

    // Notification btn actions
    $('#notif_btn').click(function (event) {
        notif_box = $('#notification_box');

        if (notif_box.css('display') === 'none') {
            notif_box.css('display', 'block');
            $.ajax({
                type: "GET",
                url: "/get_notifications",
                data: {},
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (data) {
                    if (data['status'] === 'OK')
                        display_notifications(data['notif'])
                },
                failure: function () {
                    console.log('kill em all!');
                }
            });
        } else {
            $('.notif_msg_container').remove();
            notif_box.css('display', 'none');
        }
    });

    $('#notif_btn').blur(function (event) {

        var isHovered = $('#notification_box').is(":hover");

        if (!isHovered) {
            notif_box = $('#notification_box');
            $('.notif_msg_container').remove();
            notif_box.css('display', 'none');
        } else {
            $('#notif_btn').focus();
        }

    });


    function display_notifications(notif) {
        var notification_box = document.getElementById('notification_box');
        if (notif.length == 0) {
            notification_box.appendChild(create_tameplate(' ', 'You have no notifications yet. Be more active!', 1, '#/'));
            return;
        }

        for (var i = notif.length - 1; i >= 0; i--) {
            notification_box.appendChild(create_tameplate(notif[i]['date_time'], notif[i]['msg'], notif[i]['seen'], notif[i]['url']));
        }
    }


    function create_tameplate(date_time, msg, seen, url) {
        var link = document.createElement('A');
        link.classList.add('notif_link');
        link.setAttribute('href', url);


        var notif_msg_container = document.createElement('DIV');
        notif_msg_container.classList.add('notif_msg_container', 'pa-5');

        var header_div = document.createElement('DIV');
        header_div.classList.add('display_block');

        var date_div = document.createElement('DIV');
        date_div.classList.add('display_inline');
        date_div.setAttribute('style', 'color: #00bbc4');
        date_div.textContent = date_time;
        header_div.appendChild(date_div);


        if (seen == 0) {
            var new_badge = document.createElement('span');
            new_badge.classList.add('badge', 'float-right');
            new_badge.textContent = 'new';
            header_div.appendChild(new_badge);
        }

        var text = document.createElement('DIV');
        text.classList.add('display_block');
        text.textContent = msg;

        notif_msg_container.appendChild(header_div);
        notif_msg_container.appendChild(text);

        link.appendChild(notif_msg_container);

        return link;
    }
});


