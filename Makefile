virtualenv_run:
	virtualenv -p python3.5 virtualenv_run/
	virtualenv_run/bin/pip install -r requirements.txt
	virtualenv_run/bin/pip install ipython

create_tables: virtualenv_run
	virtualenv_run/bin/python -m database.order_history
