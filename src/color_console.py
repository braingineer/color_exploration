#!/usr/bin/python
# Demo program for processing a html request
# using a CGI script and an sqlite database

import operator
import math 
import MySQLdb as mysqldb
import matplotlib
matplotlib.rcParams['backend']='Qt4Agg'
#matplotlib.use("Agg")
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import multiprocessing
from Queue import Empty
import time

from graphics import *


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
                self.db = mysqldb.connect("localhost", "color", "color", "colors") #machine, username, pw, db
                self.dbc = self.db.cursor() #our main worker guys

        def execute(self, query):
            self.dbc.execute(query)

        def insert_and_commit(self, query):
                #the insert and commit is for people who want to insert things.. 
                #no commit is needed for the select
                self.dbc.execute(query) #the execution.. 
                self.db.commit()  #need commit otherwise execute won't "save" so to speak

        def select(self, query):
                #NOTE: returns the number of items found.  Use fetchall or fetchone to get results      
                return self.dbc.execute(query)

        def fetchall(self):
                #returns all results of last query as a list
                return self.dbc.fetchall()

        def fetchone(self):
                #returns one result at a time from last query
                return self.dbc.fetchone()
            
        def __iter__(self):
            return self
        
        def next(self):
            item = self.fetchone()
            if item:
                return item
            raise StopIteration

class math_helper:
    def __init__(self):
        pass
    
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
    
    @staticmethod
    def make_plots(r_distrib,g_distrib, b_distrib, name, save=False):
        plt.plot(r_distrib.keys(), r_distrib.values(), 'ro')
        plt.plot(g_distrib.keys(), g_distrib.values(), 'go')
        plt.plot(b_distrib.keys(), b_distrib.values(), 'bo')
        plt.axis([0,256, min(r_distrib.values()+g_distrib.values()+b_distrib.values()), max(r_distrib.values()+g_distrib.values()+b_distrib.values())])
        plt.grid(True, which="both", ls='-')
        if save:
            plt.savefig("%s.png" % name)
        plt.show()
        
    @staticmethod
    def make_freq_plot(freq):
        x = [y for y in range(len(freq))]
        plt.plot(x, freq)
        plt.axis([0,len(x), 0, max(freq)])
        plt.show()
        
        
    @staticmethod
    def make_3d_plot(r_distrib, g_distrib, b_distrib, name, save=False):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(r_distrib, g_distrib,b_distrib,c='r', marker='^')
        ax.set_ylim(0,255)
        ax.set_xlim(0,255)
        ax.set_zlim(0,255)
        ax.set_xlabel('R')
        ax.set_ylabel('G')
        ax.set_zlabel('B')
        if save:
            plt.savefig('%s.png' % name)
        plt.show()
    
    @staticmethod 
    def compare_up_to_three_colors(distributions, rgbs, name, save=False):
        symbols = ['o','x','^', '<', '>', 'v', '|', '*']
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
        if save:
            plt.savefig('%s.png' % name)
        plt.show()
        
    @staticmethod
    def make_single_plot(distribution, name, x_log, y_log, save=False):
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
        if save:
            plt.savefig("%s.png" % name)
        plt.show()
    
    @staticmethod
    def rgb_constraint_trim(r_l, r_u, r, g_l, g_u, g, b_l, b_u, b):
        return (r_l<=r<=r_u) and (g_l<=g<=g_u) and (b_l<=b<=b_u)
    
    @staticmethod
    def rgb_distance_trim(r,g,b,r_variance, g_variance, b_variance, r_mean, g_mean, b_mean):
        def p(x):
            return math.pow(x,2)
        def s(x):
            return math.sqrt(x)
        ave_variance = (g_variance+b_variance+r_variance)/3
        return s(p(r_mean-r)+p(g_mean-g)+p(b_mean-b))<=ave_variance
    
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
    
#
#class classify_process(multiprocessing.Process):
#    def __init__(self):
#        multiprocessing.Process.__init__(self)
#    
#    def run(self):
#        self.classify_procedure()
#    
#    def classify_procedure(self):
#        global todo_queue, finished_queue
#        try:
#            [color_names, coords, cur_name] = todo_queue.get(1,5)
#            all_names_set=set()
#            all_names=dict()
#            changed=0
#            for name in color_names:
#                if name not in all_names_set:
#                    all_names_set |= set([name])
#                    all_names[name]=0
#                all_names[name]+=1
#            sorted_colors = sorted(all_names.iteritems(), key=operator.itemgetter(1), reverse=True)
#            if len(sorted_colors)>0:
#                if sorted_colors[0][0]=="null" and len(sorted_colors)>1:
#                    new_color = sorted_colors[1][0]
#                else:
#                    new_color = sorted_colors[0][0]
#            else:
#                new_color = "null"
#            if new_color!=cur_name:
#                changed=1
#            finished_queue.put([coords, new_color, changed],1)
#        except Empty:
#            print "Catching empty exception.  Standard when processes are faster"
#            print "TODO Queue: todo_queue.qsize()"
#    
#    
#class break_up_process(multiprocessing.Process):
#    def __init__(self, matrix_chunk, offset):
#        multiprocessing.Process.__init__(self)
#        self.chunk = matrix_chunk
#        self.offset = offset
#    
#    def run(self):
#        pass
#    
#    def break_up_procedure(self):
#        for x in range(len(self.chunk)):
#            r = self.offset+x #note, offset should be first R value
#            
        
class SimpleProgress:
    def __init__(self, total):
        self.total = total
    
    def start(self):
        self.start_time = time.time()
        
    def update(self, x):
        if x>0:
            elapsed = time.time()-self.start_time
            percDone = x*100.0/self.total
            estimatedTimeInSec=(elapsed*1.0/x)*self.total
            return "%s %s percent\n%s Processed\nElapsed time: %s\nEstimated time: %s\n--------" % (self.bar(percDone), round(percDone, 2), x, self.form(elapsed), self.form(estimatedTimeInSec))
        return ""
    
    def form(self, t):
        hour = int(t/(60.0*60.0))
        minute = int(t/60.0 - hour*60)
        sec = int(t-minute*60-hour*3600)
        return "%s Hours, %s Minutes, %s Seconds" % (hour, minute, sec)
        
    def bar(self, perc):
        done = int(round(30*(perc/100.0)))
        left = 30-done
        return "[%s%s]" % ('|'*done, ':'*left)    

class console_management:
    def __init__(self):
        #self.connection = mysql.connector.connect(user='root', password='#######', database='colors',connect_timeout=28800)
        #self.cursor = self.connection.cursor()
        self.worker= worker()
        self.name_query = ("SELECT r,g,b FROM answers WHERE colorname LIKE '%%%s%%'")
        self.rgb_query = ("select * from answers where r>=%s and r<=%s and g>=%s and g<=%s and b>=%s and b<=%s")
    
    def convert_rgb_to_hex(self, r,g,b):
        def c(x):
            if x<10:return x
            else: return {10:"A", 11:"B", 12:"C", 13:"D", 14:"E", 15:"F"}[x]
        return ("#%s%s%s%s%s%s" % (c(r/16), c(r%16), c(g/16), c(g%16), c(b/16), c(b%16)))

#    def cluster(self):
#        global finished_queue, todo_queue
#        finished_queue = multiprocessing.Queue(10000000)
#        todo_queue = multiprocessing.Queue(1000000)
#        q = "Select r,g,b,colorname from answers"
#        print "Initializing matrix..."
#        full_matrix=[[[["null"] for z in range (256)] for y in range(256)] for x in range(256)]
#        print "Grabbing from database..."
#        self.worker.execute(q)
#        for row in self.worker:
#            full_matrix[int(row[0])-1][int(row[1])-1][int(row[2])-1]+=[row[3]]
#        for r in range(256):
#            for g in range(256):
#                for b in range(256):
#                    temp_dict=dict()
#                    if len(full_matrix[r][g][b])>1:
#                        for name in full_matrix[r][g][b]:
#                            if name not in temp_dict.keys():
#                                temp_dict[name]=0
#                            temp_dict[name]+=1
#                        sorted_names = sorted(temp_dict.iteritems(), key=operator.itemgetter(1), reverse=True)
#                        full_matrix[r][g][b]=sorted_names[0][0]
#                    else:
#                        full_matrix[r][g][b]=full_matrix[r][g][b][0]
#                        
#        changed=1000
#        threshold=100
#        iteration=0
#        print "Begin the nearest neighbor clustering..."
#        for x in range(6):
#            classifier = classify_process()
#            classifier.start()
#        while changed>threshold:
#            changed=0
#            iteration+=1
#            new_matrix=[]
#            for r in range(256):
#        
#                print "At r=%s" % r
#                new_matrix.append([])
#                for g in range(256):
#                    new_matrix[r].append([])
#                    for b in range(256):
#                        new_matrix[r][g].append("null")
#                        color = full_matrix[r][g][b]
#                        color_list = self.get_color_list(r,g,b,full_matrix,3)
#                        todo_queue.put([color_list, [r,g,b], color], 1)
#                        #new_color = self.rank_color_neighbors(r,g,b,full_matrix,3)
#                        #if color!=new_color:
#                            #changed+=1  
#                        #new_matrix[r][g][b]=new_color
#            full_matrix = new_matrix
#            print "%s changed on iteration %s" % (changed, iteration)
#        all_colors=dict()
#        all_colors_set=set()
#        for r in range(256):
#            for g in range(256):
#                for b in range(256):
#                    color = full_matrix[r][g][b]
#                    if color not in all_colors_set:
#                        all_colors_set |= set([color])
#                        all_colors[color]=0
#                    all_colors[color]+=1
#        print "%s total colors after the clustering" % len(all_colors_set)
#        sorted_colors = sorted(all_colors.iteritems(), key=operator.itemgetter(1), reverse=True)
#        for color_pair in sorted_colors:
#            print color_pair
            
            
    def cluster_prep(self):
        main_query = "Select r,g,b,colorname from answers"
        color_name_query = "select colorname from trimmed_colors"
        cluster_prep_query = "insert into cluster_prep (r,g,b,color_names) values "
        cluster_prep_addition =  "(%s,%s,%s,'%s'), "
        prog = SimpleProgress(256*256)
        print "Initializing matrix..."
        full_matrix=[[[[] for z in range (256)] for y in range(256)] for x in range(256)]
        print "Getting acceptable colors..."
        self.worker.execute(color_name_query)
        valid_colors = set()
        for row in self.worker:
            valid_colors |= set([row[0]])
        print "%s valid colors" % len(valid_colors)
        #so we get valid colors, step through original, build cluster distribution
        
        print "Populating matrix with data..."
        self.worker.execute(main_query)
        x=0
        for row in self.worker:
            color = row[3]
            #print color
            if color in valid_colors:
                x+=1
                full_matrix[int(row[0])][int(row[1])][int(row[2])]+=[color]
        print "%s colors inserted into the full matrix" % x
        print "Starting 5x5x5 voxel aggregation..."
        prog.start()
        for r in range(256):
            for g in range(256):
                print prog.update(256*r+g)
                q = cluster_prep_query
                for b in range(256):
                    color_list = self.get_color_list(r,g,b,full_matrix,5)
                    if len(color_list)>0:
                        q+=cluster_prep_addition % (r,g,b,color_list)
                #print q
                if q!=cluster_prep_query:
                    self.worker.insert_and_commit(q[:-2])     
        
        print "DONE"  

#
#        #getting smaller color sets
#        print "getting"
#        all_colors_dict=dict()
#        all_colors_set=set()
#        self.worker.execute(main_query)
#        for row in self.worker:
#            color = row[3].replace("'", "")
#            if color not in all_colors_set:
#                all_colors_set |= set([color])
#                all_colors_dict[color]=0
#            all_colors_dict[color]+=1
#        
#        
#        print "sorting..."
#        all_colors_ordered = sorted(all_colors_dict.iteritems(), key=operator.itemgetter(1), reverse=True)
#        final_colors = set()
#        trimmed_color_query = "insert into trimmed_colors (colorname) values "
#        for pair in all_colors_ordered:
#            if pair[1]>2:
#                final_colors |= set([pair[0]])
#                trimmed_color_query+="('%s'), " % pair[0]
#        trimmed_color_query=trimmed_color_query[:-2]
#        self.worker.insert_and_commit(trimmed_color_query)

                    
            
            
        """
        q="insert into cluster_prep (r,g,b,color_names) values(%s,%s,%s,'%s')"
        for r in range(256):
            print "At r=%s" % r
            for g in range(256):
                for b in range(256):
                    color = full_matrix[r][g][b]
                    color_list = self.get_color_list(r,g,b,full_matrix,3)
                    self.worker.insert_and_commit(q % (r,g,b,"%s" % color_list))
                    #new_color = self.rank_color_neighbors(r,g,b,full_matrix,3)
                    #if color!=new_color:
                        #changed+=1  
                        #new_matrix[r][g][b]=new_color
            full_matrix = new_matrix
            print "%s changed on iteration %s" % (changed, iteration)
        all_colors=dict()
        all_colors_set=set()
        for r in range(256):
            for g in range(256):
                for b in range(256):
                    color = full_matrix[r][g][b]
                    if color not in all_colors_set:
                        all_colors_set |= set([color])
                        all_colors[color]=0
                    all_colors[color]+=1
        print "%s total colors after the clustering" % len(all_colors_set)
        sorted_colors = sorted(all_colors.iteritems(), key=operator.itemgetter(1), reverse=True)
        for color_pair in sorted_colors:
            print color_pair
            """
    
    def get_color_list(self,r,g,b,matrix,c_range):
        color_dict = dict()
        color_set = set()
        for r_new in range(r-c_range, r+c_range+1):
            if (255>=r_new>=0):
                for g_new in range(g-c_range,g+c_range+1):
                    if 255>=g_new >= 0:
                        for b_new in range(b-c_range,b+c_range+1):
                            if 255>=b_new >= 0 and not (r_new==r and g_new == g and b_new == b):
                                colors = matrix[r_new][g_new][b_new]
                                for color in colors:
                                    if color not in color_set:
                                        color_set |= set([color])
                                        color_dict[color] = 0
                                    color_dict[color]+=1
        ret =""
        #print "%s colors for %s,%s,%s" % (len(color_dict), r,g,b)
        for pair in sorted(color_dict.iteritems(), key=operator.itemgetter(1), reverse=True):
            ret+="%s|%s," % (pair[0], pair[1])
        #print ret
        return ret[:-1]
        
    def rank_color_neighbors(self, r,g,b,matrix,c_range):        
        all_names=dict()
        all_names_set=set()
        for r_new in range(r-c_range, r+c_range+1):
            if (255>=r_new>=0):
                for g_new in range(g-c_range,g+c_range+1):
                    if 255>=g_new >= 0:
                        for b_new in range(b-c_range,b+c_range+1):
                            if 255>=b_new >= 0 and not (r_new==r and g_new == g and b_new == b):
                                name = matrix[r_new][g_new][b_new]
                                if name not in all_names_set:
                                    all_names_set |= set([name])
                                    all_names[name]=0
                                all_names[name]+=1
        sorted_colors = sorted(all_names.iteritems(), key=operator.itemgetter(1), reverse=True)
        if len(sorted_colors)>0:
            if sorted_colors[0][0]=="null" and len(sorted_colors)>1:
                return sorted_colors[1][0]
            return sorted_colors[0][0]
        else:
            return "null"
        
    def user_patterns(self):
        q = "SELECT id from users"
        self.worker.execute(q)
        id_dict=dict()
        for row in self.worker:
            id_dict[row[0]]=0
        print "Got all IDs (%s), looking them up now" % (len(id_dict))
        x=0
        for uid in id_dict.keys():
            x+=1
            if x%(len(id_dict)/10)==0: print "we are %s tenths done" % (x/(len(id_dict)/10)) 
            q="SELECT count(id) from answers where user_id='%s'" % uid
            self.worker.execute(q)
            for row in self.worker:
                id_dict[uid]=row[0]
        print "Average number of colors named: %s" % (sum(id_dict.values())*1.0/len(id_dict))
        sorted_ids=sorted(id_dict.iteritems(), key=operator.itemgetter(1), reverse=True)
        for (uid, number) in sorted_ids[:200]:
            print "ID: %s, Number named: %s" % (uid, number)
        math_helper.make_freq_plot([y for [x,y] in sorted_ids[:10000]])
        
           
    def color_name(self, color):
        r_distrib=[]
        g_distrib=[]
        b_distrib=[]
        
        self.worker.execute(self.name_query % color)  
        for row in self.worker:
            r_distrib.append(int(row[0]))
            g_distrib.append(int(row[1]))
            b_distrib.append(int(row[2]))
            
        (r_mean, r_variance, r_max, r_min, r_plot) = math_helper.stats(r_distrib)
        (g_mean, g_variance, g_max, g_min, g_plot) = math_helper.stats(g_distrib)
        (b_mean, b_variance, b_max, b_min, b_plot) = math_helper.stats(b_distrib)
        
        
        #window = GraphWin("Color Visualizer", 300, 300)
        #color_rect = Rectangle(Point(0,0), Point(300,300))
        #color_rect.draw(window)
        #color_rect.setFill(self.convert_rgb_to_hex(int(r_mean), int(g_mean), int(b_mean)))
        print "RGB: %s, %s, %s" % (int(r_mean), int(g_mean), int(b_mean))
        
        print "------------\n"
        print "Stats:\n"
        print "r_mean, r_variance, r_std, r_max, r_min: %s, %s, %s, %s, %s <br>" % (r_mean, r_variance, math.sqrt(r_variance), r_max, r_min)
        print "g_mean, g_variance, g_std, g_max, g_min: %s, %s, %s, %s, %s <br>" % (g_mean, g_variance, math.sqrt(g_variance), g_max, g_min)
        print "b_mean, b_variance, b_std, b_max, b_min: %s, %s, %s, %s, %s <br>" % (b_mean, b_variance, math.sqrt(b_variance), b_max, b_min)
        

        #print "First Plot: Distribution over R, Distribution over G, Distribution over B"
        #math_helper.make_plots(r_plot,g_plot,b_plot, "distribution")
        print "For the following plots, they take forever, please be patient"
        print "Second Plot: Distribution over RGB space"
        math_helper.make_3d_plot(r_distrib, g_distrib, b_distrib, "distrib_3dplot")
        
        print "Third Plot: Distribution over RGB space with points trimmed"
        print "\t(trimmed if distance from average RGB > standard deviation"
        [r_distrib_trimmed, g_distrib_trimmed, b_distrib_trimmed] = math_helper.trim_outliers(r_distrib, g_distrib, b_distrib, math.sqrt(r_variance), math.sqrt(g_variance), math.sqrt(b_variance), r_mean, g_mean, b_mean)
        math_helper.make_3d_plot(r_distrib_trimmed, g_distrib_trimmed, b_distrib_trimmed, "distrib_3dplot_trimmed")
        
        #window.getMouse()
        #window.close()

        
        
if __name__=="__main__":
    has_not_chosen=True
    option=""
    manager = console_management()
    print "Welcome to the color console\n\t-\t-\t-"
    while has_not_chosen:
        print "please choose an option (by typing the number associated with it):"
        print "1. Color Name information\t2. Find user patterns\t3. chinese whisper cluster (1 nearest neighbor)"
        print "4. Cluster Prep"
        option=raw_input(">")
        try:
            option = int(option)
            has_not_chosen=False
        except:
            if option=="exit":
                option=-1
                has_not_chosen=False
            else: print "Sorry, you did not enter a correct integer, please try again"
    if option==-1:
        print "goodbye"
    elif option==1:
        looking_at_color_names=True
        while looking_at_color_names:
            print "Please type a color name (type exit to exit):" 
            color_input = raw_input(">")
            if color_input!="exit":
                manager.color_name(color_input)
            else:
                looking_at_color_names=False
    elif option==2:
        manager.user_patterns()
    elif option==3:
        #manager.cluster()
        print "currently not working"
    elif option==4:
        manager.cluster_prep()