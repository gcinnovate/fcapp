install:
	pip install -r requirements/development.txt

clean:
	chmod +x ${PWD}/scripts/clean.sh
	./scripts/clean.sh
