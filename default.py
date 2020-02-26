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
from settings import *
from functions import *

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

       
##########################################################################################


if __name__ == '__main__':
    global PLAYERBZ_before_insert_position
    global PLAYERBZ_last_updates_check
    global PLAYERBZ_playcheck_count
    xbmc.executebuiltin('Notification("Player.bz","System started ver %s")'%(PLAYERBZ_version))
    xbmc.executebuiltin('Notification("Player.bz","MODULE ID %s")'%(PLAYERBZ_module_mac))
    log('_______________________________________________________')
    log('Service started ver %s'%(PLAYERBZ_version))
    xbmc.executebuiltin('PlayerControl("RepeatAll")')
    xbmc.executebuiltin('PlayerControl("RandomOff")')
    xbmc.executebuiltin('Container.SetSortMethod(20)')
    xbmc.executebuiltin('UpdateAddonRepos')
    xbmc.executebuiltin('ActivateWindow(12005)');
    Timer(PLAYERBZ_sendlogstimer, send_log_files).start()
    Timer(PLAYERBZ_reboottimer, PLAYERBZ_reboot).start()
    try:
        conn = httplib.HTTPConnection(PLAYERBZ_server)
    except:
        log('ERROR: CANT OPEN CONNECTION TO %s'%PLAYERBZ_server)
        pass
        
    try:
        conn.request("GET", "/modulecontrol/startup/?module_id=%s&ver=%s"%(PLAYERBZ_module_mac, PLAYERBZ_version))
    except:
        log('INFO: STARTUP MARK ERROR')    
        pass
    
    player.stop()
    if (not os.path.exists('/home/xbian/.kodi/userdata/player.bz')):
    	os.mkdir('/home/xbian/.kodi/userdata/player.bz')
    	
    if (not os.path.exists('/home/xbian/storage')):
    	os.mkdir('/home/xbian/storage')
    	
    if (not os.path.exists('/home/xbian/storage/player.bz')):
    	os.mkdir('/home/xbian/storage/player.bz')
    	
    if (not os.path.exists('/home/xbian/storage/player.bz/playlist')):
    	os.mkdir('/home/xbian/storage/player.bz/playlist')    	
    	
    if (not os.path.exists('/home/xbian/storage/player.bz/video')):
    	os.mkdir('/home/xbian/storage/player.bz/video') 
    	
    if (not os.path.exists('/home/xbian/storage/player.bz/audio')):
    	os.mkdir('/home/xbian/storage/player.bz/audio')  
    	
    if (not os.path.exists('/home/xbian/storage/player.bz/image')):
    	os.mkdir('/home/xbian/storage/player.bz/image') 
    	
    if (not os.path.exists('/home/xbian/storage/player.bz/marketing')):
    	os.mkdir('/home/xbian/storage/player.bz/marketing')     	    	  	     	    	
    
    if (os.path.exists(PLAYERBZ_logo_path)):
        log('Showing logo at %s'%(PLAYERBZ_logo_path))
        xbmc.executebuiltin('PlayMedia("%s")' % PLAYERBZ_logo_path)
    
    PLAYERBZ_build_play_list()
    PLAYERBZ_play_main_content()
    PLAYERBZ_update_play_list()
    log('INFO: START MONITORING')
    #while not monitor.abortRequested():
    while not monitor.waitForAbort(1):
        if (PLAYERBZ_module_mac == ''):
            log('DEBUG: OBJECT NOT DEFINED! I AM OUT!!!!')
            break
        # Sleep/wait for abort for 3 secs
#        if monitor.waitForAbort(0):
#            log('EXIT REQUESTED. GOOD BYE')
#            player.stop()
            # Abort was requested while waiting. We should exit
#            break    
        #Repository sync timer
        
        PLAYERBZ_minutes_passed_last_update_check=int((time.time()-PLAYERBZ_last_updates_check)/60)
        #log('Minutes passed repo sync %s'%PLAYERBZ_minutes_passed_last_update_check)
        if (PLAYERBZ_repository_update_interval <= PLAYERBZ_minutes_passed_last_update_check):
            log('INFO: REPO UPDATE BY TIMER %s'%PLAYERBZ_playlist_sync_interval )
            PLAYERBZ_last_updates_check=time.time()
            xbmc.executebuiltin('UpdateAddonRepos')
        #Playlist sync timer
        PLAYERBZ_minutes_passed_last_playlist_sync=int((time.time()-PLAYERBZ_last_playlist_sync)/60)
        #log('Minutes passed plylist sync %s'%PLAYERBZ_minutes_passed_last_playlist_sync)
        if (PLAYERBZ_playlist_sync_interval <= PLAYERBZ_minutes_passed_last_playlist_sync):
            log('INFO: PLAYLIST UPDATE BY INTERVAL %s'%PLAYERBZ_playlist_sync_interval )
            PLAYERBZ_last_playlist_sync=time.time()
            PLAYERBZ_update_play_list()            
                
        if (not player.isPlaying()):
            PLAYERBZ_playcheck_count=PLAYERBZ_playcheck_count+1
            if PLAYERBZ_playcheck_count >= 4:
                log('INFO: PLAYBACK WATCHDOG: NOT PLAYING 2 SEC - RESTART PLAYING')
                PLAYERBZ_playcheck_count=0
                if PLAYERBZ_marketing_time == 1:
                    PLAYERBZ_insert_play(1)
                else:
                    PLAYERBZ_play_main_content()
