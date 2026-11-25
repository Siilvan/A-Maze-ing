EXECUTABLE=./a_maze_ing.py
VENV_PYTHON=./.venv/bin/python3

install:
	python3 -m venv .venv
	$(VENV_PYTHON) -m pip install -r ./requirements.txt

_check-install:
	@if [ ! -f "$(VENV_PYTHON)" ]; then \
		echo "\033[31mRun 'make install' first.\033[0m"; \
		exit 1; \
	fi

debug: _check-install
	$(VENV_PYTHON) -m pdb $(EXECUTABLE)

run: _check-install
	@if [ ! -n "$(CONF)" ]; then \
		echo "\033[33m"; \
		echo "\nYou did not specify a config;"; \
		echo "The program will run with the default config...\n"; \
		echo "To specify one use 'make run CONF=./maze.conf'\n"; \
		echo "\033[0m"; \
	fi
	@$(VENV_PYTHON) $(EXECUTABLE) $(CONF)

lint: _check_install
	@if ! $(VENV_PYTHON) -c 'import flake8' 1>/dev/null 2>&1; then \
		echo '\033[33mFlake8 is not installed, installing it...\033[0m'; \
		$(VENV_PYTHON) -m pip install flake8 1>/dev/null; \
		echo "\033[32mDone!\033[0m"; \
	fi
	@if ! $(VENV_PYTHON) -c 'import mypy' 1>/dev/null 2>&1; then \
		echo '\033[33mMypy is not installed, installing it...\033[0m'; \
		$(VENV_PYTHON) -m pip install mypy 1>/dev/null; \
		echo "\033[32mDone!\033[0m"; \
	fi
	@echo "\n\033[34m==== Flake 8 ====\033[0m"
	@-$(VENV_PYTHON) -m flake8 \
		&& echo "\033[32mflake8 outstandingly done!\033[0m";
	@echo "\n\033[34m====  MY PY  ====\033[0m"
	@-$(VENV_PYTHON) -m mypy . \
		&& echo "\033[32mmypy outstandingly done!\033[0m";

clean:
	@pc_count=$$(find . -depth -name "__pycache__" | wc -l); \
	mp_count=$$(find . -depth -name ".mypy_cache" | wc -l); \
	find . -depth -name "__pycache__" -exec rm -rf {} ';'; \
	find . -depth -name ".mypy_cache" -exec rm -rf {} ';'; \
	if [ $$pc_count -gt 0 ]; then \
		echo "\033[32mRemoved $$pc_count __pycache__ directories\033[0m"; \
	fi; \
	if [ $$mp_count -gt 0 ]; then \
		echo "\033[32mRemoved $$mp_count mypy directories\033[0m"; \
	fi;
	@if [ -f "$(VENV_PYTHON)" ]; then \
		yes | $(VENV_PYTHON) -m pip uninstall mypy 1>/dev/null; \
		yes | $(VENV_PYTHON) -m pip uninstall flake8 1>/dev/null; \
		echo "\033[32m\nUninstalled flake8 and mypy.\033[0m"; \
	fi

.PHONY: _check_install run install debug
