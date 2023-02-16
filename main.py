"""
Exposes a simple HTTP API to search a users Gists via a regular expression.

Github provides the Gist service as a pastebin analog for sharing code and
other develpment artifacts.  See http://gist.github.com for details.  This
module implements a Flask server exposing two endpoints: a simple ping
endpoint to verify the server is up and responding and a search endpoint
providing a search across all public Gists for a given Github account.
"""

from flask import Flask, jsonify, request
from gistapi import gistapi_service

app = Flask(__name__)


@app.route("/api/v1/search", methods=['GET'])
def search():
    """Provides matches for a single pattern across a single users gists.
    Pulls down a list of all gists for a given user and then searches
    each gist for a given regular expression.
    Returns:
        A Flask Response object of type application/json.  The result
        object contains the list of matches along with a 'status' key
        indicating any failure conditions.
    """
    username = request.args.get('username')
    pattern = request.args.get('pattern')

    if not username or not pattern:
        raise ValueError("'username' or 'pattern' query parameter is missing from the url")

    matching_gist_urls_sync = gistapi_service.get_matching_gist_urls_sync(username, pattern)
    matching_gist_urls_async = gistapi_service.get_matching_gist_urls_async(username, pattern)

    result = {
        'status': 'success',
        'username': username,
        'pattern': pattern,
        'matches_sync': matching_gist_urls_sync,
        'matches_async': matching_gist_urls_async
    }

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9876)
