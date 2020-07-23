# -*- coding: utf-8 -*-
# by digiteng...06.2020, 07.2020,

from Components.AVSwitch import AVSwitch
from enigma import eEPGCache
from Components.config import config
from ServiceReference import ServiceReference
from Screens.MessageBox import MessageBox
import Tools.Notifications
import requests
from requests.utils import quote
import os, re, random
from PIL import Image
import socket
import xtra
from datetime import datetime


tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
epgcache = eEPGCache.getInstance()

pathLoc = xtra.pathLocation().location()

# open("/tmp/path","w").write(str(pathLoc))

def save():
	if config.plugins.xtraEvent.searchMOD.value == "Current Channel":
		currentChEpgs()
	if config.plugins.xtraEvent.searchMOD.value == "Bouquets":
		selBouquets()


def currentChEpgs():
	if os.path.exists(pathLoc + "events"):
		os.remove(pathLoc + "events")
	try:
		events = None
		import NavigationInstance
		ref = NavigationInstance.instance.getCurrentlyPlayingServiceReference().toString()
		try:
			events = epgcache.lookupEvent(['IBDCTSERNX', (ref, 1, -1, -1)])
			n = config.plugins.xtraEvent.searchNUMBER.value

			for i in range(int(n)):
				title = events[i][4]
				evntN = re.sub("([\(\[]).*?([\)\]])|(: odc.\d+)|(\d+: odc.\d+)|(\d+ odc.\d+)|(:)|( -(.*?).*)|(,)|!", "", title)
				evntNm = evntN.replace("Die ", "The ").replace("Das ", "The ").replace("und ", "and ").replace("LOS ", "The ").rstrip()
				open(pathLoc + "events", "a+").write("%s\n" %str(evntNm))

			intCheck()
			download()
		except:
			pass

	except:
		pass

def selBouquets():
	if os.path.exists(pathLoc + "events"):
		os.remove(pathLoc + "events")
		
	if os.path.exists(pathLoc + "bqts"):
		with open(pathLoc + "bqts", "r") as f:
			refs = f.readlines()
		
		nl=len(refs)
		for i in range(nl):
			ref = refs[i]
			try:
				events = epgcache.lookupEvent(['IBDCTSERNX', (ref, 1, -1, -1)])
				n = config.plugins.xtraEvent.searchNUMBER.value
				for i in range(int(n)):
					title = events[i][4]
					evntN = re.sub("([\(\[]).*?([\)\]])|(: odc.\d+)|(\d+: odc.\d+)|(\d+ odc.\d+)|(:)|( -(.*?).*)|(,)|!", "", title)
					evntNm = evntN.replace("Die ", "The ").replace("Das ", "The ").replace("und ", "and ").replace("LOS ", "The ").rstrip()
					open(pathLoc+"events","a+").write("%s\n"% str(evntNm))
			except:
				pass		
		intCheck()
		download()


def intCheck():
	try:
		socket.setdefaulttimeout(0.5)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
		return True
	except:
		return False

def download():
	now = datetime.now()
	dt = now.strftime("%d/%m/%Y %H:%M:%S")
	with open("/tmp/up_report", "a+") as f:
		f.write(str("start : {}\n".format(dt)))
	try:
		if intCheck():
			if config.plugins.xtraEvent.poster.value == True:
				if config.plugins.xtraEvent.tmdb.value == True:
					tmdb_Poster()
				if config.plugins.xtraEvent.tvdb.value == True:
					tvdb_Poster()
				if config.plugins.xtraEvent.omdb.value == True:
					omdb_Poster()
				if config.plugins.xtraEvent.maze.value == True:
					maze_Poster()
				if config.plugins.xtraEvent.fanart.value == True:
					fanart_Poster()

			if config.plugins.xtraEvent.banner.value == True:
				Banner()

			if config.plugins.xtraEvent.backdrop.value == True:
				if config.plugins.xtraEvent.tmdb.value == True:
					tmdb_backdrop()
				if config.plugins.xtraEvent.tvdb.value == True:
					tvdb_backdrop()
				if config.plugins.xtraEvent.fanart.value == True:
					fanart_backdrop()
				if config.plugins.xtraEvent.bing.value == True:
					bing_backdrop()

			if config.plugins.xtraEvent.info.value == True:
				infos()
		else:
			Tools.Notifications.AddNotification(MessageBox, _("NO INTERNET CONNECTION !.."), MessageBox.TYPE_INFO, timeout = 5)
			return
	except:
		return
# DOWNLOAD POSTERS ######################################################################################################


def tmdb_Poster():
	url = ""
	dwnldFile = ""
	year = ""
	try:
		if os.path.exists(pathLoc+"event-year"):
			with open(pathLoc+"event-year", "r") as f:
				year = f.read()
				
		if os.path.exists(pathLoc+"events"):
			with open(pathLoc+"events", "r") as f:
				titles = f.readlines()
			titles = list(dict.fromkeys(titles))
			n = len(titles)
			downloaded = 0
			for i in range(n):
				title = titles[i]
				title = title.strip()
				dwnldFile = pathLoc + "poster/{}.jpg".format(title)
				if not os.path.isfile(dwnldFile):				
					srch = "multi"
					lang = config.plugins.xtraEvent.searchLang.value
					url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}&language={}".format(srch, tmdb_api, quote(title), lang)
					if year != "0":
						url_tmdb += "&primary_release_year={}&year={}".format(year, year)
					try:
						poster = ""
						poster = requests.get(url_tmdb).json()['results'][0]['poster_path']
						p_size = config.plugins.xtraEvent.TMDBpostersize.value
						url = "https://image.tmdb.org/t/p/{}{}".format(p_size, poster)
						if poster != "":
							w = open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
							downloaded += 1
							w.close()
							
					except:
						pass
			now = datetime.now()
			dt = now.strftime("%d/%m/%Y %H:%M:%S")
			with open("/tmp/up_report", "a+") as f:
				f.write("tmdb_poster end : {} (downloaded : {})\n".format(dt, str(downloaded)))
		
	except:
		pass

def tvdb_Poster():
	url = ""
	dwnldFile = ""
	downloaded = None
	try:
		if os.path.exists(pathLoc+"events"):
			with open(pathLoc+"events", "r") as f:
				titles = f.readlines()

			titles = list(dict.fromkeys(titles))
			n = len(titles)
			downloaded = 0
			for i in range(n):
				title = titles[i]
				title = title.strip()
				dwnldFile = pathLoc + "poster/{}.jpg".format(title)
				if not os.path.isfile(dwnldFile):
					try:
						url_tvdb = "https://thetvdb.com/api/GetSeries.php?seriesname={}".format(quote(title))
						url_read = requests.get(url_tvdb).text
						series_id = re.findall('<seriesid>(.*?)</seriesid>', url_read)[0]
						if series_id:
							url_tvdb = "https://thetvdb.com/api/a99d487bb3426e5f3a60dea6d3d3c7ef/series/{}/en".format(series_id)
							url_read = requests.get(url_tvdb).text
							poster = re.findall('<poster>(.*?)</poster>', url_read)[0]

							url = "https://artworks.thetvdb.com/banners/{}".format(poster)
							if config.plugins.xtraEvent.TVDBpostersize.value == "thumbnail":
								url = url.replace(".jpg", "_t.jpg")

							w = open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
							downloaded += 1
							w.close()
								
					except:
						pass
			now = datetime.now()
			dt = now.strftime("%d/%m/%Y %H:%M:%S")
			with open("/tmp/up_report", "a+") as f:
				f.write("tvdb_poster end : {} (downloaded : {})\n".format(dt, str(downloaded)))
	except:
		pass

def omdb_Poster():
	url = ""
	dwnldFile = ""
	try:
		if os.path.exists(pathLoc+"events"):
			with open(pathLoc+"events", "r") as f:
				titles = f.readlines()

			titles = list(dict.fromkeys(titles))
			n = len(titles)
			downloaded = 0
			for i in range(n):
				title = titles[i]
				title = title.strip()
				dwnldFile = pathLoc + "poster/{}.jpg".format(title)
				if not os.path.isfile(dwnldFile):
					try:
						omdb_apis = ["6a4c9432", "a8834925", "550a7c40", "8ec53e6b"]
						omdb_api = random.sample(omdb_apis, 1)[0]
						url_omdb = 'https://www.omdbapi.com/?apikey=%s&t=%s' %(omdb_api, quote(title))
						url = requests.get(url_omdb).json()['Poster']
						if url:
							w = open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
							downloaded += 1
							w.close()
					except:
						pass

			now = datetime.now()
			dt = now.strftime("%d/%m/%Y %H:%M:%S")
			with open("/tmp/up_report", "a+") as f:
				f.write("omdb_poster end : {} (downloaded : {})\n".format(dt, str(downloaded)))
	except:
		pass

def maze_Poster():
	url = ""
	dwnldFile = ""
	try:
		if os.path.exists(pathLoc+"events"):
			with open(pathLoc+"events", "r") as f:
				titles = f.readlines()

			titles = list(dict.fromkeys(titles))
			n = len(titles)
			downloaded = 0
			for i in range(n):
				title = titles[i]
				title = title.strip()
				dwnldFile = pathLoc + "poster/{}.jpg".format(title)
				if not os.path.isfile(dwnldFile):		
					url_maze = "http://api.tvmaze.com/search/shows?q={}".format(quote(title))
					try:
						url = requests.get(url_maze).json()[0]['show']['image']['medium']

						w = open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
						downloaded += 1
						w.close()
					except:
						pass

			now = datetime.now()
			dt = now.strftime("%d/%m/%Y %H:%M:%S")
			with open("/tmp/up_report", "a+") as f:
				f.write("maze_poster end : {} (downloaded : {})\n".format(dt, str(downloaded)))
	except:
		return

def fanart_Poster():
	url = ""
	dwnldFile = ""
	try:
		if os.path.exists(pathLoc+"events"):
			with open(pathLoc+"events", "r") as f:
				titles = f.readlines()

			titles = list(dict.fromkeys(titles))
			n = len(titles)
			downloaded = 0
			for i in range(n):
				title = titles[i]
				title = title.strip()
				
				dwnldFile = pathLoc + "poster/{}.jpg".format(title)
				if not os.path.exists(dwnldFile):				
					try:
						srch = "multi"
						url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(srch, tmdb_api, quote(title))
						bnnr = requests.get(url_tmdb).json()
						tmdb_id = (bnnr['results'][0]['id'])
						if tmdb_id:
							m_type = (bnnr['results'][0]['media_type'])
							if m_type == "movie":
								m_type = (bnnr['results'][0]['media_type']) + "s"
							else:
								mm_type = m_type
							


							url_maze = "http://api.tvmaze.com/singlesearch/shows?q=%s" %quote(title)
							mj = requests.get(url_maze).json()
							tvdb_id = (mj['externals']['thetvdb'])
							if tvdb_id:
								try:
									url_fanart = "https://webservice.fanart.tv/v3/%s/%s?api_key=6d231536dea4318a88cb2520ce89473b" %(m_type, tvdb_id)
									fjs = requests.get(url_fanart).json()
									if fjs:
										if m_type == "movies":
											mm_type = (bnnr['results'][0]['media_type'])
										else:
											mm_type = m_type
										url = (fjs['tvposter'][0]['url'])
										if url:

											w = open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
											downloaded += 1
											w.close()
											
											scl = 1
											im = Image.open(dwnldFile)
											scl = config.plugins.xtraEvent.FANARTresize.value
											im1 = im.resize((im.size[0] // int(scl), im.size[1] // int(scl)), Image.ANTIALIAS)
											im1.save(dwnldFile)

								except:
									pass
				
					except:
						pass
			now = datetime.now()
			dt = now.strftime("%d/%m/%Y %H:%M:%S")
			with open("/tmp/up_report", "a+") as f:
				f.write("fanart_poster end : {} (downloaded : {})\n".format(dt, str(downloaded)))
	except:
		pass

# DOWNLOAD BANNERS ######################################################################################################

def Banner():
	url = ""
	dwnldFile = ""
	if os.path.exists(pathLoc+"events"):
		with open(pathLoc+"events", "r") as f:
			titles = f.readlines()

		titles = list(dict.fromkeys(titles))
		n = len(titles)
		downloaded = 0
		for i in range(n):
			title = titles[i]
			title = title.strip()
			dwnldFile = pathLoc + "banner/{}.jpg".format(title)
			if not os.path.isfile(dwnldFile):			
				try:
					url_tvdb = "https://thetvdb.com/api/GetSeries.php?seriesname=%s" %quote(title)
					url_read = requests.get(url_tvdb).text			
					series_id = re.findall('<seriesid>(.*?)</seriesid>', url_read, re.I)[0]
					if series_id:
						url = "https://artworks.thetvdb.com/banners/graphical/%s-g_t.jpg" %(series_id)
						if url:
							w = open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
							downloaded += 1
							w.close()


				except:
					try:
						dwnldFile = pathLoc + "banner/{}.jpg".format(title)
						if not os.path.isfile(dwnldFile):
							srch = "multi"
							url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(srch, tmdb_api, quote(title))
							bnnr = requests.get(url_tmdb).json()
							tmdb_id = (bnnr['results'][0]['id'])
							if tmdb_id:
								m_type = (bnnr['results'][0]['media_type'])
								if m_type == "movie":
									m_type = (bnnr['results'][0]['media_type']) + "s"
								else:
									mm_type = m_type
								url_fanart = "https://webservice.fanart.tv/v3/%s/%s?api_key=6d231536dea4318a88cb2520ce89473b" %(m_type, tmdb_id)
								fjs = requests.get(url_fanart).json()
								if fjs:
									if m_type == "movies":
										mm_type = (bnnr['results'][0]['media_type'])
									url = (fjs[mm_type+'banner'][0]['url'])
									if url:
										w = open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
										downloaded += 1
										w.close()


					except:
						try:
							dwnldFile = pathLoc + "banner/{}.jpg".format(title)
							if not os.path.isfile(dwnldFile):
								url_maze = "http://api.tvmaze.com/singlesearch/shows?q=%s" %(title)
								mj = requests.get(url_maze).json()
								poster = (mj['externals']['thetvdb'])
								if poster:
									url_tvdb = "https://thetvdb.com/api/GetSeries.php?seriesname=%s" %quote(title)
									url_read = requests.get(url_tvdb).text
									series_id = re.findall('<seriesid>(.*?)</seriesid>', url_read, re.I)[0]
									banner_img = re.findall('<banner>(.*?)</banner>', url_read, re.I)[0]
									if banner_img:
										url = "https://artworks.thetvdb.com%s" %(banner_img)

										w = open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
										w.close()

									if series_id:
										try:
											url_fanart = "https://webservice.fanart.tv/v3/%s/%s?api_key=6d231536dea4318a88cb2520ce89473b" %(m_type, series_id)
											fjs = requests.get(url_fanart).json()
											if fjs:
												if m_type == "movies":
													mm_type = (bnnr['results'][0]['media_type'])
												else:
													mm_type = m_type
												url = (fjs[mm_type+'banner'][0]['url'])

												if url:

													w = open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
													downloaded += 1
													w.close()

										except:
											pass
						except:
							pass
		now = datetime.now()
		dt = now.strftime("%d/%m/%Y %H:%M:%S")
		with open("/tmp/up_report", "a+") as f:
			f.write("banner end : {} (downloaded : {})\n".format(dt, str(downloaded)))
# DOWNLOAD BACKDROP ######################################################################################################

def tmdb_backdrop():
	url = ""
	dwnldFile = ""
	try:
		if os.path.exists(pathLoc+"events"):
			with open(pathLoc+"events", "r") as f:
				titles = f.readlines()

			titles = list(dict.fromkeys(titles))
			n = len(titles)
			downloaded = 0
			for i in range(n):
				title = titles[i]
				title = title.strip()
				dwnldFile = pathLoc + "backdrop/{}.jpg".format(title)
				if not os.path.isfile(dwnldFile):				
					srch = "multi"
					lang = config.plugins.xtraEvent.searchLang.value
					url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}&language={}".format(srch, tmdb_api, quote(title), lang)
					try:
						backdrop = requests.get(url_tmdb).json()['results'][0]['backdrop_path']
						if backdrop:
							backdrop_size = config.plugins.xtraEvent.TMDBbackdropsize.value
							url = "https://image.tmdb.org/t/p/{}{}".format(backdrop_size, backdrop)
						
							w = open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
							downloaded += 1
							w.close()
					except:
						pass
			now = datetime.now()
			dt = now.strftime("%d/%m/%Y %H:%M:%S")
			with open("/tmp/up_report", "a+") as f:
				f.write("tmdb_backdrop end : {} (downloaded : {})\n".format(dt, str(downloaded)))				
	except:
		pass

def tvdb_backdrop():
	url = ""
	dwnldFile = ""
	try:
		if os.path.exists(pathLoc+"events"):
			with open(pathLoc+"events", "r") as f:
				titles = f.readlines()

			titles = list(dict.fromkeys(titles))
			n = len(titles)
			downloaded = 0
			for i in range(n):
				title = titles[i]
				title = title.strip()
				dwnldFile = pathLoc + "backdrop/{}.jpg".format(title)
				if not os.path.isfile(dwnldFile):
					try:
						url_tvdb = "https://thetvdb.com/api/GetSeries.php?seriesname={}".format(quote(title))
						url_read = requests.get(url_tvdb).text
						series_id = re.findall('<seriesid>(.*?)</seriesid>', url_read)[0]
						if series_id:
							url_tvdb = "https://thetvdb.com/api/a99d487bb3426e5f3a60dea6d3d3c7ef/series/{}/en".format(series_id)
							url_read = requests.get(url_tvdb).text
							backdrop = re.findall('<fanart>(.*?)</fanart>', url_read)[0]
							if backdrop:
								url = "https://artworks.thetvdb.com/banners/{}".format(backdrop)
								if config.plugins.xtraEvent.TVDBbackdropsize.value == "thumbnail":
									url = url.replace(".jpg", "_t.jpg")


								w = open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
								downloaded += 1
								w.close()

					except:
						pass
			now = datetime.now()
			dt = now.strftime("%d/%m/%Y %H:%M:%S")
			with open("/tmp/up_report", "a+") as f:
				f.write("tvdb_backdrop end : {} (downloaded : {})\n".format(dt, str(downloaded)))
	except:
		pass

def fanart_backdrop():
	url = ""
	dwnldFile = ""
	try:
		if os.path.exists(pathLoc+"events"):
			with open(pathLoc+"events", "r") as f:
				titles = f.readlines()

			titles = list(dict.fromkeys(titles))
			n = len(titles)
			downloaded = 0
			for i in range(n):
				title = titles[i]
				title = title.strip()
				dwnldFile = pathLoc + "backdrop/{}.jpg".format(title)
				if not os.path.exists(dwnldFile):				
					try:
						srch = "multi"
						url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(srch, tmdb_api, quote(title))
						bnnr = requests.get(url_tmdb).json()
						tmdb_id = (bnnr['results'][0]['id'])
						if tmdb_id:
							m_type = (bnnr['results'][0]['media_type'])
							if m_type == "movie":
								m_type = (bnnr['results'][0]['media_type']) + "s"
							else:
								mm_type = m_type
							


							url_maze = "http://api.tvmaze.com/singlesearch/shows?q=%s" %quote(title)
							
							mj = requests.get(url_maze).json()
							tvdb_id = (mj['externals']['thetvdb'])
							if tvdb_id:
								try:
									
									url_fanart = "https://webservice.fanart.tv/v3/%s/%s?api_key=6d231536dea4318a88cb2520ce89473b" %(m_type, tvdb_id)
									fjs = requests.get(url_fanart).json()
									
									if fjs:
										if m_type == "movies":
											mm_type = (bnnr['results'][0]['media_type'])
										else:
											mm_type = m_type
										url = (fjs['tvthumb'][0]['url'])

										if url:

											w = open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
											downloaded += 1
											w.close()

								except:
									pass
					except:
						pass
			now = datetime.now()
			dt = now.strftime("%d/%m/%Y %H:%M:%S")
			with open("/tmp/up_report", "a+") as f:
				f.write("fanart_backdrop end : {} (downloaded : {})\n".format(dt, str(downloaded)))
	except:
		pass



def bing_backdrop():
	if os.path.exists(pathLoc+"events"):
		with open(pathLoc+"events", "r") as f:
			titles = f.readlines()

		titles = list(dict.fromkeys(titles))
		n = len(titles)
		downloaded = 0
		for i in range(n):
			title = titles[i]
			title = title.strip()
			dwnldFile = "{}backdrop/{}.jpg".format(pathLoc, title)
			if not os.path.isfile(dwnldFile):
				evntN = re.sub("([\(\[]).*?([\)\]])|(: odc.\d+)|(\d+: odc.\d+)|(\d+ odc.\d+)|(:)|( -(.*?).*)|(,)|!|(\|)", "", title.replace(" ", "+"))
				evntNm = evntN.replace("Die ", "The ").replace("Das ", "The ").replace("und ", "and ").replace("LOS ", "The ").rstrip()
				url="https://www.bing.com/search?q={}+poster+jpg".format(evntNm)
				headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
				ff = requests.get(url, stream=True, headers=headers).text

				try:
					p='ihk=\"\/th\?id=(.*?)&'
					f= re.findall(p, ff)
					url = "https://www.bing.com/th?id="+f[0]
					# dwnldFile = "{}backdrop/{}.jpg".format(pathLoc, title)
					w = open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
					downloaded += 1
					w.close()

				except:
					pass

		now = datetime.now()
		dt = now.strftime("%d/%m/%Y %H:%M:%S")
		with open("/tmp/up_report", "a+") as f:
			f.write("bing_backdrop end : {} (downloaded : {})\n".format(dt, str(downloaded)))


# DOWNLOAD INFOS ######################################################################################################

def infos():
	import json
	if os.path.exists(pathLoc+"events"):
		with open(pathLoc+"events", "r") as f:
			titles = f.readlines()

		titles = list(dict.fromkeys(titles))
		n = len(titles)
		downloaded = 0
		for i in range(n):
			title = titles[i]
			title = title.strip()
			info_files = pathLoc + "infos/{}.json".format(title)
			if not os.path.exists(info_files):
				try:
					url = 'https://www.bing.com/search?q={}+imdb'.format(title)
					headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
					ff = requests.get(url, stream=True, headers=headers).text
					rc = re.compile('https://www.imdb.com/title/tt(\d*)', re.DOTALL)
					imdb_id = "tt" + rc.search(ff).group(1)
					if imdb_id:
						omdb_apis = ["6a4c9432", "a8834925", "550a7c40", "8ec53e6b"]
						omdb_api = random.choice(omdb_apis)
						url_omdb = 'https://www.omdbapi.com/?apikey={}&i={}'.format(str(omdb_api), str(imdb_id))
						info_json = requests.get(url_omdb).json()

						w = open(info_files,"wb").write(json.dumps(info_json))
						downloaded += 1
						w.close()

				except:
					pass
		now = datetime.now()
		dt = now.strftime("%d/%m/%Y %H:%M:%S")
		with open("/tmp/up_report", "a+") as f:
			f.write("infos end : {} (downloaded : {})\n".format(dt, str(downloaded)))
