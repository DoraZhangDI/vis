#coding=utf-8
import types  
import urllib 
import urllib2  
import json  
import re 
import MySQLdb
import datetime
from bs4 import BeautifulSoup

import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

def loopUrl():
	looplen = 50
	for i in range(1,looplen):
		registerUrl(i)

def registerUrl(p):  
	try:  
		url = "http://www.zoudupai.com/services/service.php?m=index&a=share&width=190&p="+str(p)
		data = urllib2.urlopen(url).read()  
		return data  
	except Exception,e:  
		print e  
  
def praserJsonFile(jsonData):  
	rawjson = json.loads(jsonData)  
	contents = rawjson['result']	
	cs = []
	for c in contents:
		bookinfo = onebook(c)
		if bookinfo != '':
			cs.append(bookinfo)
	savedb(cs)

def onebook(r):
	baseurl = "http://www.zoudupai.com"

	sharedid = r['share_id']
	sharedts = r['create_time']
	sharedtime = datetime.datetime.utcfromtimestamp(float(sharedts)).strftime('%Y-%m-%d %H:%M:%S')
	content = r['content']
	title = gettitle(content)
	author = title
	booktype = r['album_title']
	bookPage = r['url']
	bookurl = getMobi(bookPage)
	bookpath = bookurl.split('/')[-1]
#	for k,v in locals().items():
#		print k,v
	if bookpath != '':
		if title != '':
			urllib.urlretrieve(baseurl+bookurl, '/Users/DoraZhang/ebooks/' + title + '.mobi')
		else:
			urllib.urlretrieve(baseurl+bookurl, '/Users/DoraZhang/ebooks/' + bookpath)
		if 'imgs' in r:
			imgurl = r['imgs'][0]['img'][1:]
			imgpath = bookpath.split('.')[0]+'.'+imgurl.split('.')[-1]
			urllib.urlretrieve(baseurl+imgurl, '/Users/DoraZhang/ebooks/imgs/' + imgpath)
		else:
			imgpath = ''
	
		return [sharedid,title,content,author,booktype,bookpath,imgpath,sharedtime]
	else:
		return ''
def savedb(ob):
	conn= MySQLdb.connect(
	        host='localhost',
	        port = 3306,
	        user='root',
	        passwd='root123',
	        db ='amazon',
			charset="utf8"
	        )
	cur = conn.cursor()
	for o in ob:	
		sql = "insert into ebooks(sharedid,title,content,author,booktype,bookpath,imgpath,sharedtime) values(%s, %s, %s, %s, %s, %s, %s, %s)"
#		print sql
		cur.execute(sql,o)
	
	
	#修改查询条件的数据
	#cur.execute("update student set class='3 year 1 class' where name = 'Tom'")
	
	#删除查询条件的数据
	#cur.execute("delete from student where age='9'")
	
	cur.close()
	conn.commit()
	conn.close()

def gettitle(c):
	if '《' in c:
		return c.split('》')[0].split('《')[-1]
	else:
		return ""

def getMobi(url):
	baseurl = "http://www.zoudupai.com"
	pageurl = baseurl + url
	print pageurl
	bs = BeautifulSoup(urllib2.urlopen(pageurl).read(),'html.parser')
	result = bs.select('div[class=shw_body]')
	bookurl = result[0].findAll('div', onclick = re.compile('annexDownload'))[0].get('onclick').split("'")[1]
	return bookurl

if __name__ == "__main__":  
#	data = registerUrl(5)  
#	praserJsonFile(data) 
	for i in range(6,47):
		print i
		data = registerUrl(i)  
		praserJsonFile(data) 
