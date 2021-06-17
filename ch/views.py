# imports

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict


from .utils import HttpJSONError, CHException, DummyException, HttpJSONResponse, HttpRecordsResponse, log
from .utils import handleException, extractParams
from .utils import headers, encode

from url_magic import makeView

from hypertrack.rest import Client
from hypertrack.exceptions import HyperTrackException

###########################################
# Types
###########################################
Filename = str

###########################################
# Constants
###########################################
makeView.APP_NAME = 'ch'

##############################################################################
# General Views
##############################################################################


@makeView()
@csrf_exempt
@handleException(IndexError, 'Admin Not found', 404)
@handleException(KeyError, 'Invalid params', 501)
@extractParams
def adminGenUrl(_, dct):
    """
    Makes the supervisor login
    -----------------------------------------

    HTTPS args:
        url: the unique url id of a Clubhouse room
    -----------------------------------------
    Returns:
        nurl : the url generated
    -----------------------------------------

    """
    sURL = encode(str(dct['url']), settings.BASE62)
    ret = {'nurl': sURL}
    return HttpJSONResponse(ret)
