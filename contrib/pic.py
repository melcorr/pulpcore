# -*- coding: utf-8 -*-
#
# Copyright © 2011 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.

"""
Pulp Interactive Client
This module is meant to be imported to talk to pulp webservices interactively 
from an interpreter. It provides convenience methods for connecting to pulp as 
well as performing many common pulp tasks.
"""

import base64
import httplib
import json
import os
import sys
import types

_host = 'localhost'
_port = 443
_path_prefix = '/pulp/api'
_user = 'admin'
_password = 'admin'

# connection management -------------------------------------------------------

_connection = None

def connect():
    global _connection
    _connection = httplib.HTTPSConnection(_host, _port)

# requests --------------------------------------------------------------------

class RequestError(Exception):
    pass


def _auth_header():
    raw = ':'.join((_user, _password))
    encoded = base64.encodestring(raw)[:-1]
    return {'Authorization': 'Basic %s' % encoded}


def _request(method, path, body=None):
    if _connection is None:
        raise RuntimeError('You must run connect() before making requests')
    if not isinstance(body, types.NoneType):
        body = json.dumps(body)
    _connection.request(method,
                        _path_prefix + path,
                        body=body, 
                        headers=_auth_header())
    response = _connection.getresponse()
    response_body = response.read()
    try:
        response_body = json.loads(response_body)
    except:
        pass
    if response.staus > 299:
        raise RequestError('Server response: %d\n%s' % 
                           (response.status, response_body))
    return (response.status, response_body)


def GET(path):
    return _request('GET', path)


def PUT(path, body):
    return _request('PUT', path, body)


def POST(path, body=None):
    return _request('POST', path, body)


def DELETE(path):
    return _request('DELETE', path)

# repo management -------------------------------------------------------------

def create_repo(id, name=None, arch='noarch', **kwargs):
    """
    Acceptable keyword arguments are any arguments for a new Repo model.
    Common ones are: source and sync_schedule
    """
    kwargs.update({'id': id, 'name': name or id, 'arch': arch})
    return POST('/repositories/', kwargs)


def update_repo(id, **kwargs):
    """
    Acceptable keyword arguments are any arguments for a new Repo model.
    Common ones are: source and sync_schedule
    """
    return PUT('/repositories/%s/' % id, kwargs)

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    print >> sys.stderr, 'Not a script, import as a module in an interpreter'
    sys.exit(os.EX_USAGE)
