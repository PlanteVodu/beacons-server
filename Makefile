server: FORCE
	python3.7 api.py

test: FORCE
	python3.7 -m unittest discover

FORCE: ;
