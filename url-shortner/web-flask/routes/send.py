from flask import Blueprint,redirect,abort

direct_bp=Blueprint("direct",__name__)

@direct_bp.route("<g_url>")
def redirect_url(g_url):
    #get actual url by the help of short code until now its hard coded
    actual_url="https://www.google.com/"
    if actual_url:
        return redirect(actual_url)
    return abort(404)
