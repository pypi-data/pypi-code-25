from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import json
import urllib
import sys
import time
import request
import socket

    
def get_links(searchtext):
	print('{} images founded'.format(len(links)))
	if len(links) >= num_requested:
		return None
	else:
		number_of_scrolls = 3
        # number_of_scrolls * 400 images will be opened in the browser
		url = "https://www.google.co.in/search?q="+searchtext+"&source=lnms&tbm=isch" 
		driver.get(url)

		headers = {}
		headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
		extensions = {"jpg", "jpeg", "png", "gif"}

		for _ in xrange(number_of_scrolls):
			for __ in xrange(10):
                # multiple scrolls needed to show all 400 images
				driver.execute_script("window.scrollBy(0, 1000000)")
				time.sleep(0.2)
            # to load next 400 images
			time.sleep(0.5)
			try:
				driver.find_element_by_xpath("""//*[@id="smb"]""").click()
			except Exception as e: 
				break

		imges = driver.find_elements_by_xpath('//div[contains(@class,"rg_meta")]')
		urls = [json.loads(x.get_attribute('innerHTML'))["ou"] for x in imges]
		if (len(urls)+len(links)) > num_requested:
			urls = urls[:(num_requested-len(links))]
		links.update(urls)      
		for url in urls:
				if url not in searched:
					searched.add(url)
					return get_links(url)

def download(downloaded_img_count,img_count):
	for url in links:
		img_url = url
		img_count += 1
		img_type = url.split('.')[-1]
		print "Downloading image", img_count, ": ", img_url
		extensions = ['png','jpg','gif']      
		try:
			if img_type not in extensions:
				img_type = "jpg"
			try:
				urllib.urlretrieve(img_url,download_path+'/'+searchtext.replace(" ", "_")+"/"+str(downloaded_img_count)+"."+img_type)
				print('success')
			except socket.error: 
				errno, errstr = sys.exc_info()[:2] 
				if errno == socket.timeout: 
					print "There was a timeout" 
				else: 
					print "There was some other socket error"
			downloaded_img_count += 1
		except Exception as e:
			print "Download failed:", e
	print "Total downloaded: ", downloaded_img_count, "/", img_count

def main():
	socket.setdefaulttimeout(30)

	reload(sys)
	sys.setdefaultencoding('utf8')

    # adding path to geckodriver to the OS environment variable
	os.environ["PATH"] += os.pathsep + os.getcwd()

	global download_path
	if not len(sys.argv) >= 4:
		download_path = "dataset/"
	else:
		download_path = sys.argv[3]
        
	print('Your download path is {}'.format(download_path))
    
	global links
	links = set()
	global searched
	searched = set()
    
	global driver
	driver = webdriver.Firefox()
	global searchtext
	searchtext = sys.argv[1]
	global num_requested
	num_requested = int(sys.argv[2])
    
                        
	if not os.path.exists(download_path + searchtext.replace(" ", "_")):
		os.makedirs(download_path + searchtext.replace(" ", "_"))
    
	get_links(searchtext)
	print('{} images found successfully'.format(len(links)))
	print('Now start downloading:')
    
	global downloaded_img_count, img_count
	downloaded_img_count = 0
	img_count = 0
	download(downloaded_img_count,img_count)
    
	driver.quit()    

if __name__ == "__main__":
	main()