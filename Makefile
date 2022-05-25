#!make

# Load project config
include ./project_config.cfg
export

$(eval NAME=$(PROJECT_NAME))
$(eval PORT=9903)
$(eval VERSION=dev)

$(eval MODEL_PROTOCOL="http")
$(eval MODEL_HOST="host.docker.internal") # "host.docker.internal" on Mac, "127.0.0.1" on Linux
$(eval MODEL_PORT=9902)

$(eval UD_PROTOCOL="http")
$(eval UD_HOST="host.docker.internal") # "host.docker.internal" on Mac, "127.0.0.1" on Linux
$(eval UD_PORT=9904)

# Need to specify bash in order for conda activate to work.
SHELL=/bin/bash

# Note that the extra activate is needed to ensure that the activate floats env to the front of PATH
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

APP_SECRETS = INBOUND_CHECK_TOKEN READONLY_PASSWORD FULLACCESS_PASSWORD
UD_SECRETS = UD_INBOUND_CHECK_TOKEN
DB_SECRETS = PG_ENDPOINT PG_PORT PG_USERNAME PG_PASSWORD PG_DATABASE
SENTRY_CONFIG = SENTRY_DSN SENTRY_ENVIRONMENT SENTRY_TRACES_SAMPLE_RATE

cmd-exists-%:
	@hash $(*) > /dev/null 2>&1 || \
		(echo "ERROR: '$(*)' must be installed and available on your PATH."; exit 1)
guard-%:
	@if [ -z '${${*}}' ]; then echo 'ERROR: environment variable $* not set' && exit 1; fi

setup-dev: guard-PROJECT_CONDA_ENV cmd-exists-conda
	conda create --name $(PROJECT_CONDA_ENV) python==3.9 -y
	$(CONDA_ACTIVATE) $(PROJECT_CONDA_ENV); pip install --upgrade pip
	$(CONDA_ACTIVATE) $(PROJECT_CONDA_ENV); pip install -r requirements.txt --ignore-installed 
	$(CONDA_ACTIVATE) $(PROJECT_CONDA_ENV); pip install -r requirements_dev.txt --ignore-installed 
	$(CONDA_ACTIVATE) $(PROJECT_CONDA_ENV); pre-commit install

setup-secrets:
	@mkdir -p ./secrets/
	@if [ `ls -1 ./secrets | wc -l` -gt 0 ]; then \
		echo "One or more env file already exist"; exit 1; \
	fi
	@for env_var in $(APP_SECRETS) ; do \
		echo "$$env_var=" >> ./secrets/app_secrets.env ; \
	done
	@for env_var in $(DB_SECRETS) ; do \
		echo "$$env_var=" >> ./secrets/database_secrets.env ; \
	done
	@for env_var in $(UD_SECRETS) ; do \
		echo "$$env_var=" >> ./secrets/ud_secrets.env ; \
	done
	@for env_var in $(SENTRY_CONFIG) ; do \
		echo "$$env_var=" >> ./secrets/sentry_config.env ; \
	done

ci:
	isort --profile black --check admin_webapp
	black --check admin_webapp
	flake8 admin_webapp --count --ignore=E501,E203,E731,W503,E722 --show-source --statistics

image:
	# Build docker image
	cp ./requirements.txt ./admin_webapp/requirements.txt

	@docker build --rm \
			--build-arg NAME=$(NAME) \
			--build-arg PORT=$(PORT) \
			-t $(NAME):$(VERSION) \
			./admin_webapp
		
	rm -rf ./admin_webapp/requirements.txt

container:
	@docker container run \
		-p $(PORT):$(PORT) \
		-e MODEL_PROTOCOL=$(MODEL_PROTOCOL) \
		-e MODEL_HOST=$(MODEL_HOST) \
		-e MODEL_PORT=$(MODEL_PORT) \
		-e UD_PROTOCOL=$(UD_PROTOCOL) \
		-e UD_HOST=$(UD_HOST) \
		-e UD_PORT=$(UD_PORT) \
		--env-file ./secrets/app_secrets.env \
		--env-file ./secrets/database_secrets.env \
		--env-file ./secrets/sentry_config.env \
		--env-file ./secrets/ud_secrets.env \
		$(NAME):$(VERSION)
