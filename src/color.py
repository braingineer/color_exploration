#!/usr/bin/python
#

import cgi 
import operator
import math 
import os
os.environ['HOME']='/var/www/dev' #hopefully fix for http://stackoverflow.com/questions/2561379/matplotlib-and-wsgi-mod-python-not-working-on-apache
# debugging info on
import cgitb
#import mysql.connector
cgitb.enable()
import MySQLdb as mysqldb
import matplotlib
matplotlib.use("Agg")
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

global image_dir, images_rel_path, script_rel_path
image_dir = "/var/www/images/" #ending slash is important here
scripts_rel_path = "/scripts/"
images_rel_path="/images/"
 
#This class is primarily an API into the javascript port of the processing programming language
#it's mostly hacky because I make what I need and haven't systematically made a good API
class processing_api:
    def __init__(self):
        self.intro = """
            <canvas id="canvas1" width="300" height="300"></canvas>
            <script id="script1" type="text/javascript">
        """
        self.outro="""
                var canvas=document.getElementById("canvas1");
                var p = new Processing(canvas, sketchProc);
            </script>
            """
        self.inner_func_start="function sketchProc(processing) { processing.size(300,300); processing.draw = function() {" 
        self.inner_func_end="}; }"
        self.objects = []
        
    def add_square(self,r,g,b,size_w=100,size_h=100,pos_x=0,pos_y=0):
        self.objects.append("processing.fill(%s,%s,%s); processing.rect(%s,%s,%s,%s)" % (r,g,b,pos_x,pos_y,size_w,size_h))
        
    def make_one_color_showcase(self, r,g,b,size_w=300,size_h=300):
        ret = self.intro+self.inner_func_start
        ret+="processing.fill(%s,%s,%s); processing.rect(0, 0, %s, %s);" % (r,g,b,size_w,size_h)
        return ret+self.inner_func_end+self.outro
    
    def make_multiple_color_showcase(self, colors):
        width=max_width=0
        height=0
        per_row=6
        squares=""
        x=0
        for color in colors:
            x+=1
            
            squares+="""processing.fill(%s,%s,%s); processing.rect(%s,%s,%s,%s); processing.fill(0,0,0); processing.text('%s', %s, %s);
            """ % (color[0], color[1], color[2], width, height, 100, 100, '%s,%s,%s' % (color[0], color[1], color[2]), width+5, height+50)
            if x%per_row==0:
                print "<br>",x, height, width, x%per_row, "<br>"
                height+=100
                max_width=width+100
                width=0
            else:
                width+=100
        if max_width>width:
            width=max_width
        height+=100
        return """ <canvas id="canvas5" width="%s" height="%s"></canvas>
                <script id="script5" type="text/javascript">
                function sketchProc(processing) { processing.size(%s,%s); processing.draw = function() {
                    %s
                    }; }
                var canvas=document.getElementById("canvas5");
                var p = new Processing(canvas, sketchProc);
                </script>
            """ % (width, height,width,height, squares)
        
    def get_code(self):
        ret = self.intro+self.inner_func_start
        for obj in self.objects:
            ret+=obj
        return ret+self.inner_func_end+self.outro

    
    def _rgb_cube_helper(self,r,g,b,r_range, g_range, b_range):
        r_m=g_m=b_m=0
        r_p=g_p=b_p=255
        if (r-r_range>=0): r_m=r-r_range
        if (r+r_range<=255): r_p=r+r_range
            
        if (g-g_range>=0): g_m=g-g_range
        if (g+g_range<=255): g_p=g+g_range
            
        if (b-b_range>=0): b_m=b-b_range
        if (b+b_range<=255): b_p=b+b_range
        return [int(r_m),int(r_p),int(g_m),int(g_p),int(b_m),int(b_p)]
    

    
    def make_and_get_cube_code(self, r,g,b,r_range, g_range, b_range):
        #return self.make_and_get_cube_code_first(r, g, b, range)
        return self.make_and_get_cube_code_second(r, g, b,r_range, g_range, b_range)
    
    def make_and_get_cube_code_first(self,r,g,b,rgb_range):
        #http://processing.org/learning/topics/rgbcube.html
        #NOTE:
        #beginShape(QUADS) means it is accepting 4 vertexes defining sides of a shape
        #colors range smoothly from ther corners
        #for us, r=x, g=y, b=z, corners = {r,g,b}+-range
        #in the space, coords range from -1 to 1
        #at the -1, it is {r,g,b}-range; at 1 it is +range
        stock = "fill(%s,%s,%s); vertex(%s,%s,%s);\n"
        [r_m,r_p,g_m,g_p,b_m,b_p] = self._rgb_cube_helper(r, g, b, rgb_range, rgb_range, rgb_range)
            
        c_1=stock % (r_m, g_m, b_m,-1,-1,-1)
        c_2=stock % (r_m, g_m, b_m,-1, 1,-1)
        c_3=stock % (r_p, g_p, b_m, 1, 1,-1)
        c_4=stock % (r_p, g_m, b_m, 1,-1,-1)
        c_5=stock % (r_m, g_m, b_p,-1,-1, 1)
        c_6=stock % (r_m, g_p, b_p,-1, 1, 1)
        c_7=stock % (r_p, g_p, b_p, 1, 1, 1)
        c_8=stock % (r_p, g_m, b_p, 1,-1, 1)
        
        q_1 = "%s %s %s %s" % (c_6, c_7, c_8, c_5)
        q_2 = "%s %s %s %s" % (c_7, c_3, c_4, c_8)
        q_3 = "%s %s %s %s" % (c_3, c_8, c_1, c_4)
        q_4 = "%s %s %s %s" % (c_2, c_6, c_5, c_1)
        q_5 = "%s %s %s %s" % (c_2, c_3, c_7, c_6)
        q_6 = "%s %s %s %s" % (c_1, c_4, c_8, c_5)
        return """
        <canvas id="canvas1" width="1000" height="500"></canvas>
        <script src="processing.js"></script>
        <script type="text/processing" data-processing-target="canvas1">
            void setup() {
                size(1000,500,P3D); 
                noStroke(); 
                colorMode(RGB,255);
            }
            void draw()  {
                  background(0.5);
                  
                  pushMatrix(); 
                    
                  translate(width/2, height/2, -30); 
                  if (mousePressed) {
                      newXmag = mouseX/float(width) * TWO_PI;
                      newYmag = mouseY/float(height) * TWO_PI;
                      
                      float diff = xmag-newXmag;
                      if (abs(diff) >  0.01) { xmag -= diff/4.0; }
                      
                      diff = ymag-newYmag;
                      if (abs(diff) >  0.01) { ymag -= diff/4.0; }
                      
                      
                      rotateX(-ymag); 
                      rotateY(-xmag); 
                  }
                  scale(90);
                  beginShape(QUADS);
                
                  %s \n 
                  %s \n 
                  %s \n 
                  %s \n 
                  %s \n 
                  %s
                
                  endShape();
                  
                  popMatrix(); 
                }
            </script>
        
        """  % (q_1, q_2, q_3, q_4, q_5, q_6)
        

    def make_and_get_cube_code_second(self,r,g,b,r_range, g_range, b_range):
        #http://processing.org/learning/topics/rgbcube.html
        #NOTE:
        #beginShape(QUADS) means it is accepting 4 vertexes defining sides of a shape
        #colors range smoothly from ther corners
        #for us, r=x, g=y, b=z, corners = {r,g,b}+-range
        #in the space, coords range from -1 to 1
        #at the -1, it is {r,g,b}-range; at 1 it is +range
        #second note, for the color name display, the 3d cube uses the variance as the range
        stock = "processing.fill(%s,%s,%s); processing.vertex(%s,%s,%s);\n"
        [r_m,r_p,g_m,g_p,b_m,b_p] = self._rgb_cube_helper(r, g, b, r_range, g_range, b_range)
        [r_range, g_range, b_range] = math_helper.normalize([r_range, g_range, b_range])
            
        c_1=stock % (r_m, g_m, b_m,-r_range,-g_range,-b_range)
        c_2=stock % (r_m, g_m, b_m,-r_range, g_range,-b_range)
        c_3=stock % (r_p, g_p, b_m, r_range, g_range,-b_range)
        c_4=stock % (r_p, g_m, b_m, r_range,-g_range,-b_range)
        c_5=stock % (r_m, g_m, b_p,-r_range,-g_range, b_range)
        c_6=stock % (r_m, g_p, b_p,-r_range, g_range, b_range)
        c_7=stock % (r_p, g_p, b_p, r_range, g_range, b_range)
        c_8=stock % (r_p, g_m, b_p, r_range,-g_range, b_range)
        
        q_1 = "%s %s %s %s" % (c_6, c_7, c_8, c_5)
        q_2 = "%s %s %s %s" % (c_7, c_3, c_4, c_8)
        q_3 = "%s %s %s %s" % (c_3, c_2, c_1, c_4)
        q_4 = "%s %s %s %s" % (c_2, c_6, c_5, c_1)
        q_5 = "%s %s %s %s" % (c_2, c_3, c_7, c_6)
        q_6 = "%s %s %s %s" % (c_1, c_4, c_8, c_5)
        return """
        <canvas id="canvas2" width="500" height="500"></canvas>
        <script id="script2" type="text/javascript">
        var xmag=0;
        var ymag=0;
        var newXmag=0;
        var newYmag=0;
        function sketchProc(processing) { 
            
            processing.setup = function() {
                processing.size(500,500,processing.P3D); 
                processing.noStroke(); 
                processing.colorMode(processing.RGB,255);
            };
            processing.draw = function() {
                  processing.background(0.5);
                  
                  processing.pushMatrix(); 
                 
                  processing.translate(processing.width/2, processing.height/2, -30); 
                  
                  newXmag = processing.mouseX/parseFloat(processing.width) * processing.TWO_PI;
                  newYmag = processing.mouseY/parseFloat(processing.height) * processing.TWO_PI;
                  

                  var diff = xmag-newXmag;
                  if (Math.abs(diff) >  0.01) { xmag -= diff/4.0; }
                  
                  diff = ymag-newYmag;
                  if (Math.abs(diff) >  0.01) { ymag -= diff/4.0; }
                  
                  processing.rotateX(-ymag); 
                  processing.rotateY(-xmag); 
                  
                  processing.scale(90);
                  processing.beginShape(processing.QUADS);
                
                  %s \n 
                  %s \n 
                  %s \n 
                  %s \n 
                  %s \n 
                  %s
                
                  processing.endShape();
                  
                  processing.popMatrix(); 
                  };
            }
            var canvas=document.getElementById("canvas2");
            var p = new Processing(canvas, sketchProc);
            </script>
        
          """ % (q_1, q_2, q_3, q_4, q_5, q_6) 

class worker:
        #note, this is just-above-mysql-level-worker.  
        #I have written it to be an iterable once a query is passed
        #see down below for examples
        #but essentially, you can instantiate a worker instance:
        # w =worker()
        #then exucute some query (let's say q = "select * from answers")
        # w.execute(q)
        #now iterate over the results
        #for row in w:
        # this is going to iterate over each row returned.  the row is an array. 
        # each index in the array is a column from the table that you requested
        # so if you say select *, you are grabbing all of the columns
        # if you had said 'select r,g,b' it would only grab those three columns and they would be row[0],row[1],and row[2] respectively
        
        #to see columns in a mysql database:
        #    get into mysql.  enter command "use X;" where X is the database. 
        #    type "show tables;" to list the tables. and "describe X;" where X is a table name. 
        

        #the cost from worker creation isn't that much so keeping a consistnet worker is not absolutely necessary
        def __init__(self):
                self.db = mysqldb.connect("localhost", "color", "color", "colors") #machine, username, pw, db
                    #note about the above, you must create an account and grant permission to do this, or type in root and root's password here
                    #create user 'color'@'localhost' identified by 'color';
                    #grant all on colors.* to 'color'@'localhost';
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
            
        #following two functions make this an iterator    
        def __iter__(self):
            return self
        
        def next(self):
            item = self.fetchone()
            if item:
                return item
            raise StopIteration

#some static methods that plot and do other things.
class math_helper:
    def __init__(self):
        pass
    
    #get the stats of color component distribution.. not genrealized to any distribution
    @staticmethod
    def stats(distrib):
        d_sum=0
        d_max=0 
        d_min=255
        
        
        plot_distrib=dict([[x,0] for x in range(256)])
        for x in distrib:
            plot_distrib[x]+=1
            d_sum+=x
            if x>d_max:
                d_max=x
            if x<d_min:
                d_min=x
        mean = d_sum/len(distrib)
        d_sum=0
        for x in distrib:
            d_sum+=(x-mean)*(x-mean)
        variance = d_sum/(len(distrib)-1)
        return (mean,variance, d_max, d_min, plot_distrib)
    
    #not generalized, just for plotting the r,g,b components individually to see how they vary individually
    @staticmethod
    def make_plots(r_distrib,g_distrib, b_distrib, name):
        global image_dir
        plt.plot(r_distrib.keys(), r_distrib.values(), 'ro')
        plt.plot(g_distrib.keys(), g_distrib.values(), 'go')
        plt.plot(b_distrib.keys(), b_distrib.values(), 'bo')
        plt.axis([0,256, min(r_distrib.values()+g_distrib.values()+b_distrib.values()), max(r_distrib.values()+g_distrib.values()+b_distrib.values())])
        plt.grid(True, which="both", ls='-')
        plt.savefig("%s%s.png" % (image_dir, name))
        
    @staticmethod
    def make_3d_plot(r_distrib, g_distrib, b_distrib, name):
        global image_dir
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(r_distrib, g_distrib,b_distrib,c='r', marker='^')
        ax.set_ylim(0,255)
        ax.set_xlim(0,255)
        ax.set_zlim(0,255)
        ax.set_xlabel('R')
        ax.set_ylabel('G')
        ax.set_zlabel('B')
        plt.savefig('%s%s.png' % (image_dir,name))
    
    @staticmethod 
    def compare_colors(distributions, rgbs, name):
        global image_dir
        symbols = ['o','x','^', '<', '>', 'v', '|', '*', '8', 'H', '.', '+']
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        if len(distributions)>len(symbols):
            raise Exception
        for x in range(len(distributions)):
            [r_distrib, g_distrib, b_distrib] = distributions[x]
            ax.scatter(r_distrib, g_distrib, b_distrib,c=rgbs[x], marker=symbols[x])
        ax.set_ylim(0,255)
        ax.set_xlim(0,255)
        ax.set_zlim(0,255)
        ax.set_xlabel('R')
        ax.set_ylabel('G')
        ax.set_zlabel('B')
        plt.savefig('%s%s.png' % (image_dir,name))
        
        
    @staticmethod
    def make_single_plot(distribution, name, x_log, y_log):
        global image_dir
        plt.plot(distribution.keys(), distribution.values(), 'ro')
        if x_log:
            plt.xscale('log')
        else:
            plt.xscale('linear')
        if y_log:
            plt.yscale('log')
        else:
            plt.yscale('linear')
        plt.axis([0, max(distribution.keys()), min(distribution.values()), max(distribution.values())])
        plt.grid(True, which="both", ls="-")
        plt.savefig('%s%s.png' % (image_dir,name))
    
    @staticmethod
    def rgb_constraint_trim(r_l, r_u, r, g_l, g_u, g, b_l, b_u, b):
        return (r_l<=r<=r_u) and (g_l<=g<=g_u) and (b_l<=b<=b_u)
    
    @staticmethod
    def rgb_distance_trim(r,g,b,r_variance, g_variance, b_variance, r_mean, g_mean, b_mean):
        
        ave_variance = (g_variance+b_variance+r_variance)/3
        return math_helper.rgb_dist(r,g,b,r_mean,g_mean,b_mean)<=ave_variance
    
    #distance function
    @staticmethod
    def rgb_dist(r_1,g_1,b_1, r_2,g_2,b_2):
        def p(x):
            return math.pow(x,2)
        def s(x):
            return math.sqrt(x)
        return s(p(r_1-r_2)+p(g_1-g_2)+p(b_1-b_2))
    
    @staticmethod
    def trim_method_of_choice(r_l, r_u, r, g_l, g_u, g, b_l, b_u, b, r_variance, g_variance, b_variance, r_mean, g_mean, b_mean):
        #return math_helper.rgb_constraint_trim(r_l, r_u, r, g_l, g_u, g, b_l, b_u, b)
        return math_helper.rgb_distance_trim(r,g,b,r_variance, g_variance, b_variance, r_mean, g_mean, b_mean)
    
    @staticmethod
    def trim_outliers(r_distrib, g_distrib, b_distrib, r_variance, g_variance, b_variance, r_mean, g_mean, b_mean):
        r_u=r_mean+r_variance
        r_l=r_mean-r_variance  
        g_u=g_mean+g_variance #upper and lower bounds on the r,g,b
        g_l=g_mean-g_variance
        b_u=b_mean+b_variance
        b_l=b_mean-b_variance
        y=0
        #print r_u,",", r_l,",", g_u,",", g_l,",", b_u,",", b_l, "<br>"
        ret_r=[]
        ret_g=[]  #done to ensure that the r,g,b tuples stay together
        ret_b=[]
        #print "%s number" % len(r_distrib)
        for x in range(len(r_distrib)):
            r=r_distrib[x] 
            g=g_distrib[x] #these were added simultaneously so we can assume they are a correct tuple
            b=b_distrib[x]
            if math_helper.trim_method_of_choice(r_l, r_u, r, g_l, g_u, g, b_l, b_u, b, r_variance, g_variance, b_variance, r_mean, g_mean, b_mean): #note, this is going to be long and messy. edit: j.k. shortened variales.  much neater. 
                ret_r.append(r)
                ret_g.append(g)
                ret_b.append(b)
            else:
                y+=1
        #print y, " trimmed<br>"
        return [ret_r, ret_g, ret_b]
        
    @staticmethod
    def normalize(numbers):  #note: this might not be normalizing.  just a hack so that the max value is one.  i think actual normalizing would require subtracting min from every value.. but only if you wanted the min to BE 0.. I don't here
        num_max = max(numbers)
        ret=[]
        for x in numbers:
            ret.append((x*1.0)/(num_max*1.0))
        return ret


#actually handles the various page functions    
class page_management:
    def __init__(self):
        #self.connection = mysql.connector.connect(user='root', password='t1477bcm', database='colors',connect_timeout=28800)
        #self.cursor = self.connection.cursor()
        self.worker= worker()
        self.name_query = ("SELECT r,g,b FROM answers WHERE colorname LIKE '%%%s%%'")
        self.rgb_query = ("select * from answers where r>=%s and r<=%s and g>=%s and g<=%s and b>=%s and b<=%s")
        self.proc_api = processing_api()
        self.amidone = False

    def start_page(self):
        global scripts_rel_path
        print "Content-type: text/html"
        print 
        
        print '''<html>
            <head>
            <script src="%sprocessing.js"></script>
             <title>This is an even better program!</title>
            </head>
            
            <body>
            <form name="input" action="color.py" method="post">
            <h3>Exploring color data</h3>
            <p>Type A Color: <input type="text" name="color" /> <br>
            Options: <input type="checkbox" name="color_opts" value="cube">Show cube</input>
                     <input type="checkbox" name="color_opts" value="rgb_dist">Show R,G,B distributions</input>
                     <input type="checkbox" name="color_opts" value="3d_dist">Show 3D RGB Distribution</input>
                     <input type="checkbox" name="color_opts" value="stats">Show statistics</input>
                     <input type="checkbox" name="color_opts" value="dist_3d_without_outliers">Show 3D RGB distribution without outliers</input>
            </p>
            <p> Or Type an RGB (numbers, seperated by commas, strict syntax, i'm lazy): <input type="text" name="rgb" />
            and range: <input type="text" name="range"> <br>
            Options: <input type="checkbox" name="rgb_opts" value="color_name_distrib">Show color name distribution</input>
                     <input type="checkbox" name="rgb_opts" value="color_names">Show top color names</input>
                     
            </p>
            <p>Or enter up to three color names seperated by commas (be nice, syntax is important, i'm lazy): <input type="text" name="comparison"/>
            <p>
            <p>Or check this box for current special function <input type="checkbox" name="special" value="doit" />Do it</p>
            <input type="submit" value="Submit" />
            </form><br>''' % scripts_rel_path
    
    def end_page(self):
        print '''
            
            </body>
            </html>
            '''
        
    def special(self):
        #self.popular_rgbs()
        self.explore_primary()
        
    def popular_rgbs(self):
        q="select * from answers"
        self.worker.execute(q)
        x=0
        y=0
        tracker_set=set()
        tracker_dict=dict()
        for row in self.worker:
            x+=1
            rgb = "%s,%s,%s" % (row[3],row[4],row[5])
            if rgb not in tracker_set:
                tracker_set |= set([rgb])
                y+=1
                tracker_dict[rgb]=0
            tracker_dict[rgb]+=1
        sorted_colors = sorted(tracker_dict.iteritems(), key=operator.itemgetter(1), reverse=True)
        print "top 20 most popular named colors out of %s entries and %s unique RGB values<br>" % (x,y)

        for color in sorted_colors[:20]:
            print color, "<br>"
          
    def error(self, type_of_error):
        if type_of_error==1:
            print "<H1>Error</H1>"
            print "<p>Please fill in one of the user fields.</p>" 
    
    def compare_colors(self, form=None, distances=True, three_d=True, print_colors=True, colors=None, give_back=False):
        global images_rel_path
        if form:
            colors = [(color.lstrip()).rstrip() for color in (form["comparison"].value).split(",")]
        elif colors:
            pass
        else:
            raise Exception
        
        distributions = []
        #each top level is the color distribution
        #for each distribution, there is 5 arrays
        #each of the arrays should have 15 values
        #so one can imagine that each element in stats is a 3x5 table where the columns are the indiv stats, and rows are the components (rgb)
        stats = [] 
        color_names=""
        rgbs_for_print=""
        for color in colors:
            color_names+="%s, " % color
            distributions.append([[], [], []])
            self.worker.execute(self.name_query % color)  
            for row in self.worker:
                distributions[-1][0].append(int(row[0]))
                distributions[-1][1].append(int(row[1]))
                distributions[-1][2].append(int(row[2]))
            stats.append([[],[],[],[],[]])
            (r_mean, r_variance, r_max, r_min, r_plot) = math_helper.stats(distributions[-1][0])
            (g_mean, g_variance, g_max, g_min, g_plot) = math_helper.stats(distributions[-1][1])
            (b_mean, b_variance, b_max, b_min, b_plot) = math_helper.stats(distributions[-1][2])
            rgbs_for_print+="(%s,%s,%s), " % (int(r_mean), int(g_mean), int(b_mean))
            stats[-1][0]+=[r_mean, g_mean, b_mean]
            stats[-1][1]+=[r_variance,g_variance,b_variance]  #tried to think of a better way
            stats[-1][2]+=[r_max, g_max, b_max]             #but i couldn't.  I couldn't deposit the return of a func into a new
            stats[-1][3]+=[r_min, g_min, b_min]             #elem in an array 
            stats[-1][4]+=[r_plot,g_plot,b_plot]
        color_names=color_names[:-2]
        rgbs_for_print=rgbs_for_print[:-2]
        if print_colors:
            print "Comparing colors: %s<br>" % color_names
            #print "With RGB values: %s<br>" % rgbs_for_print
            print "<p>", self.proc_api.make_multiple_color_showcase([[int(d[0][0]), int(d[0][1]), int(d[0][2])] for d in stats]), "</p>"
            print "<br>"
        if distances:
            for x in range(len(colors)):
                stat = stats[x]
                color = colors[x]
                for y in range(x,len(colors)):
                    if x!=y:
                        stat_2 =  stats[y]
                        color_2 = colors[y]
                        print "Distance between %s and %s: %s<br>" % (color, color_2, math_helper.rgb_dist(stat[0][0], stat[0][1], stat[0][2], stat_2[0][0], stat_2[0][1], stat_2[0][2])) 
        if three_d:    
            dist_trimmed=[]
            rgbs=[]
            color_legend=""
            symbols = ['o','x','^', '<', '>', 'v', '|', '*', '8', 'H', '.', '+']
            for c in range(len(colors)):
                color_legend+="%s=%s, " % (colors[c], symbols[c])
            color_legend=color_legend[:-2]
            for d in range(len(distributions)):
                dist = distributions[d]
                stat = stats[d]
                rgbs.append((stat[0][0]/255.0, stat[0][1]/255.0, stat[0][2]/255.0))
                dist_trimmed.append([None, None, None])
                [dist_trimmed[-1][0], dist_trimmed[-1][1], dist_trimmed[-1][2]] = math_helper.trim_outliers(dist[0], dist[1], dist[2], math.sqrt(stat[1][0]), math.sqrt(stat[1][1]), math.sqrt(stat[1][2]), stat[0][0], stat[0][1], stat[0][2])
            math_helper.compare_colors(dist_trimmed, rgbs, "color_compare")
            print "<p><img src='%scolor_compare.png'/><br> <center>The trimmed 3D space with legend: <br>%s</p>" % (color_legend, images_rel_path)  
        if give_back:
            return stats
    
    def explore_primary(self):
        main_colors= ["red", "blue", "yellow", "green", "purple", "orange", "violet"]
        full_color_list=[]
        for color in main_colors:
            full_color_list+=["dark %s" % color, "%s" % color, "light %s" % color]
        stats = self.compare_colors(distances=False,three_d=False,print_colors=True, colors=full_color_list, give_back=True)
        for x in range(0, len(stats), 3):
            center_stat = stats[x+1]
            center_name=full_color_list[x+1]
            dark_stat = stats[x]
            dark_name = full_color_list[x]
            light_stat = stats[x+2]
            light_name = full_color_list[x+2]
            
            center_dark_dist = math_helper.rgb_dist(center_stat[0][0], center_stat[0][1], center_stat[0][2], dark_stat[0][0], dark_stat[0][1], dark_stat[0][2])
            dark_light_dist = math_helper.rgb_dist(dark_stat[0][0], dark_stat[0][1], dark_stat[0][2], light_stat[0][0], light_stat[0][1], light_stat[0][2])
            center_light_dist = math_helper.rgb_dist(center_stat[0][0], center_stat[0][1], center_stat[0][2], light_stat[0][0], light_stat[0][1], light_stat[0][2])
            
            
            print "Stats for %s <br>" % center_name
            print "Distance from %s to %s: %s <br>" % (dark_name, light_name, dark_light_dist)
            print "Distance from %s to %s: %s <br>" % (center_name, light_name, center_light_dist)
            print "Distance from %s to %s: %s <br>" % (center_name, dark_name, center_dark_dist)
            print "Distance from %s to %s through %s: %s" % (dark_name, light_name, center_name, (center_dark_dist+center_light_dist))
            print "<br><br>"
            
            
            
        
    def color_name(self, form):
        global images_rel_path
        cube=dist_3d=rgb_dist=stats=dist_3d_without_outliers=False
        r_distrib=[]
        g_distrib=[]
        b_distrib=[]
        
        if "color_opts" in form:
            opts=form.getlist("color_opts")
            if "cube" in opts: cube=True
            if "3d_dist" in opts: dist_3d=True
            if "rgb_dist" in opts: rgb_dist=True
            if "stats" in opts: stats=True
            if "dist_3d_without_outliers" in opts: dist_3d_without_outliers=True
            
        print "<p>Average of responses containing:", form["color"].value, "</p>"
        self.worker.execute(self.name_query % form["color"].value)  
        for row in self.worker:
            r_distrib.append(int(row[0]))
            g_distrib.append(int(row[1]))
            b_distrib.append(int(row[2]))
            
        (r_mean, r_variance, r_max, r_min, r_plot) = math_helper.stats(r_distrib)
        (g_mean, g_variance, g_max, g_min, g_plot) = math_helper.stats(g_distrib)
        (b_mean, b_variance, b_max, b_min, b_plot) = math_helper.stats(b_distrib)
        
        print "<p>", self.proc_api.make_one_color_showcase(int(r_mean), int(g_mean), int(b_mean))
        print "<br><b>RGB: %s, %s, %s</b></p>" % (int(r_mean), int(g_mean), int(b_mean))
        
        if stats:
            print "<br>Stats:<br>"
            print "r_mean, r_variance, r_std, r_max, r_min: %s, %s, %s, %s, %s <br>" % (r_mean, r_variance, math.sqrt(r_variance), r_max, r_min)
            print "g_mean, g_variance, g_std, g_max, g_min: %s, %s, %s, %s, %s <br>" % (g_mean, g_variance, math.sqrt(g_variance), g_max, g_min)
            print "b_mean, b_variance, b_std, b_max, b_min: %s, %s, %s, %s, %s <br>" % (b_mean, b_variance, math.sqrt(b_variance), b_max, b_min)
        
        if cube:
            print self.proc_api.make_and_get_cube_code(r_mean, g_mean, b_mean, math.sqrt(r_variance), math.sqrt(g_variance), math.sqrt(b_variance))
        
        if rgb_dist:
            math_helper.make_plots(r_plot,g_plot,b_plot, "distribution")
            print "<img src='%sdistribution.png'/><br>Distribution over the RGB components individually<br><br>" % images_rel_path
            
        if dist_3d:
            math_helper.make_3d_plot(r_distrib, g_distrib, b_distrib, "distrib_3dplot")
            print "<img src='%sdistrib_3dplot.png'/><br>3D plot of all RGB points with this color label<br><br>" % images_rel_path
        
        if dist_3d_without_outliers:
            [r_distrib_trimmed, g_distrib_trimmed, b_distrib_trimmed] = math_helper.trim_outliers(r_distrib, g_distrib, b_distrib, math.sqrt(r_variance), math.sqrt(g_variance), math.sqrt(b_variance), r_mean, g_mean, b_mean)
            math_helper.make_3d_plot(r_distrib_trimmed, g_distrib_trimmed, b_distrib_trimmed, "distrib_3dplot_trimmed")
            print "<img src='%sdistrib_3dplot_trimmed.png'/><br>3D plot with all of the outliers trimmed<br><br>" % images_rel_path
            

    
    def rgb_value(self, form):
        color_name_distrib=color_names=False
        if "rgb_opts" in form:
            opts = form.getlist("rgb_opts")
            if "color_name_distrib" in opts: color_name_distrib=True
            if "color_names" in opts: color_names = True
            
        if "range" not in form: 
            print "You need to provide a range. defaulting to +-5"
            rgb_range=5
        else:
            try:
                rgb_range = int(form['range'].value)
            except:
                print "You gave me a non number.  using +-5"
                rgb_range = 5
                
        rgbs = (form["rgb"].value).split(",")
        color = 'rgb(%s, %s, %s)' % (rgbs[0], rgbs[1], rgbs[2])
        print "<h3>Retrieving color names for %s</h3>" % color
        try:
            r=int(rgbs[0])
            g=int(rgbs[1])
            b=int(rgbs[2])
        except ValueError as e:
            print "You gave a bad number, %s" % e
        r_range=[r-rgb_range, r+rgb_range]
        g_range=[g-rgb_range, g+rgb_range]
        b_range=[b-rgb_range, b+rgb_range]
        [r_range[0], r_range[1], g_range[0], g_range[1], b_range[0],b_range[1]]=self.proc_api._rgb_cube_helper(r, g, b, rgb_range, rgb_range, rgb_range)
        #print r_range, g_range, b_range
        #print '<table style="background-color:' + color + ';height:300px;width:300px;"><tr><td><p></p></td></tr></table>' # old way
        
        self.worker.execute(self.rgb_query % (r_range[0], r_range[1], g_range[0], g_range[1], b_range[0], b_range[1]))
        all_colors_set = set()
        all_colors_dict = dict()
        colors_by_rgb_dict=dict()
        colors_by_rgb_set=set()
        for row in self.worker:
            rgb = "%s,%s,%s" % (row[3],row[4],row[5])
            color = "%s" % row[-1]
            if rgb not in colors_by_rgb_set:
                colors_by_rgb_set |= set([rgb])
                colors_by_rgb_dict[rgb]=dict()  
                
            if color in colors_by_rgb_dict[rgb]: colors_by_rgb_dict[rgb][color]+=1
            else: colors_by_rgb_dict[rgb][color]=1
                
            if color not in all_colors_set:
                all_colors_set |= set([color])
                all_colors_dict[color] = 1
            else: all_colors_dict[color]+=1
                
        
        print self.proc_api.make_and_get_cube_code(r, g, b, rgb_range, rgb_range, rgb_range)
        
        if color_name_distrib: self.show_color_name_distribution(all_colors_dict)
        if color_names: self.show_color_names(all_colors_dict, rgb_range)
        
        
        
    def show_color_name_distribution(self, all_colors_dict):
        global images_rel_path
        sorted_colors = sorted(all_colors_dict.iteritems(), key=operator.itemgetter(1), reverse=True)
        distrib=dict()
        x=0
        second_distrib=dict()
        for color_pair in sorted_colors:
                distrib[x]=color_pair[1]
                x+=1
                if x<200:
                    second_distrib[x]=color_pair[1]
        
        math_helper.make_single_plot(distrib, "all_words_distribution", True, True)
        math_helper.make_single_plot(second_distrib, "alt_distribution", False, False)
        print "<br><img src='%sall_words_distribution.png'/>" % images_rel_path
        print "<br><img src='%salt_distribution.png'/>" % images_rel_path
            
            
    def show_color_names(self, all_colors_dict, rgb_range):
        sorted_colors = sorted(all_colors_dict.iteritems(), key=operator.itemgetter(1), reverse=True)
        #top_num = len(sorted_colors)
        top_num=400
        print "<br>Top %s color names within +-%s range of given rgb:<br>" % (top_num, rgb_range)
        for pair in sorted_colors[:top_num]:
            print pair, "<br>"
    
    def show_rgb_distribution(self, colors_by_rgb_dict):
        print "Distribution over each RGB value in the cube<br><br>"
        for (rgb,color_dict) in colors_by_rgb_dict.iteritems():
            print "<b>",rgb,"</b><br>"
            for color_pair in sorted(color_dict.iteritems(), key=operator.itemgetter(1), reverse=True):
                print color_pair, "<br>"
            print "<br><br>"



form = cgi.FieldStorage()
manager = page_management()
manager.start_page()

if "special" in form:
    manager.special()
elif "color" not in form and "rgb" not in form and "comparison" not in form:
    manager.error(1)
elif "color" in form and "rgb" not in form and "comparison" not in form:
    manager.color_name(form)
elif "rgb" in form and "color" not in form and "comparison" not in form:
    manager.rgb_value(form)
elif "comparison" in form and "color" not in form and "rgb" not in form:
    manager.compare_colors(form)
else:
    print "one or the other please"
    
manager.end_page()