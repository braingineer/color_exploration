import MySQLdb as mysql
import cgi, cgitb


class BasicModule:
	def __init__(self, module=None, cssclass='', **args):
		self.cssclass = cssclass
		self.module = module
		self.wrapper = "<div class='{}'>{}</div>"
		
	def __str__(self):
		return self.getHTML()
	
	def __repr__(self):
		return self.getHTML()
	
	def set(self, module):
		self.module = module
	
	def getHTML(self):
		return self.wrapper.format(self.cssclass, self.module)
	
	def setCSSClass(self, cssclass):
		self.cssclass = cssclass

class Link(BasicModule):
	def __init__(self, name, link, cssclass='', **args):
		BasicModule.__init__(self, module="""<a href="{}">{}</a>""", cssclass=cssclass)
		self.name=name
		self.link=link

	def getHTML(self):
		return self.wrapper.format(self.cssclass, self.module.format(self.link, self.name))
		
	
class DIVBox(BasicModule):
	def __init__(self, module=None):
		BasicModule.__init__(self, module, "box")
		
class Image:
	def __init__(self, path, altText="An Image"):
		self.path=path
		self.altText = altText

	def set(self, path, altText="An Image"):
		self.path = path
		self.altText = altText
	
	def __repr__(self):
		return self.getHTML()

	def __str__(self):
		return self.getHTML()

	def getHTML(self):
		return """<img src="{}">{}</img>""".format(self.path, self.altText)


class IFrame:
	def __init__(self, page, **args): 
		pass
	#will get the iframe working.. but its not done yet
	
class TableModule:
	CENTER="margin-left: auto; margin-right:auto; "
	RIGHT="margin-left: auto; "
	LEFT="margin-right: auto; "
	TOP="vertical-align: top; "
	BOTTOM="vertical-align: bottom; "
	MIDDLE="vertical-align: middle; "

	def __init__(self, modules=None, width=None, **args):
		if modules and (isinstance(modules, tuple) or isinstance(modules, list)):
			self.cells = modules
		else:
			self.cells = []	
		self.borderwidth = 1
		self.width = width
		self.vAlign=None
		self.hAlign=None


	def setWidth(self, width):
		self.width = width
		
	def setBorder(self, borderwidth):
		self.borderwidth = borderwidth
		
	def add(self, **args):
		pass

	def setHorizontalAlignment(self, alignment):
		self.hAlign=alignment
	
	def setVerticalAlignment(self, alignment):
		self.vAlign=alignment

	def getStyles(self):
		t=""
		if self.hAlign:
			t+=self.hAlign
		if self.vAlign:
			t+=self.vAlign
		if len(t)>0:
			return " style='%s'" % t
		return ''
	
	def makeRow(self, cellContents, height=None):
		h='>'
		if height:
			h = " height='%s'>" % height
		return """<tr%s%s</tr>\n""" % (h, cellContents)

	def makeColumn(self, cellContents, cellWidth=None):
		if cellWidth:
			t = """<td width="%s" valign='top'>""" % cellWidth
		else:
			t = "<td valign='top'>"
		return """%s%s</td>\n""" % (t,cellContents)
	
	def getHTML(self):
		if self.width:
			t = """<table width="%s"%s>\n""" % (self.width, self.getStyles())
		else:
			t = "<table %s>" % self.getStyles()
		tableContents = self.makeContents()
		return """%s%s</table>""" % (t,tableContents)
	
	def __str__(self):
		return self.__repr__()
	
	def __repr__(self):
		return self.getHTML()

class HorizontalPanel(TableModule):
	def __init__(self, modules=None, width=None):
		TableModule.__init__(self, modules, width)
		self.widths = [None]*len(self.cells)


	def add(self, module, width=None):
		self.cells.append(module)
		self.widths.append(width)

	def setWidths(self, widths):
		if len(widths)==len(self.widths):
			self.widths = widths
			
	def makeContents(self):
		tableContents = ""
		for x in range(len(self.cells)):
			tableContents+=self.makeColumn(self.cells[x], self.widths[x])
		#tableContents = self.makeRow(tableContents)
		return self.makeRow(tableContents)	



class VerticalPanel(TableModule):
	def __init__(self, modules=None, width=None):	
		TableModule.__init__(self, modules, width)
		self.heights = []

	def add(self, module, height=None):
		self.cells.append(module)
		self.heights.append(height)

	def makeContents(self):
		tableContents = ""
		for x in range(len(self.cells)):
			tableContents+=self.makeRow(self.makeColumn(self.cells[x]), self.heights[x])
		return tableContents

class Base:
	def __init__(self):
		self.modules = []
		self.css = "nocss.css"
		self.title = "No Title"
	
	def setPageTitle(self, title):
		self.title = title

	def help(self):
		print """optional init arguments: modules (as array), css (string filename), title (string filename)
			\nFunctions include setCSS(cssfilename), add(module), printHTML()
			\nthe last will print the base which displays the page to the web browser"""
		
	def setCSS(self, css):
		self.css = css
		
	def add(self, module):
		self.modules.append(module)
		
	def printHTML(self):
		print """
		<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0top Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
		<html>
		<head>
		<title>%s</title>
		<link rel="stylesheet" href="%s">
		</head>
		<body>
		%s
		</body>
		</html>
		""" % (self.title, self.css, self.printModules())
	
	def printModules(self):
		#right now I am separating them in the Base by <br>. Can separate any other way.. or even have them all assume internal separations (aka they provide their own <br>)
		r=""
		for m in self.modules:
			r+="%s<br>" % m
		return r

def help():
	print "Modules included: VerticalPanel, HorizontalPanel, Base\nThey all have their own 'help' function as well\nThere is also a csstarterkit() present that will create a bare bones css file named 'starter.css'"


class worker:
		#note, this is just-above-mysql-level-worker.  the jobs can be abstracted into
		#domain specific task.. aka if you are going to have a consistent "select" or "insert"
		#then write a function that take the parameters and executes the corresponding
		#function with the correct sql query being passed in..
		#aka. always doing "select * from students where GPA>3.0" could be the function:
		#def getGoodStudents(self):
				#w = worker()
				#w.select("select * from students where GPA>3.0")
				#return w.fetchall()

		#the cost from worker creation isn't that much so keeping a consistnet worker is not absolutely necessary
		def __init__(self):
				self.db = mysql.connect("localhost", "compthink", "compthink", "blah")
				self.dbc = self.db.cursor() #our main worker guy

		def execute(self, query):
			self.dbc.execute(query)

		def insertAndCommit(self, query):
				#the insert and commit is for people who want to insert things.. 
				#no commit is needed for the select
				self.dbc.execute(query) #the execution.. 
				#self.dbc.commit()  #need commit otherwise execute won't "save" so to speak

		def select(self, query):
				#NOTE: returns the number of items found.  Use fetchall or fetchone to get results	  
				return self.dbc.execute(query)

		def fetchall(self):
				#returns all results of last query as a list
				return self.dbc.fetchall()

		def fetchone(self):
				#returns one result at a time from last query
				return self.dbc.fetchone()
			   
class template:
	def __init__(self):
		self.base = Base()
		v = VerticalPanel(width="500px")
		v.setHorizontalAlignment(v.CENTER)
		self.content = BasicModule()
		self.content.setCSSClass("templateBottom")
		
		header = HorizontalPanel(width="100%")
		header.add(BasicModule(module="<h3><center>#OccupyTaskManagement</center></h3>", cssclass="title"), "50%")
		header.add(self.makeMenu(), '70%')
		
		v.add(header, '30px')
		v.add(self.content)
		self.base.add(v)
		self.base.add(self.makeCopyright())
		
		self.base.setCSS("starter.css")
		self.base.setPageTitle("#OccupyTaskManagement")

	def makeCopyright(self):
		return BasicModule(module="<center><i>Copyright 2011 Karen Ambrose, Alex Anthony, Brian McMahan</i></center>", cssclass="copyright")

	def setContent(self, c):
		self.content.set(c)
	
	def makeMenu(self):
		m = BasicModule(cssclass="top_menu")
		h = HorizontalPanel()
		h.setHorizontalAlignment(h.CENTER)
		#menuHR = """<hr style='width:0.5px; color:000000; height:10px; padding: 0px;'>"""
		h.add(Link("Home", "index.py", cssclass="menu_item_leftend"))
		#h.add(menuHR)
		#h.add(Link("Projects", "view_projects.py", cssclass="menu_item_middle"))
		#h.add(menuHR)
		h.add(Link("Help!", "help.py", cssclass="menu_item_middle"))
		#h.add(menuHR)
		h.add(Link("Search", "search.py", cssclass="menu_item_rightend"))
		m.set(h)
		return m

	def printHTML(self):
		self.base.printHTML()

stockDivider = """<hr style='width: 1px; color: 000000; background-color: 000000; height: 400px;'>"""

def countMembers(memberList):
	members = memberList.split(",")
	return len(members)

def formatDueDate(date):
	if date=="None" or date==None:
		return "No Due Date"
	months={1:"January", 2:"February", 3:"March", 4:"April", 5:"May", 6:"June", 7:"July", 8:"August", 9:"September", 10:"October", 11:"November", 12:"December"}
	dateParts = str(date).split('-')
	try:
		x = eval(dateParts[1])
	except SyntaxError:
		x = eval(dateParts[1][1])
	return "{} {}, {}".format(months[x], dateParts[2], dateParts[0])

def countSubtasks(taskID):
	w = worker()
	a = w.select("select * from tasks where parent=%s" % taskID)
	return a

def formatPriority(priority):
	if priority>3:
		priority = 3
	priorityFormatter = {1:"Low", 2:"Medium", 3:"High"}
	return priorityFormatter[priority]


def makeLink(taskID, subtask):
	linkname="View this task"
	if subtask:
		linkname = "View this subtask"
	
	return Link(name="%s" % linkname, link="view_task.py?id=%s" % taskID)

def getID():
	form = cgi.FieldStorage()
	return form.getvalue('id')

def getTaskInfo(taskID):
	w = worker()
	w.select("select * from tasks where id=%s" % taskID)
	r = w.fetchone()
	if r==None:
		return ()
	return r

def getAllTasks():
	w = worker()
	w.select("select * from tasks")
	return w.fetchall()

def cssstarterkit():
	
	open("starter.css", 'w').write("""
	/* Starter CSS by Mike Cherim - http://green-beast.com */

* {
}

body {
}  

#wrapper {
}

h1, h2, h3, h4, h5, h6 {
}

p {
}

a {
text-decoration: underline;
}

a:hover, a:focus, a:active {
color: white;
}

a:focus, a:active {
}

img, a img {
}

small {
}

abbr, acronym {
}

blockquote {
}

cite {
}

em {
}

strong {
}

form {
}

fieldset {
}

legend {
}

label {
}

input {
}

select {
}

option {
}

textarea {
}

input:focus, select:focus, option:focus, textarea:focus {
}

#header {
}

#content {
}

#sidebar {
}

#navigation {
}

#footer {
}

.bold {
}

.italic {
}

.hidden {
}

.offset {
}

.highlight {
}

.tiny {
} 

.error {
}

.abbr {
}

""")
