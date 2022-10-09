import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import json


class UrlCrawl:

	def __init__(self, root_url):

		self.root_url=root_url
		params=urlparse(self.root_url)
		self.scheme=params.scheme
		#urls that was checked already
		self.visited_urls=set() 
		#urls referenced by other pages
		self.urls_referenced={}
		#final info about urls
		self.info={}

	#check if url is valid
	def is_valid(self, url): 

	    parsed = urlparse(url)
	    return bool(parsed.netloc) and bool(parsed.scheme)




	def get_all_website_links(self, url):
	    # not a valid URL
	    if not self.is_valid(url):
	    	print("Not valid URL")
	    	return
	    internal_urls = set() #internal
	    external_urls = set() #external
	    unique_urls= set() #unique subpages
	    self.visited_urls.add(url) #urls that was visited 

	    try:
		    # domain name of the URL without the protocol
		    domain_name = urlparse(url).netloc
		    soup = BeautifulSoup(requests.get(url, timeout=3).content, "html.parser")

		    #check if url was redirected
		    response= requests.get(url)
		    if response.history:
		        print("Request was redirected")
		        for resp in response.history:
		            print(resp.status_code, resp.url)
		        print("Final destination:")
		        print(response.status_code, response.url)
		        url=response.url
		        if url in self.visited_urls:
		        	return

		    # lik title
		    title=""
		    for ttl in soup.find_all('title'):
		       title+=ttl.get_text()

		    # search internal and external links on URL
		    for a_tag in soup.findAll("a"):

		        href = a_tag.attrs.get("href")

		        if href == "" or href is None:
		            # href empty tag
		            continue
		    
		        # join the URL if it's relative (not absolute link)
		        href = urljoin(url, href)
		        parsed_href = urlparse(href)
		        # remove URL GET parameters, URL fragments, etc.
		        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

	 			# not a valid URL
		        if not self.is_valid(href):
		            continue

		        # already in the set
		        if href in internal_urls:
		            continue

		        # external link
		        if domain_name not in href:
		            if href not in external_urls:
		                external_urls.add(href)
		            continue
		        # arleady checked url
		       	if href not in self.visited_urls:
		       		if href[:-1] not in self.visited_urls and href+"/" not in self.visited_urls:
		       			parts = urlparse(href)
		       			if parts.scheme==self.scheme:
		       				unique_urls.add(href)

		       	# add url that referenced by other pages
		        if href not in self.urls_referenced and url!=href:
		        	self.urls_referenced[href]=1
		        elif href not in self.urls_referenced and url==href:
		        	self.urls_referenced[href]=0
		        elif href in self.urls_referenced and url!=href and href not in internal_urls:
		        	self.urls_referenced[href]+=1

		        internal_urls.add(href)

		    self.info[url]=[title,len(internal_urls),len(external_urls)]
		    print(url)
		    #check  sublinks 
		    for i in unique_urls:
		    	self.get_all_website_links(i)

	    except requests.exceptions.Timeout:
	        print("Request timeout")
	    except requests.exceptions.TooManyRedirects:
	        print("Too many redirects")
	    except requests.exceptions.ConnectionError:
	    	print("Connection error")
	    except ConnectTimeout:
	    	print("Connection timeout")
	    except requests.exceptions.RequestException as e:
	        print("Error")
	        raise SystemExit(e)



root_url="https://crawler-test.com"

params=urlparse(root_url)
if params.path=="":
	root_url=root_url+"/"

#create URL Crawl object
crawl=UrlCrawl(root_url)
crawl.get_all_website_links(root_url)

#add number of times url was referenced by other pages
for i in crawl.info.keys():
	if i in crawl.urls_referenced:
		crawl.info[i].append(crawl.urls_referenced[i])

#write to json file 
with open(params.netloc+".json", "w") as outfile:
	for i in crawl.info:
		json.dump(i+": "+str(crawl.info[i]), outfile)
		outfile.write('\n')



