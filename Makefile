# Create a virtual environment
venv:
	python -m venv venv

# Install the package and its dependencies in development mode
install-dev: venv
	venv/bin/pip install -e image-syncer

# Clean all artifacts using git clean
clean:
	git clean -xdf

# Default target
.PHONY: venv install-dev clean
