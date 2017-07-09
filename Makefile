clean:
	rm -rf virtualenv_run/
	rm -rf .tox/

create_tables: virtualenv_run
	USE_DEV_DB=1 virtualenv_run/bin/python -m database.order_history
	USE_DEV_DB=1 virtualenv_run/bin/python -m database.price_history

dev_venv:
	virtualenv -p python3.5 virtualenv_run/
	virtualenv_run/bin/pip install -r requirements-dev.txt

test:
	tox

test_debug:
	USE_TEST_DB=1 virtualenv_run/bin/python -m pytest -s tests/ -v

virtualenv_run:
	virtualenv -p python3.5 virtualenv_run/
	virtualenv_run/bin/pip install -r requirements.txt

run_dev: virtualenv_run
	USE_DEV_DB=1 virtualenv_run/bin/python app.py

run_prod: virtualenv_run
	USE_PROD_DB=1 virtualenv_run/bin/python app.py

update_dev_data: virtualenv_run
	USE_DEV_DB=1 virtualenv_run/bin/python -m batch.google_price_history_fetcher

update_prod_data: virtualenv_run
	USE_PROD_DB=1 virtualenv_run/bin/python -m batch.google_price_history_fetcher
