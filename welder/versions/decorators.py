from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.conf import settings
from functools import wraps
import pygit2
import json
import logging

logger = logging.getLogger(__name__)

def catch(func):
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except json.decoder.JSONDecodeError as e:
            response = HttpResponseBadRequest("Bad JSON")
            logger.info(e)
        except FileExistsError as e:
            response = HttpResponseBadRequest("You already have a project with this name")
            logger.info(e)
        except OSError as e:
            response = HttpResponseBadRequest("You already have a project with this name")
            logger.info(e)
        except FileNotFoundError as e:
            response = HttpResponseBadRequest("Not a repository.")
            logger.info(e)
        except pygit2.GitError as e:
            response = HttpResponseBadRequest("Pygit error")
            logger.info(e)
        except AttributeError as e:
            response = HttpResponseBadRequest("The necessary parameter doesn't exist")
            logger.info(e)
        except KeyError as e:
            response = HttpResponseBadRequest("The necessary parameter doesn't exist")
            logger.info(e)
        except TypeError as e:
            response = HttpResponseBadRequest("The file doesn't exist")
            logger.info(e)
        except Exception as e:
            logger.info(e)
        return response
    return _decorator
