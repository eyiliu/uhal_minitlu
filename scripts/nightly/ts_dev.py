from nutils import system
from os import environ, listdir,getenv
from os.path import join,basename,isdir,expanduser
from sys import argv
from platform import platform,node
from socket import getfqdn
import getpass

class Nightly :
  def __init__(self, group,email,name,b_home):
    print "Selected group '"+group+"'"
    
    self.TO_EMAIL            = email
    self.CHECKOUT_NAME       = name
    self.BUILD_HOME          = b_home

    self.USER_NAME           = getpass.getuser()
    self.USER_HOME           = join(expanduser("~"))
    self.PLATFORM            = platform()
    self.HOSTNAME            = node()
    self.RELATIVE_BASE       = join("nightly",basename(__name__+"_"+group),self.PLATFORM)
    self.NIGHTLY_BASE        = join(self.USER_HOME,"www",self.RELATIVE_BASE)
    self.NIGHTLY_RPM_DIR     = join(self.NIGHTLY_BASE,"RPMS")
    self.NIGHTLY_LOG_DIR     = join(self.NIGHTLY_BASE,"logs")
    #The log file name and path should be the same than in the one in the acrontab
    self.CACTUS_PREFIX       = "/opt/cactus"
    self.XDAQ_ROOT           = "/opt/xdaq"
    self.L1PAGE_ROOT         = "/opt/l1page/tomcat/webapps/ROOT"

    #PSEUDO PLATFORM
    self.pseudo_platform = "unknown"
    if self.PLATFORM.find("i686-with-redhat-5") != -1:
        self.pseudo_platform="slc5_i686"
    elif self.PLATFORM.find("x86_64-with-redhat-5") != -1:
        self.pseudo_platform="slc5_x86_64"
    elif self.PLATFORM.find("x86_64-with-redhat-6") != -1:
        self.pseudo_platform="slc6_x86_64"

    ####VARIABLES: analysis of logs
    self.TITLE             = "TS Nightlies : %s @%s " % (self.pseudo_platform,self.HOSTNAME)
    self.FROM_EMAIL        = "cactus.service@cern.ch"
    self.WEB_URL           = join("http://cern.ch/"+self.USER_NAME,self.RELATIVE_BASE)
    self.NIGHTLY_LOG_FILE  = join(self.NIGHTLY_LOG_DIR,"nightly.log")
    self.ERROR_LIST        = ['error: ',
                        'RPM build errors',
                        'collect2: ld returned',
                        ' ERROR ',
                        ' Error ',
                        'TEST FAILED',
                        'L1Page ERROR']

    self.IGNORE_ERROR_LIST = ["sudo pkill",
                        "sudo rpm -ev"]

    self.TEST_PASSED_LIST  = ["TEST OK",
                        "L1Page OK"]

    ####ENVIRONMENT
    environ["XDAQ_ROOT"]       = self.XDAQ_ROOT
    environ["LD_LIBRARY_PATH"] = ":".join([join(self.CACTUS_PREFIX,"lib"),
                                          join(self.XDAQ_ROOT,"lib"),
                                          "/lib",
                                          environ.get("LD_LIBARY_PATH","")])
    
    self.importCommonCommands()
    
    if group == "TS_DEV" : 
      self.nightlyTSDev()
    elif group == "SUBSYSTEM_DEV" :
      self.nightlySubsystemDev()
    elif group == "SUBSYSTEM_904" :
      self.nightlySubsystem904()
      
    self.COMMANDS += [["CHECKOUT",
                  [";".join(self.CHECKOUT_CMDS)]]]

    print "Setting up nightly build instructions done!"


  def importCommonCommands(self) :
    self.COMMANDS = []

    self.COMMANDS += [["TESTECHO", 
                  ["echo This is a test",
                  "echo TO_EMAIL = %s" %self. TO_EMAIL,
                  "echo CHECKOUT_NAME = %s" % self.CHECKOUT_NAME,
                  "echo BUILD_HOME = %s" % self.BUILD_HOME,
                  "echo PLATFORM = %s" % self.PLATFORM,
                  "echo HOSTNAME = %s" % self.HOSTNAME,
                  "echo RELATIVE_BASE = %s" % self.RELATIVE_BASE,
                  "echo NIGHTLY_BASE = %s" % self.NIGHTLY_BASE]]]


    self.COMMANDS += [["CLEANUP_WWW_AREA", [""]]] # Dummy placeholder -- this corresponds to the call to cleanupLogs()


    self.COMMANDS += [["UNINSTALL",
                  ["sudo /sbin/service xdaqd stop &> /dev/null ",
                  "rpm -qa | grep daq-xaas-l1test | xargs sudo rpm -ev --nodeps",
                  "sudo yum -y groupremove triggersupervisor",
                  "sudo yum -y groupremove uhal",
                  "sudo yum -y groupremove extern_coretools coretools extern_powerpack powerpack database_worksuite general_worksuite hardware_worksuite ",
                  "sudo pkill -f \"xdaq.exe\" ",
                  "rpm -qa| grep cactuscore- | xargs sudo rpm -ev &> /dev/null ",
                  "rpm -qa| grep cactusprojects- | xargs sudo rpm -ev &> /dev/null ",
                  "sudo pkill -f \"jsvc\" &> /dev/null ",
                  "sudo pkill -f \"DummyHardwareTcp.exe\" &> /dev/null ",
                  "sudo pkill -f \"DummyHardwareUdp.exe\" &> /dev/null ",
                  "sudo pkill -f \"cactus.*erlang\" &> /dev/null ",
                  "sudo pkill -f \"cactus.*controlhub\" &> /dev/null ",
                  "sudo rm -f /etc/yum.repos.d/xdaq.repo",
                  "sudo rm -f /etc/yum.repos.d/ts.repo",
                  "sudo rm -f /etc/yum.repos.d/ts_subsystem.repo",
                  "sudo rm -f /etc/yum.repos.d/cactus.repo",
                  "sudo rm -rf %s" % self.BUILD_HOME]]]
                  

    self.COMMANDS += [["ENVIRONMENT",
                ["env"]]]
    

    self.CHECKOUT_CMDS = ["sudo mkdir -p %s" % self.BUILD_HOME,
                    "sudo chmod -R 777 %s" % self.BUILD_HOME,
                    "cd %s" % self.BUILD_HOME]


    self.COMMANDS += [["RELEASE",
                  ["rm -rf %s" % self.NIGHTLY_RPM_DIR,
                  "mkdir -p %s" % self.NIGHTLY_RPM_DIR,
                  "mkdir -p %s" % self.NIGHTLY_LOG_DIR,
                  "cp %s %s" % ("yumgroups.xml",self.NIGHTLY_RPM_DIR),
                  "find %s -name '*.rpm' -exec cp {} %s \;" % (self.BUILD_HOME,self.NIGHTLY_RPM_DIR),
                  "cd %s;createrepo -vg yumgroups.xml ." % self.NIGHTLY_RPM_DIR]]]


    self.COMMANDS += [["TEST_DUMMY_SUBSYSTEM",
                  ["sudo cp %s /etc/tnsnames.ora" % join(self.BUILD_HOME,"l1test/daq/xaas/slim/l1test/settings/etc/tnsnames.cern.ora"),
                  "cp -r %s %s" % (self.USER_HOME+"/secure", self.BUILD_HOME),                                
                  "cd %s;make; make rpm; make install;" % join(self.BUILD_HOME,"l1test/daq/xaas/slim/l1test"),               
                  "sudo cp %s /etc/slp.conf" % join(self.BUILD_HOME,"l1test/daq/xaas/slim/l1test/settings/etc/slp.localhost.conf"),
                  "sudo /sbin/service slp restart",
                  "/bin/slptool findsrvs service:directory-agent",
                  "sudo /sbin/service xdaqd start l1test",
                  "sleep 240",
                  "sudo /sbin/service xdaqd status l1test",
                  "cd %s;python multicell.py" % join(self.BUILD_HOME,"trunk/cactusprojects/subsystem/tests"),
                  "cd %s;python multicell_fault.py;" % join(self.BUILD_HOME,"trunk/cactusprojects/subsystem/tests"),
                  "cd %s;python multicell_stress.py" % join(self.BUILD_HOME,"trunk/cactusprojects/subsystem/tests"),
                  "sudo /sbin/service xdaqd stop l1test"]]]


    self.COMMANDS += [["TEST_L1CE",
                  ["sudo /sbin/service xdaqd start l1test",
                  "sleep 30",
                  "sudo /sbin/service xdaqd status l1test",
                  "cd %s;python l1ce.py" % join(self.BUILD_HOME,"trunk/cactuscore/ts/l1ce/tests"),
                  "sudo /sbin/service xdaqd stop l1test"]]]
  
  
    self.COMMANDS += [["TEST_CENTRAL_CELL",
                  ["sudo /sbin/service xdaqd start l1test",
                  "sleep 30",
                  "sudo /sbin/service xdaqd status l1test",
                  "cd %s;python central.py" % join(self.BUILD_HOME,"trunk/cactusprojects/central/tests"),
                  "sudo /sbin/service xdaqd stop l1test"]]]



    self.COMMANDS += [["TEST_GT",
                  [#"sed -i 's|\(PWD_PATH=\).*$|\\1%s|' %s" % (join(self.BUILD_HOME,"secure"),
                  #                                            join(self.BUILD_HOME,"gtgmttest/daq/xaas/slim/gtgmttest/service/mf.service.settings")),
                  "cd %s;make;make rpm;make install" % join(self.BUILD_HOME,"gtgmttest/daq/xaas/slim/gtgmttest"),
                  "sudo rm -f /etc/cron.d/gtgmttest.jobcontrol.cron",
                  "sudo /sbin/service xdaqd start gtgmttest",
                  "sleep 30",
                  "sudo /sbin/service xdaqd status gtgmttest",
                  "cd %s;python gt.py" % join(self.BUILD_HOME,"trunk/cactusprojects/gt/tests"),
                  "sudo /sbin/service xdaqd stop gtgmttest"]]]


    self.COMMANDS += [["TEST_GMT",
                  ["sudo /sbin/service xdaqd start gtgmttest",
                  "sleep 30",
                  "sudo /sbin/service xdaqd status gtgmttest",
                  "cd %s;python gmt.py" % join(self.BUILD_HOME,"trunk/cactusprojects/gmt/tests"),
                  "sudo /sbin/service xdaqd stop gtgmttest"]]]


    self.COMMANDS += [["TEST_L1PAGE",
                  ["sudo yum -y install cactusprojects-l1page-*",
                  "mkdir -p %s" % join(self.BUILD_HOME, "triggerpro/l1page/data"),
                  "sudo sed -i 's|%s|%s|g' %s" % ("/nfshome0/centraltspro", self.BUILD_HOME, join(self.L1PAGE_ROOT, "main/l1page.properties")),
                  "sudo sed -i 's|%s|%s|g' %s" % ("/nfshome0", self.BUILD_HOME, join(self.L1PAGE_ROOT, "main/l1page.properties")),
                  "sudo sed -i 's|%s|%s|g' %s" % ("log4j.appender","#log4j.appender", join(self.L1PAGE_ROOT, "WEB-INF/classes/log4j.properties")),
                  "python %s" % join(self.L1PAGE_ROOT, "test/l1pageTest.py")]
                  ]]
                

  def cleanupLogs(self) :
    # The following lines are meant to delete old platform directories containing RPMs and logs
    target_platform = "unknown"
    if self.pseudo_platform == "slc5_i686":
        target_platform = "i686-with-redhat-5"
    elif self.pseudo_platform == "slc5_x86_64":
        target_platform = "x86_64-with-redhat-5"
    elif self.pseudo_platform == "slc6_x86_64":
        target_platform = "x86_64-with-redhat-6"
      
      
    system("mkdir -p %s" % self.NIGHTLY_BASE,exception=False)
    system("rm -f %s" % join(self.NIGHTLY_BASE,"..",self.pseudo_platform),exception=False)
    system("ln -s %s %s" % (self.NIGHTLY_BASE,join(self.NIGHTLY_BASE,"..",self.pseudo_platform)),exception=False)

    del_dirs = [d for d in listdir(join(self.NIGHTLY_BASE, "..")) if isdir(join(self.NIGHTLY_BASE, "..", d)) and d.find(target_platform) != -1 and d != platform()]
    for d in del_dirs:
        system("rm -rf %s" % join(self.NIGHTLY_BASE, "..", d), exception=False)



  ### Build groups
  # TS_DEV
  def nightlyTSDev(self):
    self.DEFAULT_COMMANDS    = ["CLEANUP_WWW_AREA","UNINSTALL","ENVIRONMENT","DEPENDENCIES",
                        "CHECKOUT","BUILD","RELEASE","INSTALL","TEST_DUMMY_SUBSYSTEM",
                        "TEST_L1CE"]
                  
    XDAQ_REPO_FILE_NAME = "xdaq12.%s.repo" % self.pseudo_platform
    self.COMMANDS += [["DEPENDENCIES",
		   ["sudo yum -y install arc-server createrepo bzip2-devel zlib-devel ncurses-devel python-devel curl curl-devel graphviz graphviz-devel boost boost-devel wxPython e2fsprogs-devel libuuid-devel qt qt-devel PyQt PyQt-devel qt-designer libusb libusb-devel gd-devel xsd",
                  "sudo cp %s %s" % (XDAQ_REPO_FILE_NAME,"/etc/yum.repos.d/xdaq.repo"),
                  "sudo yum clean all && sudo yum clean metadata && sudo yum clean dbcache && sudo yum makecache",
                  "sudo yum -y groupinstall extern_coretools coretools extern_powerpack powerpack database_worksuite general_worksuite hardware_worksuite",
                  "sed \"s/<platform>/%s/\" cactus.stable.repo  | sudo tee /etc/yum.repos.d/cactus.repo > /dev/null" % self.pseudo_platform,
                  "sudo yum clean all && sudo yum clean metadata && sudo yum clean dbcache && sudo yum makecache",
                  "sudo yum -y groupinstall uhal"
                  ]]]
                  
    self.CHECKOUT_CMDS += ["svn -q co svn+ssh://%s@svn.cern.ch/reps/cactus/trunk trunk/" % self.CHECKOUT_NAME,
                    "svn -q co svn+ssh://%s@svn.cern.ch/reps/cmsos/branches/l1_xaas l1test/daq/xaas/" % self.CHECKOUT_NAME
                    ]
    
    self.COMMANDS += [["BUILD",
                ["cd %s;make -sk Set=tsdev" % join(self.BUILD_HOME,"trunk"),
                "cd %s;make -sk Set=tsdev rpm" % join(self.BUILD_HOME,"trunk")
                ]]]  
    
    self.COMMANDS += [["INSTALL",
                  ["sed \"s/<platform>/%s/\" ts_dev.nightly.repo  | sudo tee /etc/yum.repos.d/ts.repo > /dev/null" % self.pseudo_platform,
                  "sudo yum clean all && sudo yum clean metadata && sudo yum clean dbcache && sudo yum makecache",
                  "sudo yum --disablerepo=cactus-base,cactus-updates -y groupinstall triggersupervisor"]]]
    
    
    
  # SUBSYSTEM_DEV  
  def nightlySubsystemDev(self):
    self.DEFAULT_COMMANDS    = ["CLEANUP_WWW_AREA","UNINSTALL","ENVIRONMENT","DEPENDENCIES",
                        "CHECKOUT","BUILD","RELEASE","INSTALL","TEST_DUMMY_SUBSYSTEM",
                        "TEST_CENTRAL_CELL",
                        "TEST_GT","TEST_GMT","TEST_L1PAGE"]
                          
    XDAQ_REPO_FILE_NAME = "xdaq12.%s.repo" % self.pseudo_platform
    WBM_REPO_FILE_NAME = "wbm.repo"
    SLC6X_CERN_FILE_NAME="slc6X-cernonly.repo"
    self.COMMANDS += [["DEPENDENCIES",
                  ["sudo cp %s %s" % (WBM_REPO_FILE_NAME, "/etc/yum.repos.d/wbm.repo"),
		   "sudo cp %s %s" % (SLC6X_CERN_FILE_NAME, "/etc/yum.repos.d/slc6X-cernonly.repo"),
		   "sudo yum -y install arc-server createrepo bzip2-devel zlib-devel ncurses-devel python-devel curl curl-devel graphviz graphviz-devel boost boost-devel wxPython e2fsprogs-devel libuuid-devel qt qt-devel PyQt PyQt-devel qt-designer libusb libusb-devel gd-devel xsd wbm-support-root",
                  "sudo cp %s %s" % (XDAQ_REPO_FILE_NAME,"/etc/yum.repos.d/xdaq.repo"),
                  "sudo yum clean all && sudo yum clean metadata && sudo yum clean dbcache && sudo yum makecache",
                  "sudo yum -y groupinstall extern_coretools coretools extern_powerpack powerpack database_worksuite general_worksuite hardware_worksuite",
		  "sed \"s/<platform>/%s/\" cactus.stable.repo  | sudo tee /etc/yum.repos.d/cactus.repo > /dev/null" % self.pseudo_platform,
                  "sudo yum clean all && sudo yum clean metadata && sudo yum clean dbcache && sudo yum makecache",
                  "sudo yum -y groupinstall triggersupervisor"
                  ]]]       
            
    self.CHECKOUT_CMDS += ["svn -q co svn+ssh://%s@svn.cern.ch/reps/cactus/trunk trunk/" % self.CHECKOUT_NAME,
                    "svn -q co svn+ssh://%s@svn.cern.ch/reps/cmsos/branches/l1_xaas l1test/daq/xaas" % self.CHECKOUT_NAME, 
                    "svn -q co svn+ssh://%s@svn.cern.ch/reps/cmsos/branches/gtgmt_xaas_xdaq12 gtgmttest/daq/xaas" % self.CHECKOUT_NAME
                    ]
         
    self.COMMANDS += [["BUILD",
                  ["cd %s;make -sk Set=tssub; make -sk Set=tsupgrades" % join(self.BUILD_HOME,"trunk"),
                  "cd %s;make -sk Set=tssub rpm; make -sk Set=tsupgrades" % join(self.BUILD_HOME,"trunk")
                  ]]]
     
    self.COMMANDS += [["INSTALL",
                  ["sed \"s/<platform>/%s/\"  subsystem_dev.nightly.repo | sudo tee /etc/yum.repos.d/ts_subsystem.repo > /dev/null" % self.pseudo_platform,
                  "sudo yum clean all && sudo yum clean metadata && sudo yum clean dbcache && sudo yum makecache",
                  "sudo yum --disablerepo=cactus-base,cactus-updates -y groupinstall gtgmt"]]]

    
    
  # SUBSYSTEM_904
  def nightlySubsystem904(self):
    self.DEFAULT_COMMANDS    = ["CLEANUP_WWW_AREA","UNINSTALL","ENVIRONMENT","DEPENDENCIES",
                          "CHECKOUT","BUILD","RELEASE","INSTALL","TEST_DUMMY_SUBSYSTEM",
                          "TEST_CENTRAL_CELL",
                          "TEST_GT","TEST_GMT","TEST_L1PAGE"]
    
    self.CHECKOUT_CMDS += ["svn -q co svn+ssh://%s@svn.cern.ch/reps/cactus/trunk" % self.CHECKOUT_NAME,
                    "svn -q co svn+ssh://%s@svn.cern.ch/reps/cmsos/branches/l1_xaas l1test/daq/xaas" % self.CHECKOUT_NAME,
                    "svn -q co svn+ssh://%s@svn.cern.ch/reps/cmsos/branches/gtgmt_xaas_xdaq12 gtgmttest/daq/xaas" % self.CHECKOUT_NAME]


    XDAQ_REPO_FILE_NAME = "xdaq.%s.repo" % self.pseudo_platform

    self.COMMANDS += [["DEPENDENCIES",
                  ["sudo yum -y install arc-server createrepo bzip2-devel zlib-devel ncurses-devel python-devel curl curl-devel graphviz graphviz-devel boost boost-devel wxPython e2fsprogs-devel libuuid-devel qt qt-devel PyQt PyQt-devel qt-designer libusb libusb-devel gd-devel xsd",
                  "sudo cp %s %s" % (XDAQ_REPO_FILE_NAME,"/etc/yum.repos.d/xdaq.repo"),
                  "sudo yum clean all && sudo yum clean metadata && sudo yum clean dbcache && sudo yum makecache",
                  "sudo yum -y groupinstall extern_coretools coretools extern_powerpack powerpack database_worksuite general_worksuite hardware_worksuite",
                  "sudo cp ts_legacy904.repo /etc/yum.repos.d/ts.repo",
                  "sudo yum clean all && sudo yum clean metadata && sudo yum clean dbcache && sudo yum makecache",
                  "sudo yum -y groupinstall uhal triggersupervisor"
                  ]]]
    
    self.COMMANDS += [["BUILD",
                  ["cd %s;make -sk Set=tssub" % join(self.BUILD_HOME,"trunk"),
                  "cd %s;make -sk Set=tssub rpm" % join(self.BUILD_HOME,"trunk")]]] 
    
    self.COMMANDS += [["INSTALL",
                  ["sed \"s/<platform>/%s/\"  ts_904.nightly.repo | sudo tee /etc/yum.repos.d/ts_subsystem.repo > /dev/null" % self.pseudo_platform,
                  "sudo yum clean all && sudo yum clean metadata && sudo yum clean dbcache && sudo yum makecache",
                  "sudo yum -y --disablerepo=ts-legacy-904 groupinstall gtgmt"]]]
    
