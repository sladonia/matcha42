$(function () {
    resize_connections_photos();
    $(window).resize(function () {
        resize_connections_photos();
    });

    function resize_connections_photos() {
        var container = $('#connections_container');
        var connection_photos = $('.connections_photos');
        if (connection_photos && container.hasClass('in')) {
            connection_photos.css('height', connection_photos[0].clientWidth * 1.2 + 'px');
        }
    }
});