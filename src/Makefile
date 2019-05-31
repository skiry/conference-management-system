run:
	-@clear
	-@python3 manage.py runserver

mkmigration:
	-@clear
	-@python3 manage.py makemigrations conferences

migrate:
	-@clear
	-@python3 manage.py migrate

shell:
	-@clear
	-@python3 manage.py shell

squash:
	-@clear
	-@rm db.sqlite3
	-@find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	-@find . -path "*/migrations/*.pyc"  -delete
	-@python3 manage.py makemigrations
	-@python3 manage.py migrate

.PHONY: run migrate mkmigration shell squash
