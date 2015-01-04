# !/usr/bin/python
# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License,published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import subprocess
import os
import string

from module.plugins.Hook import Hook
from module.utils import save_join


class FileBot(Hook):
    __name__ = "FileBot"
    __version__ = "0.14"
    __config__ = [("activated", "bool", "Activated", "False"),


                  ("destination", "folder", "destination folder", ""),
  
                  ("logfile", "str", "log file path", ""),
   
                  ("loglevel", """off;warning;info;config;all""", "log level", "info"),

                  ("conflict", """skip;override""", "conflict handling", "override"),

                  ("action", """move;copy;test""", "copy, move or test(dry run)", "move"),

                  ("lang", "str", "language (en, de, fr, es, etc)", ""),

                  ("subtitles", "str", "subtitles language (en, de, fr, es, etc)", ""),

                  ("unsorted", """y;n""", "sort out files that cannot be proceed to $destination/unsorted/", "n"),

                  ("ignore", "str", "ignore files (regex)", ""),

                  ("artwork", """y;n""", "download artwork", "n"),

                  ("clean", """y;n""", "clean folder from clutter thats left behind", "y"),

                  ("movie", "str", "movie destination (relative to destination or absolute)", ""),

                  ("series", "str", "series destination (relative to destination or absolute)", ""),

                  ("music", "str", "music destination (relative to destination or absolute)", ""),

                  ("anime", "str", "anime destination (relative to destination or absolute)", ""),

                  ("gmail", "str", "gmail login (without @gmail.com)", ""),
                  ("gmailpw", "password", "gmail password", ""),

                  ("mail", "str", "mail (host:port:from)", ""),
                  ("mailto", "str", "mailto", ""),

                  ("excludeList", "str", "exclude list file", "pyload-amc.txt"),

                  ("myepisodes", "str", "myepisodes login", " "),
                  ("myepisodespw", "password", "myepisodes password", " "),

                  ("pushover", "str", "pushover user key", ""),

                  ("pushbullet", "str", "pushbullet api key", ""),

                  ("xbmc", "str", "xbmc hostname", ""),

                  ("plex", "str", "plex hostname", ""),

                  ("reportError", """y;n""", "report error via email", "n"),

                  ("filebot", "str", "filebot executable", "filebot"),

                  ("exec", "str", "additional exec script", ""),

                  ("storeReport", """y;n""", "save reports to local filesystem", "n"),
                  
                  ("historyfile", "str", "rename history file", ""),

                  ("extensions","list","comma-separated file extensions to process, that are not archives ","mkv,mp4,ts,avi,wmv,mpeg")]

    __description__ = "automated renaming and sorting for tv episodes movies, music and animes"
    __author_name__ = ("Branko Wilhelm", "Kotaro", "Gutz-Pilz")
    __author_mail__ = ("branko.wilhelm@gmail.com", "screver@gmail.com", "unwichtig@gmail.com")

    
    event_list = ["downloadFinished","archive_extracted","unrarFinished"]

    def archive_extracted(self, pyfile, folder, fname, extracted_files):
        self.Finished(folder)

    def unrarFinished(self, folder, fname):
        self.Finished(folder,"unrarFinished")
        
      
    def downloadFinished(self, pyfile):
        filename =  os.path.splitext(pyfile.name)
        extensions = string.split(self.getConf("extensions"), ',')
        
        if filename[1].replace('.','') in extensions:
            package = pyfile.package()
            folder  = save_join(self.config['general']['download_folder'], package.folder)
            self.Finished(folder)


    def Finished(self, folder):
        args = []  # http://www.filebot.net/forums/viewtopic.php?f=4&t=215&p=1561

        self.logDebug(folder)

        if self.getConfig('filebot'):
            args.append(self.getConfig('filebot'))
        else:
            args.append('filebot')

        args.append('-script')
        args.append('fn:amc')

        args.append('-non-strict')

        args.append('--log')
        args.append(self.getConfig('loglevel'))

        args.append('--log-file')
        args.append(self.getConfig('logfile'))

        args.append('-r')

        args.append('--conflict')
        args.append(self.getConfig('conflict'))

        args.append('--action')
        args.append(self.getConfig('action'))

        if self.getConfig('destination'):
            args.append('--output')
            args.append(self.getConfig('destination'))
        else:
            args.append('--output')
            args.append(folder)

        if self.getConfig('lang'):
            args.append('--lang')
            args.append(self.getConfig('lang'))

        # start with all definitions:
        args.append('--def')

        if self.getConfig('exec'):
            args.append('exec=' + self.getConfig('exec'))

        if self.getConfig('clean'):
            args.append('clean=' + self.getConfig('clean'))

        if self.getConfig('mail'):
            args.append('mail=' + self.getConfig('mail'))

        if self.getConfig('mailto'):
            args.append('mailto=' + self.getConfig('mailto'))

        args.append('skipExtract=y')

        if self.getConfig('excludeList'):
            args.append('excludeList=' + self.getConfig('excludeList'))

        if self.getConfig('reportError'):
            args.append('reportError=' + self.getConfig('reportError'))

        if self.getConfig('storeReport'):
            args.append('storeReport=' + self.getConfig('storeReport'))

        if self.getConfig('artwork'):
            args.append('artwork=' + self.getConfig('artwork'))

        if self.getConfig('subtitles'):
            args.append('subtitles=' + self.getConfig('subtitles'))

        if self.getConfig('ignore'):
            args.append('ignore=' + self.getConfig('ignore'))

        if self.getConfig('unsorted'):
            args.append('unsorted=' + self.getConfig('unsorted'))

        if self.getConfig('gmail') and self.getConfig('gmailpw'):
            args.append('gmail=' + self.getConfig('gmail') + ':' + self.getConfig('gmailpw'))

        if self.getConfig('myepisodes') and self.getConfig('myepisodespw'):
            args.append('myepisodes=' + self.getConfig('myepisodes') + ':' + self.getConfig('myepisodespw'))

        if self.getConfig('pushover'):
            args.append('pushover=' + self.getConfig('pushover'))

        if self.getConfig('pushbullet'):
            args.append('pushbullet=' + self.getConfig('pushbullet'))

        if self.getConfig('xbmc'):
            args.append('xbmc=' + self.getConfig('xbmc'))

        if self.getConfig('plex'):
            args.append('plex=' + self.getConfig('plex'))

        if self.getConfig('movie'):
            args.append('movieFormat=' + self.getConfig('movie'))

        if self.getConfig('series'):
            args.append('seriesFormat=' + self.getConfig('series'))

        if self.getConfig('music'):
            args.append('musicFormat=' + self.getConfig('music'))
        else:
            args.append('music=n')

        if self.getConfig('anime'):
            args.append('animeFormat=' + self.getConfig('anime'))

        args.append(folder)

        try:
            p = subprocess.Popen(args, bufsize=-1)
            self.logInfo('executed')
            self.logDebug(' '.join(args))
            p.wait()
        except Exception, e:
            self.logError(str(e))

        try:
            if self.getConfig('historyfile'):
                self.logInfo('generating history file')
                fb = ''
                if self.getConfig('filebot'):
                    fb = self.getConfig('filebot')
                else:
                    fb = 'filebot'
                
                historyargs = fb + ' -script fn:history > "' + self.getConfig('historyfile') + '"'
                self.logDebug(historyargs)
                p = subprocess.Popen(historyargs, bufsize=-1, shell=True)
                
                p.wait()
        except Exception, e:
            self.logError(str(e))
