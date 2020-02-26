# -*- coding: utf-8 -*-
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
############################                                                                                    ############################
############################                        S T A B L E   B R A N C H                                   ############################
############################                                                                                    ############################
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
###########
###########FUNCTIONS
###########
import subprocess
import xbmc
import xbmcgui
import xbmcaddon
import time
# import xml
from xml.etree import ElementTree as xmlet
import httplib
import urllib
import itertools
import mimetools
import mimetypes
from cStringIO import StringIO
import urllib2
import os
import datetime
import time
#import sched
from threading import Timer
#from uuid import getnode as get_mac
import socket
import fcntl
import struct

#import settings
from settings import *

def log(text):
    flog = open(PLAYERBZ_logfile, 'a')
    flog.write("%s     %s\n" % (datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"), text))
    flog.close()    
    
##########################################################################################

def encode_multipart_formdata(fields, files):
     """
     fields is a sequence of (name, value) elements for regular form fields.
     files is a sequence of (name, filename, value) elements for data to be uploaded as files
     Return (content_type, body) ready for httplib.HTTP instance
     """
     BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
     CRLF = '\r\n'
     L = []
     for (key, value) in fields:
         L.append('--' + BOUNDARY)
         L.append('Content-Disposition: form-data; name="%s"' % key)
         L.append('')
         L.append(value)
     for (key, filename, value) in files:
         L.append('--' + BOUNDARY)
         L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
         L.append('Content-Type: %s' % get_content_type(filename))
         L.append('')
         L.append(value)
     L.append('--' + BOUNDARY + '--')
     L.append('')
     body = CRLF.join(L)
     content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
     return content_type, body
     
def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'     
    
##########################################################################################    

def send_file_to_server(path, file_type):
    
    try:
        conn = httplib.HTTPConnection(PLAYERBZ_server)
    except:
        log('ERROR: CANT OPEN CONNECTION TO %s'%PLAYERBZ_server)
        return 0
    
    fields=[['type', file_type], ['module_id', PLAYERBZ_module_mac], ['ver', PLAYERBZ_version]]
    files=[[file_type, file_type, open(path, "rb").read()]]
    
    content_type, body = encode_multipart_formdata(fields, files)
    headers = {
    'Content-Type': content_type
    }
    
    try:
        conn.request('POST', '/modulecontrol/modulelog/', body, headers)     
        res = conn.getresponse()
        request_status=res.status
        return 1
        
    except Exception as e:
        log('ERROR: Upload request falied for file: %s : %s'%(path,e))
        return 0

##########################################################################################

def send_log_files():
    Timer(PLAYERBZ_sendlogstimer, send_log_files).start()
    
    log('INFO: SENDING LOGFILE TO SERVER. LOG: %s'%PLAYERBZ_kodilogfile)
    if send_file_to_server(PLAYERBZ_kodilogfile, 'kodi.log') == 1:
        flog = open(PLAYERBZ_kodilogfile, 'w')
        flog.write("_____LOG FILE WAS CLEARED_______\n")
        flog.close()
    else:
        log('LOG %s WAS NOT SENT TO SERVER'%PLAYERBZ_kodilogfile)
        
    log('INFO: SENDING LOGFILE TO SERVER. LOG: %s'%PLAYERBZ_logfile)
    if send_file_to_server(PLAYERBZ_logfile, 'playerbz.log') == 1:
        flog = open(PLAYERBZ_logfile, 'w')
        flog.write("_____LOG FILE WAS CLEARED_______\n")
        flog.close()
    else:
        log('LOG %s WAS NOT SENT TO SERVER'%PLAYERBZ_logfile)
        

##########################################################################################

def PLAYERBZ_load_playlist():
    global PLAYERBZ_playlist_content
    global PLAYERBZ_playlist_sync_in_progress
    log('DEBUG: LOADING PLAYLIST')
    PLAYERBZ_sync_needed=0
    if os.path.exists(PLAYERBZ_playlist_path):
        try:
            synclist = xmlet.parse(PLAYERBZ_playlist_path)
        except:
            log('ERROR: READING XML PLAYLIST ERROR AT %s' %PLAYERBZ_playlist_path)
            PLAYERBZ_get_playlist()
            return 1
            
        PLAYERBZ_playlist_content=[]
        synclist = synclist.getroot()
        PLAYERBZ_content_path=PLAYERBZ_video_storage_path
        if PLAYERBZ_content_type=='audio':
            PLAYERBZ_content_path=PLAYERBZ_audio_storage_path
            
        if PLAYERBZ_content_type=='video':
            PLAYERBZ_content_path=PLAYERBZ_video_storage_path     
            
        if PLAYERBZ_content_type=='image':
            PLAYERBZ_content_path=PLAYERBZ_image_storage_path              
        
        if synclist.tag == "SyncList":
            filesarr=os.listdir(PLAYERBZ_content_path)
            if len(filesarr) == 0:
                log('DEBUG: THERE IS NO ONE NORMAL CONTENT FILE')
                PLAYERBZ_sync_needed=1
            for file in os.listdir(PLAYERBZ_content_path):
                file_listed=0
                #log('REVERSE TEST FOR %s'%file)
                for obj in synclist.iter("file"):
                    
                    filename=obj.find('filename').text
                    url=obj.find('url').text
                    filetype=obj.find('type').text
                    
                    if monitor.abortRequested():
                        return 1
                    if(file == filename):
                        file_listed=1
                    if not os.path.exists(PLAYERBZ_content_path + filename):
                        log('DEBUG: FILE %s IN PLAYLIST WAS NOT DOWNLOADED. NEED PLAYLIST SYNC'%filename)
                        PLAYERBZ_sync_needed = 1

                if(file_listed == 0):
                    log('DEBUG: File %s not listed in playlist, deleting it'%file)
                    try:
                        os.remove(PLAYERBZ_content_path+file)
                    except:
                        log('ERROR: CANT UNLINK FILE: %s%s'%(PLAYERBZ_content_path,file))
                else:
                    log("INFO: PLAYLIST ADDED: %s%s"%(PLAYERBZ_content_path, file))
                    PLAYERBZ_playlist_content.append(PLAYERBZ_content_path + file)
            
            log('DEBUG: PLAYLiST LOADING DONE')        
            if (PLAYERBZ_sync_needed == 0):
                log('DEBUG: PLAYLIST SYNC NOT NEEDED')
                return 1 
            
            if (PLAYERBZ_playlist_sync_in_progress == 0):
                PLAYERBZ_playlist_content=[]
                #forward sync
                log('DEBUG: STARTING PLAYLIST SYNC')
                PLAYERBZ_playlist_sync_in_progress = 1
                #PLAYERBZ_get_playlist()
                for obj in synclist.iter("file"):
                    if monitor.abortRequested():
                        return 1  
                        
                    filename=obj.find('filename').text
                    url=obj.find('url').text
                    filetype=obj.find('type').text
                    caption=obj.find('caption').text
                    log("DEBUG: FILE: %s %s %s %s"%(filename, url, filetype, caption))
                    
                    if not os.path.exists(PLAYERBZ_content_path + filename):
                        if os.path.exists(PLAYERBZ_content_path + filename + '.download'):
                            os.remove(PLAYERBZ_content_path + filename +'.download')
    
                        log('DEBUG: DOWNLOADING %s'%url)
                        try:
                            urllib.urlcleanup()
                            res = urllib.urlretrieve(url, PLAYERBZ_content_path + filename + '.download')
                        except:
                            log('ERROR: CANNOT DOWNLOAD %s'%(url))
                            
                        try:
                            os.rename(PLAYERBZ_content_path + filename + '.download', PLAYERBZ_content_path + filename)
                            log('DEBUG: FILE %s DOWNLOADED'%file)
                            #break
                        except:
                            log('ERROR: CANT RENAME %s%s.download! File will be remooved at next sync'%(PLAYERBZ_content_path, filename))
    
                    if os.path.exists(PLAYERBZ_content_path + filename):
                        PLAYERBZ_playlist_content.append(PLAYERBZ_content_path + filename)
                        log("INFO: PLAYLIST ADDED: %s%s"%(PLAYERBZ_content_path, filename))
                        if (not player.isPlaying()):
                            PLAYERBZ_play_main_content()
                    else:
                        log('ERROR: FILE WAS DOWNLOADED FROM %s BUT DOES NOT EXISTS AT %s%s'%(url,PLAYERBZ_content_path,filename))
                log('INFO: PLAYLIST SYNC DONE!')
                PLAYERBZ_playlist_sync_in_progress = 0
            else:
                log('WARN: ANOTHER SYNC IN PROGRESS. OR HERE IS A BUG')
        else:
            PLAYERBZ_playlist_sync_in_progress = 0
            log('ERROR: W R O N G   V I D E O   P L A Y L I S T   F O R M A T')
            PLAYERBZ_get_playlist()
    else:
        PLAYERBZ_playlist_sync_in_progress = 0
        log('DEBUG: PLAYLIST NOT EXIST.')
        PLAYERBZ_get_playlist()
    return 1    
    
##########################################################################################

        
def PLAYERBZ_get_playlist():
    global PLAYERBZ_playlist_content
    global PLAYERBZ_sync_needed
    #PLAYERBZ_playlist_content=[]
    request_status=0
    log('DEBUG: GET SERVER PLAYLIST')

    if (PLAYERBZ_module_mac == ''):
        log('ERROR: Object not defined %s'%(PLAYERBZ_module_mac))
        return 0
        
    PLAYERBZ_sync_needed=0
    
    try:
        conn = httplib.HTTPConnection(PLAYERBZ_server)
    except:
        log('ERROR: CANT OPEN CONNECTION TO %s'%PLAYERBZ_server)
        
    try:
        conn.request("GET", "/modulecontrol/playlist/?module_id=%s&ver=%s"%(PLAYERBZ_module_mac, PLAYERBZ_version))
        res = conn.getresponse()
        request_status=res.status
    except Exception as e:
        log('ERROR: Connection error %s'%e)
            
    if request_status == 200:
        log('DEBUG: Playlist recieved succesfull')
        servlist = res.read()
        try:
            synclist = xmlet.fromstring(servlist)
        except Exception as e:
            log("ERROR: ERROR READING XML: %s"%e)
            return 0
        
        try:
            fplaylist = open(PLAYERBZ_playlist_path, 'w')
            fplaylist.write("%s"%servlist)
            fplaylist.close()
        except Exception as e:
            log('ERROR: Cannot write to playlist as %s : %s'%(PLAYERBZ_playlist_path, e))
        PLAYERBZ_sync_needed=1
        PLAYERBZ_load_playlist()            
    else:
        log('ERROR: ERROR RECIEVING PLAYLIST:%s'%request_status)
        

##########################################################################################

def PLAYERBZ_build_play_list():
    if (not PLAYERBZ_module_mac == ''):
        PLAYERBZ_load_playlist()
        PLAYERBZ_load_marketinglist()
        
##########################################################################################
        
def PLAYERBZ_update_play_list():
    if (not PLAYERBZ_module_mac == ''):
        PLAYERBZ_get_playlist()
        PLAYERBZ_get_marketinglist()
            
##########################################################################################

def PLAYERBZ_load_marketinglist():
    global PLAYERBZ_marketing_content
    global PLAYERBZ_schedule_set
    global PLAYERBZ_sheduletime
    log('DEBUG: LOADING MARKETINGLIST')
    PLAYERBZ_sync_needed=1
    if os.path.exists(PLAYERBZ_marketing_playlist_path):
        try:
            synclist = xmlet.parse(PLAYERBZ_marketing_playlist_path)
        except Exception as e:
            log('ERROR: READING XML MARKETINGLIST ERROR: %s'%e)
            PLAYERBZ_get_marketinglist()
            return 1
    
        synclist = synclist.getroot()
        PLAYERBZ_content_path=PLAYERBZ_marketing_storage_path
        
        PLAYERBZ_marketing_content=[]
        if PLAYERBZ_sheduletime > 0:
            if PLAYERBZ_schedule_set == 0:
                PLAYERBZ_schedule_set=1
                arg=[]
                arg.append(PLAYERBZ_sheduletime)                
                log("INFO: SCHEDULLING MARKETING REPEAT TIMER :%s SECONDS"%PLAYERBZ_sheduletime)
                Timer(PLAYERBZ_sheduletime, PLAYERBZ_insert_play, arg).start()
        
        if synclist.tag == "SyncList":
            files=os.listdir(PLAYERBZ_content_path)
#            if(len(files)==0):
#                log('NO MARKETING FILES DOWNLOADED! SYNC IS NEEDED')
#                #PLAYERBZ_get_marketinglist()
#                PLAYERBZ_sync_needed=1
            for file in os.listdir(PLAYERBZ_content_path):
                file_listed=0
                #log('REVERSE TEST FOR %s'%file)
                for obj in synclist.iter("file"):
                    filename=obj.find('filename').text
                    url=obj.find('url').text
                    if monitor.abortRequested():
                        return 1
                    if(file == filename):
                        file_listed=1
                        
                    if not os.path.exists(PLAYERBZ_content_path + filename):  
                        log('ERROR: FILE %s IN MARKETINGLIST WAS NOT DOWNLOADED. NEED PLAYLIST SYNC'%filename)
                        PLAYERBZ_sync_needed = 1

                if(file_listed == 0):
                    log('DEBUG: File %s not listed in marketinglist, deleting it'%file)
                    os.remove(PLAYERBZ_content_path+file)
                else:
                    log("INFO: MARKETINGLIST ADDED: %s%s"%(PLAYERBZ_content_path, file))
                    PLAYERBZ_marketing_content.append(PLAYERBZ_content_path + file)
                    
            if (PLAYERBZ_sync_needed == 0):
                log('DEBUG: MARKETINGLIST SYNC NOT NEEDED')
                return 1 
            
            PLAYERBZ_marketing_content=[]
            #forward sync
            log('DEBUG: STARTING MARKETINGLIST SYNC')
            for obj in synclist.iter("file"):
                if monitor.abortRequested():
                    return 1  
                    
                filename=obj.find('filename').text
                url=obj.find('url').text
                log("DEBUG: FILE: %s %s"%(filename, url))
                
                if not os.path.exists(PLAYERBZ_content_path + filename):
                    if os.path.exists(PLAYERBZ_content_path + filename + '.download'):
                        log('INFO: BROKEN DOWNLOAD, REMOVING: %s'%(PLAYERBZ_content_path + filename))
                        os.remove(PLAYERBZ_content_path + filename +'.download')

                    log('DEBUG: DOWNLOADING %s'%url)
                    try:
                        urllib.urlcleanup()
                        res = urllib.urlretrieve(url, PLAYERBZ_content_path + filename + '.download')
                        try:
                            log('INFO: MARKETING FILE DOWNLOADED FROM URL:%s'%url)
                            os.rename(PLAYERBZ_content_path + filename + '.download', PLAYERBZ_content_path + filename)
                        except:
                            log('ERROR: CANT RENAME %s'%(PLAYERBZ_content_path + filename + '.download! File will be remooved at next sync'))
                    except Exception as e:
                        log('ERROR: CANNOT DOWNLOAD %s:%s'%(url,e))

                if os.path.exists(PLAYERBZ_content_path + filename):
                    PLAYERBZ_marketing_content.append(PLAYERBZ_content_path + filename)
                    log("INFO: MARKETINGLIST ADDED: %s%s"%(PLAYERBZ_content_path, filename))
        else:
            log('ERROR: W R O N G   M A R K E T I N G   P L A Y L I S T   F O R M A T')
            PLAYERBZ_get_marketinglist()
    else:
        log('ERROR: MARKETINGLIST NOT EXIST')
        PLAYERBZ_get_marketinglist()
    return 1 

##########################################################################################

def PLAYERBZ_get_marketinglist():
    global PLAYERBZ_marketinglist_content
    #PLAYERBZ_playlist_content=[]
    request_status=0
    log('DEBUG: GET SERVER MARKETINGLIST')

    if (PLAYERBZ_module_mac == ''):
        log('ERROR: Object not defined %s'%(PLAYERBZ_module_mac))
        return 0
        
    PLAYERBZ_sync_needed=0
    
    try:
        conn = httplib.HTTPConnection(PLAYERBZ_server)
    except Exception as e:
        log('ERROR: CANT OPEN CONNECTION TO %s:%s'%(PLAYERBZ_server,e))
        
    try:
        conn.request("GET", "/modulecontrol/marketing/?module_id=%s&ver=%s"%(PLAYERBZ_module_mac, PLAYERBZ_version))
        res = conn.getresponse()
        request_status=res.status
    except Exception as e:
        log('ERROR: Connection error: %s'%e)
            
    if request_status == 200:
        log('DEBUG: MARKETING LIST recieved succesfull')
        servlist = res.read()
        try:
            synclist = xmlet.fromstring(servlist)
        except Exeption as e:
            log("ERROR: ERROR READING XML: %s"%e)
            return 0
        
        fplaylist = open(PLAYERBZ_marketing_playlist_path, 'w')
        fplaylist.write("%s"%servlist)
        fplaylist.close()
        PLAYERBZ_load_marketinglist()            
    else:
        log('ERROR: ERROR RECIEVING PLAYLIST:%s'%request_status)
        
##########################################################################################

def PLAYERBZ_insert_play(t):
    log('DEBUG: MARKETING PLAY FUNCTION. MARKETINC CONTENT TOTALL: %s'%(len(PLAYERBZ_marketing_content)))
    global PLAYERBZ_before_insert_time
    global PLAYERBZ_marketing_time
    global PLAYERBZ_marketing_position
    global PLAYERBZ_schedule_set
    
    if (len(PLAYERBZ_marketing_content)>0):
        PLAYERBZ_schedule_set=0
        PLAYERBZ_marketing_time = 1
        if PLAYERBZ_before_insert_time < 1:
            if player.isPlaying():
                PLAYERBZ_before_insert_time=player.getTime()
            else:
                PLAYERBZ_before_insert_time=0
            
        '''
        if(PLAYERBZ_marketing_position>=len(PLAYERBZ_marketing_content)):
            PLAYERBZ_marketing_position=0
            PLAYERBZ_marketing_time=0
        '''

        if os.path.exists(PLAYERBZ_marketing_content[PLAYERBZ_marketing_position]):
            player.play(PLAYERBZ_marketing_content[PLAYERBZ_marketing_position])
            xbmc.executebuiltin('ActivateWindow(12005)');
            xbmc.executebuiltin('PlayerControl("RepeatOff")')

    #first step - fix current track

    #second step - locate track in playlist
    #third step - fix current play position
    #fourth step - stop playing
    #fifth step - play marketing playlist
    #sixth step - load back main playlist
    #seventh step - find track
    #eighth step - seek to time we stop
    #tenth step - start playback

##########################################################################################

def PLAYERBZ_play_main_content():
    log('DEBUG: MAIN CONTENT PLAY FUNCTION')
    global PLAYERBZ_before_insert_position
    global PLAYERBZ_marketing_time

    PLAYERBZ_marketing_time=0
    if (len(PLAYERBZ_playlist_content)>0):
        if(PLAYERBZ_before_insert_position>=len(PLAYERBZ_playlist_content)):
            log('WARN: PLAYLIST COUNTER OVERFLOW ON PLAY MAIN CONTEN FUNCTION. THIS IS SHIT')
            PLAYERBZ_before_insert_position=0
            
        if os.path.exists(PLAYERBZ_playlist_content[PLAYERBZ_before_insert_position]):
            player.play(PLAYERBZ_playlist_content[PLAYERBZ_before_insert_position])
            log('DEBUG: PLAYING NORMAL: %s : %s' %(PLAYERBZ_before_insert_position, PLAYERBZ_playlist_content[PLAYERBZ_before_insert_position]))
        else:
            log('WARN: NORMAL CONTENT FILE NOT EXISTS %s'%(PLAYERBZ_playlist_content[PLAYERBZ_before_insert_position]))
            PLAYERBZ_build_play_list()
    else:
        log('INFO: NOTHING TO PLAY len:%s'%(len(PLAYERBZ_playlist_content)))
            
    xbmc.executebuiltin('PlayerControl("RepeatAll")')
    xbmc.executebuiltin('Dialog.Close(all,true)')     
    
##########################################################################################

def PLAYERBZ_reboot():
    log('INFO: REBOOT FUNCTION')
    xbmc.executebuiltin('Reboot')     

##########################################################################################

class mPlayer(xbmc.Player):
    def __init__(self, *args):
        xbmc.Player.__init__(self)    
        
    def onPlayBackEnded(self):
        global PLAYERBZ_playlist_position
        global PLAYERBZ_marketing_position
        global PLAYERBZ_marketing_time
        global PLAYERBZ_before_insert_position
        global PLAYERBZ_schedule_set
        log('DEBUG: PLAYBACK ENDED; MARKETING STATUS %s | MARKETING POSITION/TOTAL %s/%s PLAYLIST POSITION/TOTAL %s/%s '%(PLAYERBZ_marketing_time, PLAYERBZ_marketing_position, len(PLAYERBZ_marketing_content), PLAYERBZ_before_insert_position, len(PLAYERBZ_playlist_content)))
        if PLAYERBZ_marketing_time == 0:
            PLAYERBZ_before_insert_position=PLAYERBZ_before_insert_position+1
            #PLAYERBZ_before_insert_time=0
            if (PLAYERBZ_before_insert_position == len(PLAYERBZ_playlist_content)):
                log('DEBUG: PLAYLIST END REACHED. NULLING COUNTER')
                PLAYERBZ_before_insert_position=0
            PLAYERBZ_play_main_content()
        
        if PLAYERBZ_marketing_time == 1:
            PLAYERBZ_marketing_position=PLAYERBZ_marketing_position+1
            if (PLAYERBZ_marketing_position >= len(PLAYERBZ_marketing_content)):
                log('DEBUG: MARKETING ENDED. Resuming normal playlist')
                        
                if PLAYERBZ_sheduletime > 0:
                    log("DEBUG: SCHEDULLING MARKETING REPEAT TIMER :%s SECONDS"%PLAYERBZ_sheduletime)
                    PLAYERBZ_schedule_set=1
                    arg=[]
                    arg.append(PLAYERBZ_sheduletime)                
                    Timer(PLAYERBZ_sheduletime, PLAYERBZ_insert_play, arg).start()
                PLAYERBZ_marketing_position=0
                PLAYERBZ_marketing_time=0
                PLAYERBZ_play_main_content()
            else:
                log('DEBUG: PLAYING NEXT MARKETING FILE')
                PLAYERBZ_insert_play(1)

    def onPlayBackStopped(self):
        log('DEBUG: ************************ PLAYBACK STOPED')

    def onPlayBackStarted(self):
        global PLAYERBZ_before_insert_time
        global PLAYERBZ_schedule_set
        if not os.path.exists(PLAYERBZ_playlist_content[PLAYERBZ_before_insert_position]):
            log('ERROR: TRYING TO PLAY NOT EXISTING FILE. WILL STOP AND RESYNC.')
            playert(stop)
            PLAYERBZ_build_play_list()
            PLAYERBZ_play_main_content()
            
        log('DEBUG: PLAYBACK S T A R T E D; MARKETING STATUS %s | LAST TIME %s |  MARKETING POSITION/TOTAL %s/%s PLAYLIST POSITION/TOTAL %s/%s, file: %s '%(PLAYERBZ_marketing_time, PLAYERBZ_before_insert_time, PLAYERBZ_marketing_position, len(PLAYERBZ_marketing_content), PLAYERBZ_before_insert_position, len(PLAYERBZ_playlist_content), PLAYERBZ_playlist_content[PLAYERBZ_before_insert_position]))
        
        #xbmc.executebuiltin('Dialog.Close(all,true)')
        if(PLAYERBZ_marketing_time == 0):
            if (not player.isPlaying()):
                log('DEBUG: PLAYER IS NOT PLAYING !!!!!!!!!!!!!!!!!!!!!!')
            else:
                if PLAYERBZ_before_insert_time > 0:
                    log("DEBUG: PLAY AND JUMP TO TIME: %s"%PLAYERBZ_before_insert_time)
                    player.seekTime(PLAYERBZ_before_insert_time)
                    PLAYERBZ_before_insert_time=0
                else:
                    log('DEBUG: SEKING IS NOT NEED %s'%PLAYERBZ_before_insert_time)
                PLAYERBZ_before_insert_time=0
        
        xbmc.executebuiltin('ActivateWindow(12005)')
        xbmc.executebuiltin('Dialog.Close(all,true)')
            
        
player  = mPlayer() 