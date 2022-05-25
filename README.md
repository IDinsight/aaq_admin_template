# Ask A Question (AAQ) Admin App Template

This is the readme for the AAQ Template Admin App repository. To start development on a new AAQ solution, clone or fork this and follow the setup instructions below.

Ensure to pull in new features from this repository regularly.

## What is the Admin App?

This is a containerized flask app that provides the following functionality:
* Demo AAQ service by sending test messages
* Manage FAQs
* Manage Urgency Detection rules
* Test new FAQ tags
* Test new Urgency Detection rules

You can view the app at {server address}:9903/ in your web browser.

This app calls endpoints in the [AAQ Core app](https://github.com/IDinsight/aaq_core_template) which needs to be running for the above functions to work.

## Setup

### Copy this code

Clone or fork this repository.

If you clone this, please setup a new repository for future commits and add this repository as another remote -  called `template`. This will allow you to pull in new changes made to this template. Here are the instructions on how to do this:

1. Clone this repo
```
git clone git@github.com:IDinsight/aaq_admin_template.git <project_name>
```

2. Change remote name to `template`
```
git remote rename origin template
```

3. Create a [new repo](https://github.com/organizations/IDinsight/repositories/new) in Github
4. Add it as remote for local repo

```
git remote add origin git@github.com:IDinsight/<project_name>.git
```
### Configure project details

The `project_config.cfg` in the root directory should be updated with your project details.

### Initialise

#### `make setup-dev`

This command does the following:

1. Creates a `conda` virtual environment
2. Installs dependencies from `requirements.txt` and `requirements_dev.txt`
3. Installs pre-commit hooks
4. Creates secrets files in `./secrets/`

### Enter details in secrets file

You should edit each of the files in `./secrets` and set the correct parameters.

### Other tasks

1. Setup auto deployment on EC2 (using webhooks or other)
2. Enable UD by passing `enable_ud=True` to `creat_app` in `aaq_admin_template/admin_webapp/flask_app.py`
2. Update this file! 
  - Remove irrelevant content (all the template text)
3. Setup other apps as necessary

## Running Project

To run this project:

1. Setup environment as determined above.
2. Set up secrets in the 3 files under `/secrets/`.
3. Run `make image` from the root folder.
4. Run the Docker container by calling `make container` from the root folder.
