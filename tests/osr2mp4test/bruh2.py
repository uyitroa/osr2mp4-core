import os
import sys
import inspect


class afasdf: pass


fff = os.path.dirname(os.path.abspath(inspect.getsourcefile(afasdf)))
fff = os.path.relpath(fff)
if fff[-1] != "/" and fff[-1] != "\\":
	fff += "/"

sys.path.insert(0, fff + "../")
