import xbmc, xbmcgui
import time
import subprocess
import common

fanart = {}
fanart_changed = 0
def get_fanart_list():
    global fanart
    showlist = common.file_get_contents("/data/etc/.fanart")
    if showlist == "":
        return
        
    showlist = showlist.split("\n")
    fanart = {}
    for line in showlist:
        if "=" in line:
            line = line.split("=")
            show = line[0]
            art = line[1]
            fanart[show] = art

def store_fanart_list():
    global shows, fanart_changed
    
    file = ""
    for show in fanart:
        file = file + show + "=" + fanart[show] + "\n"
    
    common.file_put_contents("/data/etc/.fanart", file)
    fanart_changed = 0

def grab_fanart_for_item(item):
    global fanart, fanart_changed

    if item.GetProperty("fanart") != "":
        return

    label = item.GetLabel()
    path = "%s" % item.GetPath()
    if "stack:" in path:
        path = path.split(" , ")
        path = path[len(path)-1]
        
    thumbnail = item.GetThumbnail()
    art = ""

    # to make sure we don't generate fanart entries for things like vimeo
    if path.find("http://") != -1:
        return

    if label in fanart:
        art = fanart[item.GetLabel()]
    elif path != "" and path.find("boxeedb://") == -1:
        art = path[0:path.rfind("/")+1] + "fanart.jpg"
    elif thumbnail.find("special://") == -1:
        art = thumbnail[0:thumbnail.rfind("/")+1] + "fanart.jpg"
#    else:
#        db_path = xbmc.translatePath('special://profile/Database/')
#        sql = ".timeout 1000000\n"
#        if path.find("boxeedb://") == -1:
#            # it must be a movie
#            sql = sql + "SELECT strCover FROM video_files WHERE strTitle=\"" + label + "\";\n"
#        else:
#            # it must be a tv show
#            sql = sql + "SELECT strCover FROM series WHERE strTitle=\"" + label + "\";\n"
#
#        common.file_put_contents("/tmp/sqlinject", sql)
#        os.system('/bin/sh \'cat /tmp/sqlinject | /data/hack/bin/sqlite3 "' + db_path + '../../../Database/boxee_catalog.db" > /tmp/readsql\'')
#        thumbnail = common.file_get_contents("/tmp/readsql")
#        if "/" in thumbnail:
#            art = thumbnail[0:thumbnail.rfind("/")+1] + "fanart.jpg"

    if art != "":
        fanart[label] = art
        fanart_changed = 1
        item.SetProperty("fanart", art)

def get_list(listNum):
    try:
        lst = mc.GetActiveWindow().GetList(listNum)
    except:
        lst = ""
    return lst

def grab_fanart_list(listNum):
    global fanart_changed
    
    get_fanart_list()
    
    # sometimes the list control isn't available yet onload
    # so add some checking to make sure
    lst = get_list(listNum)
    count = 10
    while lst == "" and count > 0:
        time.sleep(0.25)
        lst = get_list(listNum)
        count = count - 1

    if lst == "":
        pass
    else:
        items = lst.GetItems()
        
        # as long as the list exists (while the window exists)
        # the list gets updated at regular intervals. otherwise
        # the fanart disappears when you change sort-orders or
        # select a genre
        # should have very little overhead because all the values
        # get cached in memory
        while lst != "":
            items = lst.GetItems()
            # try and apply the stuff we already know about
            for item in items:
                grab_fanart_for_item(item)
                
            time.sleep(0.25)
            
            lst = get_list(listNum)
        
            # store the fanart list for next time if the list
            # was modified
            if fanart_changed == 1:
                store_fanart_list()

if (__name__ == "__main__"):
    command = sys.argv[1]

    if command == "grab_fanart_list": grab_fanart_list(int(sys.argv[2]))