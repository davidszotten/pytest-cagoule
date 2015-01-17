noop:
	@true

.PHONY: noop

pytest:
	coverage run --source pytest_cagoule -m pytest --cagoule-capture tests
	coverage report --show-missing

flake8:
	flake8 pytest_cagoule tests

test: flake8 pytest
