venv:
	python -m venv .venv

install-dev: .venv
	.venv/bin/pip install -U pip setuptools wheel
	.venv/bin/pip install -e image-syncer

clean:
	git clean -xdf

.PHONY: .venv install-dev clean
