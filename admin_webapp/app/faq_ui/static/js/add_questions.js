$('.add_question').on('click', add_question);
$('.remove_question').on('click', remove_question);


// Adds question field to page
function add_question() {
    var n_new_question = parseInt($('#total_questions').val()) + 1;

    if (n_new_question < 11) {
        var new_input = '<input class="form-control" placeholder="Question ' + n_new_question + '" required type="text" style="margin-bottom:5px;" id="question_' + n_new_question + '" name="question_' + n_new_question + '"> ';
        $('#new_questions').append(new_input);

        $('#total_questions').val(n_new_question);
    }
}

// Removes question field from page
function remove_question() {
    var n_last_question = $('#total_questions').val();

    if (n_last_question > 5) {
        $('#question_' + n_last_question).remove();
        $('#total_questions').val(n_last_question - 1);
    }
}