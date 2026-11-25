VENV_PYTHON=./.venv/bin/python3

install:
	python3 -m venv .venv
	$(VENV_PYTHON) -m pip install -r ./requirements.txt

run:
	@if [ ! -f "$(VENV_PYTHON)" ]; then \
		echo "\033[31mRun 'make install' first.\033[0m"; \
		exit 1; \
	fi
	@if [ ! -n "$(CONF)" ]; then \
		echo "\033[33m"; \
		echo "\nYou did not specify a config;"; \
		echo "The program will run with the default config...\n"; \
		echo "To specify one use 'make run CONF=./maze.conf'\n"; \
		echo "\033[0m"; \
	fi
	@$(VENV_PYTHON) a_maze_ing.py $(CONF)


create-venv:

