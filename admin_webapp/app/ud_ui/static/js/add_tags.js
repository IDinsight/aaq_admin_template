$('.add').on('click', add_tag);
$('.remove').on('click', remove_tag);
$('.addinclude').on('click', function () {add_rule_tag('include')});
$('.removeinclude').on('click', function () {remove_rule_tag('include')});
$('.addexclude').on('click', function () {add_rule_tag('exclude')});
$('.removeexclude').on('click', function () {remove_rule_tag('exclude')});


// Adds tag field to page
function add_tag() {
    var n_new_tag = parseInt($('#total_tags').val()) + 1;

    if (n_new_tag < 11) {
        var new_input = '<input class="form-control" placeholder="Tag ' + n_new_tag + '" required type="text" style="margin-bottom:5px;" id="tag_' + n_new_tag + '" name="tag_' + n_new_tag + '"> ';
        $('#new_tags').append(new_input);

        $('#total_tags').val(n_new_tag);
    }
}

// Removes tag field from page
function remove_tag() {
    var n_last_tag = $('#total_tags').val();

    if (n_last_tag > 1) {
        $('#tag_' + n_last_tag).remove();
        $('#total_tags').val(n_last_tag - 1);
    }
}

function add_rule_tag(rule_group) {
    var n_new_tag = parseInt($('#' + rule_group + '_total_tags').val()) + 1;

    if (n_new_tag < 11) {
        var new_input = '<input class="form-control" placeholder="Tag ' + n_new_tag + '" type="text" style="margin-bottom:5px;" id="' + rule_group + '_' + n_new_tag + '" name="' + rule_group + '_' + n_new_tag + '">'
        $('#' + rule_group + '_new_tags').append(new_input);

        $('#' + rule_group + '_total_tags').val(n_new_tag);
    }
}

// Removes tag field from page
function remove_rule_tag(rule_group) {
    var n_last_tag = $('#' + rule_group + '_total_tags').val();

    if (n_last_tag > 1) {
        $('#' + rule_group + '_' + n_last_tag).remove();
        $('#' + rule_group + '_total_tags').val(n_last_tag - 1);
    }
}
