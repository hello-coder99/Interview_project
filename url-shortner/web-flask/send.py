from flask import Blueprint,redirect,abort
from check_url import fetch_url
direct_bp=Blueprint("direct",__name__)

@direct_bp.route("<g_code>")
def redirect_url(g_code):
    actual_url=fetch_url(g_code)
    if actual_url:
        return redirect(actual_url)
    return abort(404)

