from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import time
import gc
from .pipelines import SaveToFilePipeline, SaveToMongoPipeline
from .entities import Follower,Following
from .settings import settings
from collections import deque

class Extractor(object):
	__prev_size, __size = None,None
	__driver = None
	__user = None
	__tweets = None
	__nFollowers = None
	__nFollowing = None
	__time = None
	__cantU = None
	__idUser = None
	__saveFile = None
	__userAuth = None
	__passAuth = None
	__users = None 
	__timeExtract = None
	__lang= None
	__timeout = None
	__data = None

	def __init__(self, user =settings.USER_AUTH, passwd = settings.PASS_AUTH,  
		cantU = settings.TOTAL_USERS_EXTRACT, timeExt = settings.TOTAL_EXTRACT_TIME, 
		lang = settings.LANGUAGE, timeout = settings.TIMEOUT, data = settings.DATA):
		"""__init__(user =settings.USER_AUTH, passwd = settings.PASS_AUTH,  
		cantU = settings.TOTAL_USERS_EXTRACT, timeExt = settings.TOTAL_EXTRACT_TIME, 
		lang = settings.LANGUAGE, timeout = settings.TIMEOUT, data = settings.DATA) 
           
        Crea el extractor de usuarios de Twitter

        @keyword user: el usuario a autenticar en Twitter.
        @keyword passwd: el contrasena a autenticar en Twitter.
        @keyword cantU: la cantidad de seguidores que va a obtener por usuario a extraer.
        @keyword timeExt: tiempo de espera que toma extrayendo durante la ejecuion de los metodos de extraccion, dado en milisegundos.
        @keyword lang: lenguaje en el que se va a manejar las paginas de Twitter.
        @keyword timeout: tiempo de espera por pagina de Twitter, dado en milisegundos.
        @keyword data: tipo de almacenamiento en el que se guardara la informacion a extraer.
         """ 
		self.__data = data
		self.__userAuth = user
		self.__passAuth = passwd
		self.__cantU = cantU
		self.__timeExtract = timeExt
		self.__lang = lang
		self.__timeout = timeout

	def setDatabase(self, host = settings.HOST, port = settings.PORT, database = settings.DATABASE, 
		collection_follower = settings.COLLECTION_FOLLOWER, collection_following = settings.COLLECTION_FOLLOWING):
		""" setDatabase(host = settings.HOST, port = settings.PORT, database = settings.DATABASE, 
		collection_follower = settings.COLLECTION_FOLLOWER, collection_following = settings.COLLECTION_FOLLOWING)

		Asigna el tipo de almacenamiento y si es una base de datos mongodb, se le asigna los parametros a esta

		@param host: la direccion ip o dominio en el que se encuentra el servidor mongodb, ignorar si es otro tipo de almacenamiento
		@param port: el puerto donde se escucha el servidor mongo, ignorar si es otro tipo de almacenamiento
		@param database: el nombre de la base de datos que va ser almacenado en mongo, ignorar si es otro tipo de almacenamiento
		@param collection_follower: el nombre de la coleccion que va a almacenar los followers, ignorar si es otro tipo de almacenamiento
		@param collection_following: el nombre de la coleccion que va a almacenar los followings, ignorar si es otro tipo de almacenamiento
		@throw NO almacenamiento encontrado: si no encuentra el tipo de almacenamiento dado
		"""
		if(self.__data == "SaveToFilePipeline"):
			self.__saveFile = SaveToFilePipeline()
		elif(self.__data == "SaveToMongoPipeline"):
			self.__saveFile = SaveToMongoPipeline(host = host, port = port, database = database, collection_follower = collection_follower, collection_following = collection_following)
		else :
			raise Exception("NO almacenamiento encontrado")


	def __getData(self, user):
		"""__getData(user)

		Obtiene la informacion de Twitter del usuario que le dan

		@param user: el usuario a extraer la informacion
		@throw Usuario no encontrado: si se intenta acceder a una pagina que no existe basado en el usuario
		"""
		self.__driver.get("https://twitter.com/{}".format(user))
		idi = self.__driver.find_elements_by_xpath("//div[@data-user-id][@data-screen-name='{}']".format(user))
		try:
			self.__idUser = idi[0].get_attribute("data-user-id")
		except Exception as e:
			raise Exception("Usuario no encontrado")
		time.sleep(self.__timeExtract)
		self.__driver.get("https://twitter.com/{}/followers".format(user))
		elementos = self.__driver.find_elements_by_class_name("ProfileNav-value")
		try:
			self.__nFollowing = int(elementos[1].get_attribute("data-count"))
		except:
			self.__nFollowing = 0
		try:
			self.__nFollowers = int(elementos[2].get_attribute("data-count"))
		except:
			self.__nFollowers = 0
		time.sleep(self.__timeExtract)
	
	def __move(self, elementos):
		"""__move(elementos)

		Logra desplazar la ventana hacia abajo para cargar mas usuarios

		@param elementos: la cantidad de elementos a tener en cuenta para continuar con el deslice hacia abajo
		@return True si se excedio el tiempo limite de espera por carga de usuarios, False de lo contrario
		"""
		count = 0
		while self.__prev_size < b and count < 2:
			wait = WebDriverWait(self.__driver, 10)
			height = self.__driver.execute_script("var h=document.body.scrollHeight; window.scrollTo(0, h); return h;")
			time.sleep(self.__timeExtract)
			try:
				a = wait.until(lambda drv: drv.execute_script("return document.documentElement.scrollHeight;") > height)
				break
			except:
				count +=1
				continue
		return count==2

	def __openConnection(self):
		"""__openConnection()

		Abre el browser Firefox para poder extraer datos y se identifica bajo la cuenta de Twitter antes dada

		"""
		self.__driver = webdriver.Firefox()
		self.__driver.set_page_load_timeout(self.__timeout)
		self.__driver.get("https://twitter.com/login?lang={}".format(self.__lang))
		time.sleep(self.__timeExtract)
		self.__prev_size, self.__size = 0,0
		username = self.__driver.find_element_by_xpath("//div[contains(@class,'clearfix field')]/input[contains(@name,'username')]")
		password = self.__driver.find_element_by_xpath("//div[contains(@class,'clearfix field')]/input[contains(@name,'password')]")
		username.send_keys(self.__userAuth)
		password.send_keys(self.__passAuth)
		self.__driver.find_element_by_xpath("//button[contains(., 'Log in')]").submit()
		time.sleep(self.__timeExtract)
		
	def __closeConnection(self):
		"""__closeConnection()

		Cierra el browser Firefox y logra limpiar memoria que dejo el browser

		"""
		if(self.__driver!=None):
			self.__driver.close()
		gc.collect()

	def __getFollowers(self, user):
		"""__getFollowers(user)

		Obtiene los followers del usuario dado y los almacena en el tunel de informacion

		@param user: el usuario a extraer su red de seguidores
		@return: devuelve una lista de todos los followers encontrados

		"""
		self.__driver.get("https://twitter.com/{}/followers".format(user))
		followers =  self.__driver.find_elements_by_class_name("ProfileCard")
		self.__size = self.__nFollowers
		self.__prev_size=0
		lista = []
		ifoll = []
		print("{} followers that were extracted...".format(len(followers)))
		while self.__prev_size < self.__nFollowers:
			if(len(followers)==0): break
			if(self.__cantU!=-1 and self.__prev_size >= self.__cantU): break
			for follower in followers[self.__prev_size:]:
				self.__prev_size+=1
				follow = Follower(self.__idUser, user, follower.get_attribute("data-user-id"), follower.get_attribute("data-screen-name"))
				ifoll.append(follow)
				lista.append(follow.nameFollower)
			if(self.__move(self.__nFollowers)): break
			time.sleep(self.__timeExtract)
			followers =  self.__driver.find_elements_by_class_name("ProfileCard")
			self.__size = len(followers)
			print("{} followers that were extracted...".format(len(followers)))
		self.__saveFile.process_items(ifoll)
		return lista
	
	def __getFollowing(self, user):
		"""__getFollowing(user)

		Obtiene los followings del usuario dado y los almacena en el tunel de informacion

		@param user: el usuario a extraer su red de seguidores
		@return: devuelve una lista de todos los followings encontrados

		"""
		self.__driver.get("https://twitter.com/{}/following".format(user))
		followings =  self.__driver.find_elements_by_class_name("ProfileCard")
		self.__size = len(followings)
		self.__prev_size = 0
		lista = []
		ifoll = []
		print("{} followings that were extracted...".format(len(followings)))
		while self.__prev_size < self.__nFollowing:
			if(len(followings)==0): break
			if(self.__cantU!=-1 and self.__prev_size >= self.__cantU): break
			for following in followings[self.__prev_size:]:
				self.__prev_size+=1
				follow = Following(self.__idUser, user, following.get_attribute("data-user-id"), following.get_attribute("data-screen-name"))
				ifoll.append(follow)
				lista.append(follow.nameFollowing)
			if(self.__move(self.__nFollowing)): break
			time.sleep(self.__timeExtract)
			followings =  self.__driver.find_elements_by_class_name("ProfileCard")
			self.__size = len(followings)
			print("{} followings that were extracted...".format(len(followings)))
		self.__saveFile.process_items(ifoll)
		return lista

	def getFollowers(self, user):
		"""getFollowers(user)

		Es la transaccion para poder obtener los followers de un usuario dado

		@param user: el usuario a extraer su red de seguidores
		@return: devuelve una lista de todos los followers encontrados

		"""
		lista = []
		try:
			self.__openConnection()
			self.__getData(user)
			lista=self.__getFollowers(user)
		except Exception as e:
			print(e)
			print("Hubo un error con el usuario {}".format(user))
		finally:
			self.__closeConnection()
		return lista
		
	def getFollowing(self, user):
		"""getFollowing(user)

		Es la transaccion para poder obtener los followings de un usuario dado

		@param user: el usuario a extraer su red de seguidores
		@return: devuelve una lista de todos los followings encontrados

		"""
		lista = []
		try:
			self.__openConnection()
			self.__getData(user)
			lista=self.__getFollowing(user)
		except Exception as e:
			print(e)
			print("Hubo un error con el usuario {}".format(user))
		finally:
			self.__closeConnection()
		return lista
		
	def getFollowersAndFollowing(self, user):
		"""getFollowersAndFollowing(user)

		Es la transaccion para poder obtener los followers y luego los followings de un usuario dado

		@param user: el usuario a extraer su red de seguidores
		@return: devuelve una lista de todos los followers y followings encontrados

		"""
		lista = []
		try:
			self.__openConnection()
			self.__getData(user)
			lista=self.__getFollowers(user)
			lista+=self.__getFollowing(user)
		except Exception as e:
			print(e)
			print("Hubo un error con el usuario {}".format(user))
		finally:
			self.__closeConnection()
		return lista

	def getFollowingAndFollowers(self, user):
		"""getFollowersAndFollowing(user)

		Es la transaccion para poder obtener los followings y luego los followers de un usuario dado

		@param user: el usuario a extraer su red de seguidores
		@return: devuelve una lista de todos los followers y followings encontrados

		"""
		lista = []
		try:
			self.__openConnection()
			self.__getData(user)
			lista=self.__getFollowing(user)
			lista+=self.__getFollowers(user)
		except Exception as e:
			print(e)
			print("Hubo un error con el usuario {}".format(user))
		finally:
			self.__closeConnection()
		return lista
