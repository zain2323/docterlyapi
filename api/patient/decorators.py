from api import cache
from flask import jsonify

# for caching the response of the endpoint with the id as the parameter
def cache_response_with_id(prefix):
    def cache_it(function):
        def inner(id):
            CACHE_KEY = prefix + str(id)
            if cache.has(CACHE_KEY):
                data = cache.get(CACHE_KEY)
                return jsonify(data)
            else:
                return function(id)
        inner.__name__ = function.__name__
        return inner
    return cache_it

# for caching the response of the endpoint usng token as the key
def cache_response_with_token(prefix, token):
    def cache_it(function):
        def inner():
            current_user = token.current_user()
            CACHE_KEY  = prefix + current_user.get_token()
            if cache.has(CACHE_KEY):
                data = cache.get(CACHE_KEY)
                return jsonify(data)
            else:
                return function()
        inner.__name__ = function.__name__
        return inner
    return cache_it