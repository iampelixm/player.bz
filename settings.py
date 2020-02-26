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
import xbmc
import xbmcgui
import xbmcaddon
import time
import socket
import struct
import fcntl

##########################################################################################

def getHwAddr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

##########################################################################################

self=xbmcaddon.Addon('service.player.bz.xbian')
###http://mirrors.xbmc.org/docs/python-docs/13.0-gotham/xbmc.html#PlayList-getposition
##ADDON SETTINGS
PLAYERBZ_object = self.getSetting('player.bz_object')
PLAYERBZ_version = self.getAddonInfo('version')
PLAYERBZ_content_type=self.getSetting('player.bz_content_type')
PLAYERBZ_content_type='video'
PLAYERBZ_playlist_path='/home/xbian/storage/player.bz/playlist/normal.m3u'
PLAYERBZ_playlist_content = []
PLAYERBZ_playlist_position = 0
PLAYERBZ_marketing_content=[]
PLAYERBZ_marketing_position=0
PLAYERBZ_marketing_playlist_path = "/home/xbian/storage/player.bz/playlist/marketing.m3u"
PLAYERBZ_marketing_timelist_path = "/home/xbian/storage/player.bz/playlist/marketingtimelist.txt"

PLAYERBZ_video_storage_path="/home/xbian/storage/player.bz/video/"
PLAYERBZ_audio_storage_path="/home/xbian/storage/player.bzmusic/"
PLAYERBZ_image_storage_path="/home/xbian/storage/player.bz/image/"
PLAYERBZ_storage_path=PLAYERBZ_video_storage_path
PLAYERBZ_marketing_storage_path="/home/xbian/storage/player.bz/marketing/"

PLAYERBZ_logo_path='/home/xbian/storage/player.bz/logo.jpg'

PLAYERBZ_system_started=time.time()
PLAYERBZ_last_updates_check=time.time()
PLAYERBZ_last_playlist_sync=time.time()
PLAYERBZ_repository_update_interval=240
PLAYERBZ_insertplay_ready=0
PLAYERBZ_plaing_marketing=0

PLAYERBZ_playlist_sync_interval=20

PLAYERBZ_current_pos=0

PLAYERBZ_server='xbmc.xlitservice.pp.ru'

PLAYERBZ_module_id='noid'
PLAYERBZ_module_mac=getHwAddr("eth0")

PLAYERBZ_before_insert_position=0
PLAYERBZ_marketing_position=0
PLAYERBZ_before_insert_time=0

PLAYERBZ_sendlogstimer=3600
PLAYERBZ_sheduletime = 180
PLAYERBZ_reboottimer = 14200
PLAYERBZ_schedule_set=0

PLAYERBZ_marketing_time=0

PLAYERBZ_playcheck_count=0
PLAYERBZ_logfile="/home/xbian/.kodi/temp/playerbz.log"
PLAYERBZ_kodilogfile="/home/xbian/.kodi/temp/kodi.log"

PLAYERBZ_playlist_sync_in_progress=0

PLAYERBZ_shuffle_playlist=1

monitor = xbmc.Monitor()