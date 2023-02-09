$('.add_tag').on('click', add_tag);
$('.remove_tag').on('click', remove_tag);

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

    if (n_last_tag > 2) {
        $('#tag_' + n_last_tag).remove();
        $('#total_tags').val(n_last_tag - 1);
    }
}

