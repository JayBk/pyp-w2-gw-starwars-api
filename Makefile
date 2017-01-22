.PHONY: test test-cov

TAG="\n\n\033[0;32m\#\#\# "
END=" \#\#\# \033[0m\n"

test:
	@echo $(TAG)Running tests$(END)
	PYTHONPATH=. py.test -s tests

test-client:
	@echo $(TAG)Running tests$(END)
	PYTHONPATH=. py.test -s tests/test_client.py
	
test-models:
	@echo $(TAG)Running tests$(END)
	PYTHONPATH=. py.test -s tests/test_models.py


test-cov:
	@echo $(TAG)Running tests with coverage$(END)
	PYTHONPATH=. py.test --cov=starwars_api tests

coverage:
	@echo $(TAG)Coverage report$(END)
	@PYTHONPATH=. coverage run --source=starwars_api $(shell which py.test) ./tests -q --tb=no >/dev/null; true
	@coverage report
