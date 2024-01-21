.venv:
	@python --version
	@python -m venv .venv
	@echo "Type `source .venv/bin/activate`"

install-dev: .venv
	.venv/bin/pip install -U pip setuptools wheel
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip list

clean:
	git clean -xdf

.PHONY: .venv install-dev clean
