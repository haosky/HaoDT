import logging
import logging.handlers
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
import haounits as parent
def get_defFileLogger(fileName,loggerMain='',level=logging.DEBUG):
    settings_file = get_uri_relative_parent_package(parent, "logging.properties")

    logparentpath = get_items_in_cfg("file", "root_path",settings_file)
    log = logging.getLogger(loggerMain)
    rf  = logging.handlers.RotatingFileHandler(filename=logparentpath+'/'+fileName,maxBytes=8000000,backupCount=3)
    format=logging.Formatter("%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s")
    rf.setFormatter(format)
    log.addHandler(rf)
    log.setLevel(level)
    return log

def get_defTestLogger(level=logging.DEBUG,clazz='default'):
    logi = logging.getLogger(str(clazz))
    logging.basicConfig(level=level,
    format='%(asctime)s %(name)-12s %(levelname)- %(lineno)d -8s %(message)s',
    datefmt='%m-%d %H:%M',
    # filename='myapp.log',
    # filemode='w'
                )
    return logi

