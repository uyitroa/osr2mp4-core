from osr2mp4 import logger
from osr2mp4cv import getaudiocodec

a = getaudiocodec()

codec = {}
for x in a:
	codec[x.decode("utf-8")] = a[x].decode("utf-8")

for x in codec:
	logger.debug(f"{x}: {codec[x]}")
