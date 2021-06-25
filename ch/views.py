# imports

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict


from .utils import HttpJSONError, CHException, DummyException, HttpJSONResponse, HttpRecordsResponse, log
from .utils import handleException, extractParams
from .utils import headers, encode, decode

from url_magic import makeView

from .models import Admin, User, Page, Post

###########################################
# Types
###########################################
Filename = str

###########################################
# Constants
###########################################
makeView.APP_NAME = 'ch'

##############################################################################
# Admin Views
##############################################################################


@makeView()
@csrf_exempt
@handleException(IndexError, 'Admin Not found', 404)
@handleException(KeyError, 'Invalid params', 501)
@extractParams
def adminGenPage(_, dct):
    """
    Makes the admin generate the URL for the notepad
    -----------------------------------------

    HTTPS args:
        url: the unique url id of a Clubhouse room
        eg = https://www.clubhouse.com/room/xl4QgdZ4
    -----------------------------------------
    Returns:
        {}
    -----------------------------------------

    """
    sURL = decode(str(dct['url']).split('/')[4], settings.BASE62)

    # check whether the page already exists or not
    checkPage = Page.objects.filter(nurl=sURL)

    page = Page() if len(checkPage) == 0 else checkPage[0]
    page.nurl = sURL
    page.save()

    log('new page generated: %s' % page.nurl)

    return HttpJSONResponse({})


@makeView()
@csrf_exempt
@handleException(IndexError, 'Admin Not found', 404)
@handleException(KeyError, 'Invalid params', 501)
@extractParams
def adminApprovePost(_, dct):
    """
    Admin approves the post by any user
    -----------------------------------------

    HTTPS args:
        txt : text containing the link or other stuff
    -----------------------------------------
    Returns:
        {}
    -----------------------------------------

    """
    post = Post()
    post.txt = dct['txt']
    post.save()

    log('new post approved: %s' % post.txt)
    return HttpJSONResponse({})


@makeView()
@csrf_exempt
@handleException(IndexError, 'Admin Not found', 404)
@handleException(KeyError, 'Invalid params', 501)
@extractParams
def adminDisapprovePost(_, dct):
    """
    Admin disapproves the post by any user
    -----------------------------------------

    HTTPS args:
    -----------------------------------------
    Returns:
        {}
    -----------------------------------------

    """
    log('post approved!')
    return HttpJSONResponse({})


@makeView()
@csrf_exempt
@handleException(IndexError, 'Admin Not found', 404)
@handleException(KeyError, 'Invalid params', 501)
@extractParams
def adminDeletePost(_, dct):
    """
    Admin deletes the post by any user
    -----------------------------------------

    HTTPS args:
        id : is of the post
    -----------------------------------------
    Returns:
        {}
    -----------------------------------------

    """
    Post.objects.filter(id=dct['id'])[0].delete()
    return HttpJSONResponse({})


@makeView()
@csrf_exempt
@handleException(IndexError, 'Admin Not found', 404)
@handleException(KeyError, 'Invalid params', 501)
@extractParams
def adminEndPage(_, dct):
    """
    Admin ends the page
    -----------------------------------------

    HTTPS args:
    -----------------------------------------
    Returns:
        {}
    -----------------------------------------

    """
    # TODO
    # set this up correctly
    return HttpJSONResponse({})


##############################################################################
# User Views
##############################################################################


@makeView()
@csrf_exempt
@handleException(IndexError, 'Admin Not found', 404)
@handleException(KeyError, 'Invalid params', 501)
@extractParams
def userAddPost(_, dct):
    """
    user adds a post
    -----------------------------------------

    HTTPS args:
        txt : text containing the link or other stuff
    -----------------------------------------
    Returns:
        {}
    -----------------------------------------

    """
    log('new post added by user: %s' % dct['txt'])

    return HttpJSONResponse({})
