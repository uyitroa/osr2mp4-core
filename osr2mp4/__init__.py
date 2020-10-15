#import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import logging
import os
import sys

logger = logging.getLogger(__name__)
logger.propagate = False


def log_stream():
	if not logger.handlers:
		return sys.stdout
	handler = logger.handlers[0]
	if hasattr(handler, "stream"):
		return handler.stream
	return open(os.devnull, "w")
