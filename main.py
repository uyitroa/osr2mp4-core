import os
import time
from osr2mp4.osr2mp4 import Osr2mp4
from osr2mp4.VideoProcess.DiskUtils import convert_tomp4



def main():
	settings_all = Osr2mp4.settings_json()

	config = settings_all['config.json']
	config['osu! path'] = r''
	config['Skin path'] = r''
	config['Beatmap path'] = r''
	config['.osr path'] = r''
	config['Default skin path'] = r''
	config['Output path'] = 'out.avi'
	config['Width'] = 1280
	config['Height'] = 720
	config['FPS'] = 60
	config['Start time'] = 0 # 121
	config['End time'] = -1
	config['Video codec'] = 'XVID'
	config['Process'] = 1
	config['ffmpeg path'] = 'ffmpeg'

	pp = settings_all['ppsettings.json']
	settings = settings_all['settings.json']

	settings['Show background video'] = True
	settings['Resample'] = False
	settings['Blend frames'] = 5

	osr2mp4 = Osr2mp4(
		data = config,
		gameplaysettings = settings,
		ppsettings = pp,
		logtofile=True
	)

	osr2mp4.startall()
	osr2mp4.joinall()

	if os.name != 'nt':
		convert_tomp4(osr2mp4.settings)



if __name__ == "__main__":
	asdf = time.time()
	main()
	print("\nTotal time:", time.time() - asdf)
