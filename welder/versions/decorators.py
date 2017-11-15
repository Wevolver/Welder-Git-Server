from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseForbidden
from django.conf import settings
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def catch(func):
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        if settings.DEBUG:
             return func(request, *args, **kwargs)
        try:
            return func(request, *args, **kwargs)
        except json.decoder.JSONDecodeError as e:
            response = HttpResponseBadRequest("The requested path parameter doesn't exist!")
        except FileExistsError as e:
            response = HttpResponseBadRequest("looks like you already have a project with this name!")
        except OSError as e:
            response = HttpResponseBadRequest("You already have a project with this name")
        except FileNotFoundError as e:
            response = HttpResponseBadRequest("Not a repository.")
        except pygit2.GitError as e:
            response = HttpResponseBadRequest("Not a git repository")
        except AttributeError as e:
            response = HttpResponseBadRequest("No path parameter")
        except KeyError as e:
            response = HttpResponseBadRequest("The requested path doesn't exist!")
        except TypeError as e:
            response = HttpResponseBadRequest("The file doesn't exist!")
        except Exception as e:
            logger.info(e)
    return _decorator
