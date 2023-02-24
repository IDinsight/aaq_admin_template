$('.add_context').on('click', add_context);
$('.remove_context').on('click', remove_context);


// Adds context field to page
function add_context() {
    var n_new_context = parseInt($('#total_contexts').val()) + 1;

    if (n_new_context < 11) {
        var new_input = '<input class="form-control" placeholder="context ' + n_new_context + '"  type="text" style="margin-bottom:5px;" id="context_' + n_new_context + '" name="context_' + n_new_context + '"> ';
        $('#new_contexts').append(new_input);

        $('#total_contexts').val(n_new_context);
    }
}

// Removes context field from page
function remove_context() {
    var n_last_context = $('#total_contexts').val();

    if (n_last_context > 1) {
        $('#context_' + n_last_context).remove();
        $('#total_contexts').val(n_last_context - 1);
    }
}