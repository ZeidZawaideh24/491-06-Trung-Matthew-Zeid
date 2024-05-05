import logging

MEMBA_VERSION = "0.0.1"

def camel_to_snake(s):
	return ''.join(['_' + c.lower() if c.isupper() else c for c in s]).lstrip('_')

def remove_dupe_stub(seen, item):
	return item not in seen

def remove_dupe(arr, func=remove_dupe_stub):
	seen = []
	result = []
	for item in arr:
		if func(seen, item):
			seen.append(item)
			result.append(item)
	return result

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