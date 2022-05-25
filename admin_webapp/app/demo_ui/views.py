import requests
from flask import current_app, flash, render_template

from ..auth import auth
from . import demo_ui
from .form_models import APICallDemoForm, CheckTagsForm

##############################################################################
# Demo core app endpoints
##############################################################################


@demo_ui.route("/apicall", methods=["GET", "POST"])
@auth.login_required
def demo_enduser():
    """
    Hosts and accepts APICallDemoForm, with single text input field

    On submission, sends POST with form content to MODEL_HOST:MODEL_PORT/inbound/check,
    formatted per API.
    """
    form = APICallDemoForm()
    top_matches = None
    scoring = None
    spell_corrected = None

    if form.validate_on_submit():
        api_call_body = {
            "text_to_match": form.submission_content.data,
            "return_scoring": "true",
        }
        endpoint = "%s://%s:%s/inbound/check" % (
            current_app.MODEL_PROTOCOL,
            current_app.MODEL_HOST,
            current_app.MODEL_PORT,
        )
        headers = {"Authorization": "Bearer %s" % current_app.INBOUND_CHECK_TOKEN}
        response = requests.post(endpoint, json=api_call_body, headers=headers)

        response_json = response.json()

        top_matches = response_json["top_responses"]
        scoring = response_json["scoring"]
        spell_corrected = scoring["spell_corrected"]
        del scoring["spell_corrected"]

    return render_template(
        "demo_apicall.html",
        form=form,
        top_matches=top_matches,
        scoring=scoring,
        spell_corrected=spell_corrected,
    )


def validate_tags(tag_list):
    """Validate FAQ tags by requesting core AAQ app"""
    api_call_body = {"tags_to_check": tag_list}
    bad_tags_endpoint = "%s://%s:%s/tools/validate-tags" % (
        current_app.MODEL_PROTOCOL,
        current_app.MODEL_HOST,
        current_app.MODEL_PORT,
    )
    headers = {"Authorization": "Bearer %s" % current_app.INBOUND_CHECK_TOKEN}
    bad_tags = requests.post(
        bad_tags_endpoint, json=api_call_body, headers=headers
    ).json()

    return bad_tags


@demo_ui.route("/check-new-faq-tags", methods=["GET", "POST"])
@auth.login_required
def check_new_faq_tags():
    """
    Hosts and accepts CheckTagsForm

    On submission, sends POST with form content to
    MODEL_HOST:MODEL_PORT/tools/check-new-tags, formatted per API.

    Prints results of checking new tags
    """
    form = CheckTagsForm()
    results = []
    tag_list = []

    if form.validate_on_submit():
        tag_list = [
            form.tag_1.data,
            form.tag_2.data,
            form.tag_3.data,
            form.tag_4.data,
            form.tag_5.data,
            form.tag_6.data,
            form.tag_7.data,
            form.tag_8.data,
            form.tag_9.data,
            form.tag_10.data,
        ]
        tag_list = list(filter(None, tag_list))

        # Step 1: check if all tags are valid
        bad_tags = validate_tags(tag_list)

        # If unsuccessful
        if len(bad_tags) > 0:
            flash(
                "The following tags are invalid: %s.\nPlease correct and resubmit."
                % str(bad_tags),
                "danger",
            )
        # Else, go to step 2:
        else:
            queries = [
                form.query_1.data,
                form.query_2.data,
                form.query_3.data,
                form.query_4.data,
                form.query_5.data,
            ]

            api_call_body = {"tags_to_check": tag_list, "queries_to_check": queries}
            headers = {"Authorization": "Bearer %s" % current_app.INBOUND_CHECK_TOKEN}

            endpoint = "%s://%s:%s/tools/check-new-tags" % (
                current_app.MODEL_PROTOCOL,
                current_app.MODEL_HOST,
                current_app.MODEL_PORT,
            )
            response = requests.post(endpoint, json=api_call_body, headers=headers)
            response_json = response.json()

            results = []
            for i in range(len(queries)):
                cur_matches = []
                matched_new_tags = False

                for match in response_json["top_matches_for_each_query"][i]:
                    # [title, score, [all_tags]]
                    if match[0] == "*** NEW TAGS MATCHED ***":
                        matched_new_tags = True

                    title_and_score = "%s / Score: %s" % (match[0], match[1])
                    tag_list_str = str(match[2])
                    cur_matches.append([title_and_score, tag_list_str])

                results.append(
                    [
                        "Query %d: %s" % (i + 1, queries[i]),
                        cur_matches,
                        matched_new_tags,
                    ]
                )

    return render_template(
        "check_new_faq_tags.html", form=form, results=results, tags=tag_list
    )
