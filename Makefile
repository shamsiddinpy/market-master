mig:
	python manage.py makemigrations
	python manage.py migrate


load:
	python manage.py loaddata region
	python manage.py loaddata district


flake:
	flake8