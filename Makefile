noop:
	@true

.PHONY: noop

pytest:
	coverage erase
	coverage run -p --source pytest_cagoule -m pytest tests
	coverage run -p --source pytest_cagoule -m pytest --cagoule-capture tests
	coverage combine
	coverage report --show-missing

flake8:
	flake8 pytest_cagoule tests

test: flake8 pytest
