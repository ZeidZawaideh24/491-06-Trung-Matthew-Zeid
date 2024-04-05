import logging

MEMBA_VERSION = "0.0.1"

def camel_to_snake(s):
	return ''.join(['_' + c.lower() if c.isupper() else c for c in s]).lstrip('_')

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