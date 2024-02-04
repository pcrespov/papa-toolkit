.venv:
	@python --version
	@python -m venv .venv
	@echo "Type source .venv/bin/activate"

install: .venv
	.venv/bin/pip install -U pip setuptools wheel
	.venv/bin/pip install pre-commit
	.venv/bin/pre-commit install
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip list


install-dev: install
	.venv/bin/pip install -r requirements-dev.txt
	.venv/bin/pip list


clean:
	git clean -xdf

.PHONY: install-dev clean install
