function enable_funct(checkboxElem) {
    var to_enable = document.getElementById(checkboxElem.getAttribute('other_id'));
    if (checkboxElem.checked) {
        to_enable.disabled = false;
    } else {
        to_enable.disabled = true;
    }
    if (checkboxElem.getAttribute('other_id') == 'age_from') {
        var age_to = document.getElementById('age_to');
        if (checkboxElem.checked) {
            age_to.disabled = false;
        } else {
            age_to.disabled = true;
        }
    }
}

function enable_on_load() {
    var enablers_list = document.getElementsByClassName('enabler');
    for (var i = 0; i < enablers_list.length; i++) {
        enable_funct(enablers_list[i]);
    }
}

enable_on_load();