tests: unittest

.PHONY: venv
venv:
	if [ ! -d "venv" ]; then python3 -m venv venv && venv/bin/pip3 install -r requirements.txt; fi

unittest:
	venv/bin/python3 -m unittest

container:
	podman run -it --name mosquitto-rcswitch -p 1883:1883 -p 9001:9001 eclipse-mosquitto

clean:
	podman rm -f mosquitto-rcswitch || true

