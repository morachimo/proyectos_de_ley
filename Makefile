.PHONY: help serve migrations stats coverage rebuild_index

help:
	@echo "help - see available commands"
	@echo "serve - runserver for development"
	@echo "migrations - prepare database for Django based on models"
	@echo "stats - get stats about the proyects in our database"
	@echo "coverage - run unittests and calculate coverage"
	@echo "rebuild_index - re-index our data using elasticsearch"

serve:
	cd proyectos_de_ley; python ./manage.py runserver --settings=proyectos_de_ley.settings.local

migrations:
	cd proyectos_de_ley; python ./manage.py makemigrations --settings=proyectos_de_ley.settings.local
	cd proyectos_de_ley; python ./manage.py migrate --settings=proyectos_de_ley.settings.local

stats:
	cd proyectos_de_ley; python ./manage.py create_stats --settings=proyectos_de_ley.settings.local

coverage:
	coverage run --source proyectos_de_ley proyectos_de_ley/manage.py test -v 2 pdl search_advanced \
	    seguimientos stats api --settings=proyectos_de_ley.settings.testing
	coverage report -m
	coverage html

rebuild_index:
	python proyectos_de_ley/manage.py rebuild_index --noinput --settings=proyectos_de_ley.settings.local
