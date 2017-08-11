$(function () {
    var location_dict = {};

    // Get geolocation
    function get_geolocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(get_location_by_coordinates, get_location_by_ip);
        } else {
            get_location_by_ip();
        }
    }

    function get_location_by_coordinates(position) {
        var latitude = position.coords.latitude;
        var longitude = position.coords.longitude;
        location_dict['method'] = 'coordinates';
        location_dict['latitude'] = latitude;
        location_dict['longitude'] = longitude;
        send_location(JSON.stringify(location_dict));
    }

    function get_location_by_ip() {
        location_dict['method'] = 'ip';
        send_location(JSON.stringify(location_dict));
    }

    function send_location(data_to_send) {
        $.ajax({
            type: "POST",
            url: "/geolocation",
            data: data_to_send,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                if (data['response'] === 'OK')
                    console.log('OK from server');
                else
                    console.log('KO from server')
            },
            failure: function () {
                console.log('failed from server');
            }
        });
    }
    get_geolocation();
});