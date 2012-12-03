Things that need to be done:

1. Apache2
-Just install for now.  on linux, sudo apt-get install apache2

2. MySQL
-Install. Create a database called colors.  from terminal
mysql -u root -p
([type in password]
create database colors;
exit;

Then navigate to where the mysqldump is for colors.  make sure restore has the right permissions:
sudo chmod 771 restore
Then use restore to load in the dump (the .sql file)
restore colors
The name of the file needs to be colors.sql (same name as the database)
and  you can't pass in the filename with its extension (the .sql part) because it uses the name in the mysql call to say "use this database please"

3. Python
sorry that most of these directions are for linux.  on windows/mac there should be a similar analog or some webpage found via google
get python 2.7. also get the dev package (sudo apt-get install python2.7-dev , i think. the dash may or may not be there).  
get setup-tools ( go to http://pypi.python.org/pypi/setuptools , download appropriate version, the 'sudo sh [filename]')
get python-mysql ( also called mysqldb, found at http://sourceforge.net/projects/mysql-python/  , there's a file INSTALL that comes with it, but basically it's 'python setup.py build' then 'sudo python setup.py install'  if you're on linux you can also do a sudo apt-get install python-mysql ... i realized this after I went through all the problems.  see my mysqldb.instaljournal for details if you run into problems, maybe I had the same problem)
get matplotlib.  there are usually no issues with this one.  
this should be it for the python dependencies.

4. Server setup (do this last)
go into /etc/apache2 and configure the 000-default conf file in the sites-enabled folder
here you want to add:
ScriptAlias /somepaththing/ /var/www/somefoldername/
<Directory "/var/www/somefoldername/">
	AllowOverride None
	Options +ExecCGI -Multiviews +SymLinksIfOwnerMatch
	Order allow,deny
	Allow from all
</Directory>

where somepaththing will become a localhost/somepaththing and somefoldername is the folder inside your apache's document root directory 

At least on my install, cgid was already enabled so I didn't have to do that.  If it's not for you, then you have to enable the cgi or cgid mod (cgid in case of some multithreading module, didn't have problems so didn't investiage this part of setup)

What I had originally set up on my old machine no longer works, So I had to do some funky things.  In the color.py, specifically in the math helper class, the functions that create images are putting them in a subfolder of the apache document root (in the default case the document root is '/var/www/').  I had to do this because apache was having a really hard time dealing with images in a cgi-enabled folder.  Similarily, processing.js needs to be moved to a folder called "scripts" that is just below the document root (aka '/var/www/scripts/')

If you decide to put scripts and images somewhere not underneath the document root of apache, then you need to set up some Aliases in the apache config files (this is because matplotlib needs the actual file path to save the images, and the client-side html needs a website path).  it's a little bit of a pain, but not impossible.  it's easier just to save the headache, though, and create the two folders just under the '/var/www' (or whereever you have doc root).  

After you have the images and scripts folders created, and the paths correctly pointing (the variables to set are at the top of the color.py), put the processing.js in the scripts folder

What I did for the color.py is mildly complicated.  I didn't want to have to worry about running, editing, copying, etc, so I made a hard link between my workspace and the /somefoldername/ 
basically: ln /home/brian/workspace/color/src/color.py /var/www/dev/color.py  -- and then inside the dev/ folder, I did the following to allow apache to run it:
'chown brian:www-data . color.py processing.js' 
'chmod 0775 . color.py processing.js' 

The reason for the chown (change owner) is because apache operates under the www-data user group, and my username is brian.  this allows for me to 'own' the file and 'www-data' to be granted permissions on the file.  the chmod changes permissions for 3 different levels at once.  the first is the '7' part.  it is a representation of a 3 bit binary number: 111 which reprsents 'rwx', so that the '4' bit is 'r', '2' bit is 'w', and '1' bit is 'x'.  7 is 'rwx', 5 is 'r-x'.  the 775 sets a 7 for owner, 7 for group, and 5 for everyone else.  Since I have set the group to www-data, apache gets to read, write, and execute.  


