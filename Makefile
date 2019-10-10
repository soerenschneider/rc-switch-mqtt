tests: unittest

.PHONY: venv
venv:
	if [ ! -d "venv" ]; then python3 -m venv venvi && venv/bin/pip3 install -r requirements.txt; fi

unittest:
	venv/bin/python3 -m unittest
