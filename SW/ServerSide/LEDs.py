
#!/usr/bin/python
import sys
sys.path.append("/home/pi/PWM")
from Adafruit_PWM_Servo_Driver import PWM
import time
import threading
import MySQLdb
import colorsys
import os

#main dealing with arguments
if len(sys.argv)>1:
  if sys.argv[1]=="debug":
    debug = True
else:
  debug = False
  sys.stdout = open('program.log','a')

#pidfile dealing
pid = os.getpid()
print str(pid)
pidfile = open('/var/run/program.pid','w')
pidfile.write(str(pid))
pidfile.close()
os.nice(-10)

#set up main variables
program=0
sl=0.01
Gh=0.0
s=0.0
l=0.0
run=0

#setup for PWM modul
pwm = PWM(0x40, debug=True);
pwm.setPWMFreq(1000);
pwm.setPWM(15,0,4095)
ledField = []

class ledChannel:
        r=0
        g=0
        b=0
        rb=0
        number=0
        program = 0
        step=0
        sleep=0
        h=0
        l = 0.5
        s = 1
        Pmodul = None
        global Gh
        def __init__(self,number,name,Pmodul):
                self.number = number
                self.name = name
                self.Pmodul = Pmodul
                self.lock = threading.Lock()

        def __repr__(self):
                return "-----------------------------------------\n"+str(self.number)+", "+str(self.name)+"\nthis is color of this channel r:"+str(self.r)+" g:"+str(self.g)+"b:"+str(self.b)+"\n program is "+str(self.program)+", also step and sleep is:"+str(self.step)+" "+str(self.sleep)+"\n\n\n\n";

        def __str__(self):
                return "-----------------------------------------\n"+str(self.number)+", "+str(self.name)+"\nthis is color of this channel r:"+str(self.r)+" g:"+str(self.g)+"b:"+str(self.b)+"\n program is "+str(self.program)+", also step and sleep is:"+str(self.step)+" "+str(self.sleep)+"\n\n\n\n";

        def setColor(self, r,g,b):
                self.r = r
                self.b = b
                self.g = g

        def setHLS(self,h,l,s):
                color = colorsys.hls_to_rgb(h, l, s);
                #print color
                self.r=color[0]*255
                self.g=color[1]*255
                self.b=color[2]*255

        def updateDir(self):
                #print "R>"+str(int(16*self.r))+"  G>"+str( int(16*self.g))+"  B>"+str( int(16*self.b))
                self.Pmodul.setPWM(1+3*self.number-1,0,int(16*self.r));
                self.Pmodul.setPWM(2+3*self.number-1,0,int(16*self.g));
                self.Pmodul.setPWM(3+3*self.number-1,0,int(16*self.b));

        def update(self):
                if self.program == 0:
                        #print "still normal color"
                        self.Pmodul.setPWM(1+3*self.number-1,0,int(16*self.r));
                        self.Pmodul.setPWM(2+3*self.number-1,0,int(16*self.g));
                        self.Pmodul.setPWM(3+3*self.number-1,0,int(16*self.b));
                        return;

                if self.program == 1:
                        self.h += self.step
                        self.setHLS(self.h,self.l,self.s)
                        self.updateDir()

                if self.program == 2:
                        self.setHLS(Gh,self.l,self.s)
                        self.updateDir()

#pocatecni naplneni pole s kanaly, zde se bude tahat jmeno z databaze
for i in range(0,5):
        temp = ledChannel(i,"this is chanel nmbr:"+str(i),pwm)
        ledField.append(temp)


def mysql():
  db=MySQLdb.connect(host='localhost',user='led',passwd='led',db='LED')
  cur = db.cursor()
  cur.execute("SELECT * FROM mainColors LIMIT 5;")
  p=0
  for row in cur.fetchall() :
    program=int(row[4])
    h=row[1]
    s=row[3]
    l=row[2]
    sleep = row[6]
    step = row[5]
    #print row
    if program == 0:
                ledField[p].setHLS(h,l,s)
                ledField[p].program = program
                ledField[p].step = step
                ledField[p].sleep = sleep
    if program == 1:
                ledField[p].program = program
                ledField[p].step = step
                ledField[p].sleep = sleep
                ledField[p].l = l
                ledField[p].s = s
    if program == 2:
                ledField[p].program = program
                ledField[p].step = step
                ledField[p].sleep = sleep
                ledField[p].l = l
                ledField[p].s = s
    #print ledField[p]
    p+=1

  cur.close()
  db.close()

def updateField():
        update = False
        updateStep = 0
        global Gh
        for i in range(0,5):
                ledField[i].update();
                if ledField[i].program == 2:
                        update = True
                        updateStep = ledField[i].step
        if update:
                Gh+=updateStep

def end():
  ending = open("/home/pi/PWM/end.sys","r")
  if ending.read(4)=="True":
    out("ENDING APP by end file")
    ending.close()
    e=open('/home/pi/PWM/end.sys','w')
    e.write('False')
    exit()


try:
  while 1:
        end()
        mysql()
        updateField()
        #print ledField
        time.sleep(sl)
except KeyboardInterrupt:
        ledField[1].program = 0
        updateField()
        exit()

