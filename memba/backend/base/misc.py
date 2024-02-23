MEMBA_VERSION = "0.0.1"

def log(*args, msg = "", **kwargs):
	res = []
	for arg in args:
		res.append(f"[{arg}]")
	for key in kwargs:
		res.append(f"[{key}={kwargs[key]}]")
	if len(msg) > 0:
		res.append(msg)
	print(" ".join(res))