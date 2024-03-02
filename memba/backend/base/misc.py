import logging

MEMBA_VERSION = "0.0.1"

def log(
	*args,
	msg = "", level = logging.INFO,
	**kwargs
):
	res = []
	for arg in args:
		res.append(f"[{arg}]")
	for key in kwargs:
		res.append(f"[{kwargs[key]}]" if key == "_" else f"[{key}={kwargs[key]}]")
	if len(msg) > 0:
		res.append(msg)
	logging.log(level, " ".join(res))