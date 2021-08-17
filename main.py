import os
import time
from osr2mp4.osr2mp4 import Osr2mp4



def main():
	settings_all = Osr2mp4.settings_json()

	config = settings_all['config.json']
	config['osu! path'] = r'D:\Games\osu!'
	config['Skin path'] = r'D:\Games\osu!\Skins\Aristia(Edit)+trail'
	config['Beatmap path'] = r'D:\Games\osu!\Songs\375648 S3RL - Bass Slut (Original Mix)'
	config['.osr path'] = r"D:\Games\osu!\Replays\FireRedz - S3RL - Bass Slut (Original Mix) [Fort's Light Insane] (2021-05-01) Osu.osr"
	config['Default skin path'] = r'D:\Projects\osr2mp4-core\osr2mp4\res\default'
	config['Output path'] = 'out.avi'
	config['Width'] = 640
	config['Height'] = 360
	config['FPS'] = 30
	config['Resample'] = False
	config['Start time'] = 68 # 121
	config['End time'] = 92
	config['Video codec'] = 'XVID'
	config['Process'] = 1
	config['ffmpeg path'] = 'ffmpeg'

	pp = settings_all['ppsettings.json']
	settings = settings_all['settings.json']
	strain = settings_all['strainsettings.json']

	osr2mp4 = Osr2mp4(
		data = config,
		gameplaysettings = settings,
		ppsettings = pp,
		strainsettings = strain
	)

	osr2mp4.startall()
	osr2mp4.joinall()



if __name__ == "__main__":
	asdf = time.time()
	main()
	print("\nTotal time:", time.time() - asdf)
