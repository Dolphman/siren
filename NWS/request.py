from bs4 import BeautifulSoup
import requests


class report:							#Handles reports
	def __init__(self,id_url,gdata=True):

		self.id  = id_url
		self.meta = ["identifier","sender","sent","status","scope","note"]
		self.infolist = ["category","event","urgency","severity","certainty","effective","expires","senderName","headline","description","instruction"]
		if gdata:
			self.report_raw = requests.get(self.id).text
			self.soup = BeautifulSoup(self.report_raw)
			self.info = self.soup.alert.info

	def refresh(self):
		self.report_raw = requests.get(self.id).text
		self.soup = BeautifulSoup(self.report_raw)
		self.info = self.soup.info

	def get_meta(self):
		
		store = {}
		for y in self.meta:
			try:
				store = dict(store.items() + {y:self.soup.find(y).text}.items()) 
			except:
				store = dict(store.items() + {y:None}.items()) 
		return store

	def get_info(self):
		store = {}
		for y in self.infolist:
			try:
				store = dict(store.items() + {y:self.info.find(y).text}.items()) 
			except:
				store = dict(store.items() + {y:None}.items() )
		return store
		

class nws:

	def url_formatter(self): #URL FORMATER
		return ("https://alerts.weather.gov/cap/%s.atom" % (self.state))

	def error_handeling(self):
		self.no_warnings = (self.entries)[0].title.text == "There are no active watches, warnings or advisories"

	def __init__(self,state="us", gdata=True):
		self.state = state
		self.limit = 20
		if gdata:
			self.alert_raw = requests.get(self.url_formatter()).text
			self.soup = BeautifulSoup(self.alert_raw)
			self.entries = (self.soup.find_all("entry"))
			self.updated = self.soup.find("updated")
		self.cap = ["event", "effective","expires","status","msgtype","category","urgency","severity","areadesc","polygon","geocode"] 
		self.error_handeling()
	
	def refresh(self):                #Refreshes the data
		try:
			self.alert_raw = requests.get(self.url_formatter()).text
			self.soup = BeautifulSoup(self.alert_raw)
			self.entries = (self.soup.find_all("entry"))
			self.updated = self.soup.find("updated")
			self.error_handeling()
			return True
		except:
			return False

	def change_state(self,state):
		self.state = state #state if state in 

	def load_entry(self, entry):	#Loads entries
		if not type(entry) is list:
			self.entries = [entry]
		else:
			self.entries = entry

	def get_summary(self, limit=None):
		if self.no_warnings :
			return None
		
		def summary_gen(limit): #generator for summary 
		
			for x in self.entries:
				yield {"summary":x.summary.text}
				limit = limit - 1 if limit is not None else None 
				if type(limit) is int:
					if limit == 0:
						break

		limit = self.limit if limit is None else limit
		return list(summary_gen(limit))


	def get_title(self, limit=None):
		if self.no_warnings :
			return None

		def title_gen(limit):  #Generator

			for x in self.entries:
				yield {"title":x.title.text}
				if type(limit) is int:
					if limit == 0:
						break

		limit = self.limit if limit is None else limit
		return list(title_gen(limit))

	def get_id(self, limit=None):
		if self.no_warnings :
			return None

		def id_gen(limit):				#id generator
			for x in self.entries:
				yield {"id":x.id.text}
				limit = limit - 1 if limit is not None else None 
				if type(limit) is int:
					if limit == 0:
						break
			limit = self.limit if limit is None else limit

		return list(id_gen(limit))


	def get_cap(self, limit=None):   #

		if self.no_warnings :
			return None

		def cap_gen(limit):    #Generator for cap content

			store = {}
			for x in self.entries:
				for y in self.cap:
					store = dict(store.items() + {y:x.find("cap:"+y).text}.items()) 
				yield([store])
				limit = limit - 1 if limit is not None else None 
				if type(limit) is int:
					if limit == 0:
						break

		limit = self.limit if limit is None else limit
		lst = []
		for x in cap_gen(limit):
			lst = lst + list(x)
		return lst




