# Praekelt MomConnect - Demo

## Overview

The Demo module is a Flask application that demos the FAQ matching model and Urgency Detection

To understand the Praekelt NLP system in better detail, please visit the praekelt_nlp_core repository.
- [IDinsight/praekelt_nlp_core](https://github.com/IDinsight/praekelt_nlp_core)

## Details

Demo is a containerized Flask server that connects to the model and allows sending demo messages, as well as checking tags.

You can view FAQs at {server address}:9903/demo/apicall in your web browser. You can check new tags at {server address}:9903/demo/check-new-faq-tags in your web browser.
You can check new urgency detection rules at {server address}:9903/demo/check-new-urgency-rules.

## Environment Setup

You need to:

1. Create a conda environment and install libraries in `requirements.txt` and `requirements_dev.txt`.
2. Enable pre-commit hooks.
3. Setup secrets.

or just use the Makefile.

### Using the Makefile

Running `make setup-dev` in the root of the repository will setup your development Conda environment. You will still need to update the two environment secrets files (app_secrets.env, sentry_config.env).

## Running Project

To run this project:

0. Setup environment as determined above.

1. Run `make image` from the praekelt_mc_demo folder.

2. Set up secrets. The secrets include:
    1. Environment variable `INBOUND_CHECK_TOKEN`, which is a bearer token required for any of the model endpoints. This should be obtained from the `praekelt_mc_core` module, and set in this module in `secrets/app_secrets.env` (since this module must authenticate itself to the model endpoint).
    2. Environment variable `UD_INBOUND_CHECK_TOKEN`, which is a bearer token required for any of the urgency detection endpoints. This should be obtained from the `praekelt_mc_ud` module, and set in this module in `secrets/app_secrets.env`
    3. Environment variables `DEMO_PASSWORD`, which is the password for user `demo` to access the FAQ tags and Urgency Rule checking tools. `DEMO_READONLY_PASSWORD` for user `demo_readonly` and `DEMO_FULLACCESS_PASSWORD` for user `demo_fullaccess` for the Urgency Rule table interface. (`demo` user and `demo_readonly` both have read-only access to the DB). These should be set in `secrets/app_secrets.env`. This can be anything you want, for example, outputs of `uuidgen`.
    4. Environment variables for database connections, `PG_ENDPOINT`, `PG_DATABASE`, `PG_USERNAME`, `PG_PASSWORD`, `PG_PORT`. These should be set in `secrets/db_secrets.env`.

3. Run the Docker container by calling `make container` from the `praekelt_mc_demo` folder.

## Publishing Project

The project should only be published formally via releases. Once a release (on GitHub) is tagged and published, a Github Actions script will create an image and push to GHCR with the release tag.

Do NOT build and push the images locally!

The instructions for Praekelt are found in docs/instructions_for_praekelt.md.
