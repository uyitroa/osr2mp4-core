import os
from osr2mp4.osr2mp4 import Osr2mp4
from PIL import ImageFont

def lambda_handler(event, context):
	os.system('cp /opt/bin/ffmpeg /tmp/ffmpeg')
	os.system('chmod 755 /tmp/ffmpeg')

	osr2mp4 = Osr2mp4(filedata="data.json", filesettings="settings.json", filepp="ppsettings.json", logtofile=False)
	osr2mp4.startaudio()
	osr2mp4.startvideo()
	#osr2mp4.joinall()
