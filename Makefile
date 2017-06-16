clean:
	rm -rf virtualenv_run/
	rm -rf .tox/

create_tables: virtualenv_run
	virtualenv_run/bin/python -m database.order_history
	virtualenv_run/bin/python -m database.price_history

dev_venv:
	virtualenv -p python3.5 virtualenv_run/
	virtualenv_run/bin/pip install -r requirements-dev.txt

test:
	tox

virtualenv_run:
	virtualenv -p python3.5 virtualenv_run/
	virtualenv_run/bin/pip install -r requirements.txt
