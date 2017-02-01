# -*- coding: utf-8 -*-
#
# Repository path   : $HeadURL:  $
# Last committed    : $Revision:  $
# Last changed by   : $Author:  $
# Last changed date : $Date: $
#

"""Simple helper class for retrieving remote version information."""

from tmEditor.core import Settings
from distutils.version import StrictVersion
import logging
import json
import os

try:
    # Python 2
    from urllib2 import urlopen
    from urllib2 import URLError, HTTPError
    from urlparse import urljoin
except ImportError:
    # Python 3
    from urllib.request import urlopen
    from urllib.error import URLError, HTTPError
    from urllib.parse import urljoin

kName = 'name'
kVersion = 'version'
kMenu = 'menu'
kUri = 'uri'
kScaleSet = 'scale_set'
kExtSignalSet = 'ext_signal_set'

class RemoteVersionInfo(object):
    """Helper class for retrieving remote server side version info."""

    def __init__(self, url=None):
        self.name = None
        self.version = None
        self.scale_set_name = None
        self.scale_set_url = None
        self.ext_signal_set_name = None
        self.ext_signal_set_url = None
        if url: self.read_version(url)

    @property
    def is_valid(self):
        if self.name:
            if self.version:
                return True
        return False

    def read_url(self, url):
        r = urlopen(url)
        charset = r.info().get('charset') or 'utf-8'
        return r.read().decode(charset)

    def read_version(self, url):
        """Retrieve version information from remote server. Returns empty dict on error."""
        try:
            logging.debug("reading version information from: %s", url)
            data = json.loads(self.read_url(url))
            if data:
                self.load_json(data)
        except (URLError, HTTPError) as e:
            logging.warning("unable to retrieve version information from: %s", url)

    def load_json(self, data):
        """Load data from JSON dict."""
        baseurl = os.path.dirname(Settings.VersionUrl)
        application = data.get('application')
        if application:
            self.name = application.get(kName)
            self.version = application.get(kVersion)
            if self.version:
                self.version = StrictVersion(self.version)
        menu = data.get(kMenu)
        if menu:
            # Scale set
            scale_set = menu.get(kScaleSet)
            name = scale_set.get(kName)
            uri = scale_set.get(kUri)
            if name:
                if not uri:
                    uri = Settings.DefaultScaleSetUri.format(scale_set=name)
                url = urljoin(baseurl, uri)
            self.scale_set_name = name
            self.scale_set_url = url
            # External signal set
            ext_signal_set = menu.get(kExtSignalSet)
            name = ext_signal_set.get(kName)
            uri = ext_signal_set.get(kUri)
            if name:
                if not uri:
                    uri = Settings.DefaultExtSignalSetUri.format(ext_signal_set=name)
                url = urljoin(baseurl, uri)
            self.ext_signal_set_name = name
            self.ext_signal_set_url = url
