noop:
	@true

.PHONY: noop

pytest:
	pytest --cov=pytest_cagoule --cov-context=test
	coverage run -p --source pytest_cagoule -m pytest --cagoule-select=pytest_cagoule/select.py:14 tests
	coverage run -p --source pytest_cagoule -m pytest tests
	coverage combine
	coverage report --show-missing

flake8:
	flake8 pytest_cagoule tests

test: flake8 pytest
