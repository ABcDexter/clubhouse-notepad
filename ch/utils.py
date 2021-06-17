# imports
import datetime
import json
import os
import sys
import re
from datetime import datetime, timedelta
from json import JSONDecodeError
from functools import wraps

import logging
from django.conf import settings
from django.utils import timezone
import csv

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

from .models import Admin, User

from django.conf import settings
import requests
from urllib.parse import urlencode

from math import ceil

logger = logging.getLogger('ch')


def log(x: str):
    logger.debug(x)


###########################################
# Utility functions and classes


def errMsg(err, status=501):
    return{'error': err, 'status': status}


def HttpJSONResponse(data, status:int=None):
    return HttpResponse(json.dumps(data), content_type='application/json', status=status)


def HttpRecordsResponse(data, status:int=None):
    ret = json.dumps(list(data), cls=DjangoJSONEncoder)
    return HttpResponse(ret, content_type='application/json', status=status)


def HttpJSONError(err, status=501):
    return HttpResponse(json.dumps(errMsg(err, status)), content_type='application/json')


class CHException(Exception):
    """
    Custom exception with status and message
    -----------------------------------------
    """
    def __init__(self, status, message):
        self.status = status
        self.message = message

    # return HTTPJsonResponse with code and message
    def response(self):
        return HttpJSONResponse(errMsg(self.message, self.status))


class DummyException(Exception):
    pass


##########################################
# Helpers/Algorithms

###########################################

sys.path.insert(0, os.path.dirname(__file__))

############################################
logging.warning('Leave the Matrix!')

############################################
# Constants

sLogDIRName = settings.LOG_DIR
sLogFileName = sLogDIRName + "logFile.csv"
field_names = ['api', 'timestampUTC', 'timestampIST', 'response']

###########################################
# Functions
###########################################

def logEvent(funcName, status):
    """
    Logs the event to the file
    -----------------------------------------
    funName is the API being hit,
    status is the JSON reponse
    -----------------------------------------

    """
    currTimeUTC = timezone.now()
    tdISTdelta  = timedelta(hours=5, minutes=30)
    currTimeIST = currTimeUTC + tdISTdelta

    # Writing to a CSV
    with open(sLogDIRName, 'a+', encoding='utf-8') as file:
        csvwriter = csv.DictWriter(file, field_names)

        csvwriter.writerow({'api': funcName, 'timestampUTC': currTimeUTC, 'timestampIST': currTimeIST, 'response': status})


###########################################
# Decorators
###########################################
def extractParams(func):
    """
    Decorator applied to a view function to retrieve GET/POST data as a dict
    -----------------------------------------

    POST is treated as JSON
    -----------------------------------------

    """
    def _decorator(request):
        log('extractParams:' + func.__name__)
        if request.method == 'GET':
            dct = dict(request.GET.items())

        else:
            # log(request.body.decode('utf-8'))
            dct = dict(json.loads(request.body.decode('utf-8')))
        return func(request, dct)

    return wraps(func)(_decorator)


class checkAuth(object):
    """
    Decorator class that performs authentication with auth=dct[auth] and returns the object
    -----------------------------------------
    Decides which table to check based on whether the function name starts with
    user, admin or
    auth (generic)
    -----------------------------------------

    """
    def __init__(self, driverMode=None):
        self.driverMode = driverMode
        pass

    def __call__(self, func):
        @wraps(func)
        def decorated_func(request, dct):
            # log('checkAuth:' + func.__name__)
            sFnName = func.__name__
            isUser = sFnName.startswith('user')
            isAdmin = sFnName.startswith('admin')
            isAuth = sFnName.startswith('auth')

            if isAdmin:
                if dct.get('auth', '') != settings.ADMIN_AUTH:
                    return HttpJSONError('Forbidden', 403)
                else:
                    return func(dct)

            # If auth key checks out, then return JSON, else Unauthorized
            auth = dct.get('auth', '')
            print("auth is :", auth, "...")
            if isUser or isAuth:
                qsUser = User.objects.filter(auth=auth)
                if (qsUser is not None) and len(qsUser) > 0:
                    print("user : ", qsUser)
                    return func(dct, qsUser[0])

            return HttpJSONError('Unauthorized', 403)

        return decorated_func


class handleException(object):
    """
    handles exceptions and returns it as a HTTP response
    -----------------------------------------
    """

    def __init__(self, class_name=None, message=None, status=None):
        self.class_name = class_name or DummyException
        self.status = status
        self.message = message

    def __call__(self, func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except CHException as ex:
                log(repr(ex))
                return ex.response()
            # in case of unspecified message/code, dump the exception text itself
            except self.class_name as ex:
                log(repr(ex))
                return HttpJSONError(self.message or str(ex), self.status or 501)
            except Exception:
                # TODO
                # print out exceptions which I didn't handle and also throw it to get stack trace
                # log(e)
                raise

        return decorated_func


###########################################
# simple Helpers
###########################################

def headers(h):
    """
    Decorator adding arbitrary HTTP headers to the response.

    This decorator adds HTTP headers specified in the argument (map), to the
    HTTPResponse returned by the function being decorated.
    -----------------------------------------
    Example:

    @headers({'Refresh': '10', 'X-Bender': 'Bite my shiny, metal ass! cuz I'll be bach!'})
    def index(request):
    -----------------------------------------

    """
    def headers_wrapper(fun):
        def wrapped_function(*args, **kwargs):
            response = fun(*args, **kwargs)
            for k,v in h.iteritems():
                response[k] = v
            return response
        return wrapped_function
    return headers_wrapper


# TODO delete the URL

#############################
#  Encryption / Decryption
#############################

def encode(num, alphabet):
    """
    Encode a positive number into Base X and return the string.
    -----------------------------------------

    Arguments:
    - `num`: The number to encode
    - `alphabet`: The alphabet to use for encoding
    -----------------------------------------

    """
    num = int(num)
    if num == 0:
        return alphabet[0]
    arr = []
    arr_append = arr.append  # Extract bound-method for faster access.
    _divmod = divmod  # Access to locals is faster.
    base = len(alphabet)
    while num:
        num, rem = _divmod(num, base)
        arr_append(alphabet[rem])
    arr.reverse()
    return str(''.join(arr))


def decode(string, alphabet=settings.BASE62)-> str:
    """
    Decode a Base X encoded string into the number
    -----------------------------------------

    Arguments:
    - `string`: The encoded string
    - `alphabet`: The alphabet to use for decoding
    -----------------------------------------

    """
    base = len(alphabet)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1

    return str(num)

