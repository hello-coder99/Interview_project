from flask import Flask,render_template,request
from send import direct_bp
from check_url import register_url
app=Flask(__name__)
app.register_blueprint(direct_bp,url_prefix='/d')

def get_server_ip():

    # Method B: Fetch from the local system socket (reliable fallback)
    try:
        # Connects to an external dummy IP to find the outbound network interface IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        server_ip_socket = s.getsockname()[0]
        print(server_ip_socket)
        s.close()
    except Exception:
        server_ip_socket = "127.0.0.1"
    return server_ip_socket

@app.route("/",methods=["GET","POST"])
def home():
    h_url="None"
    h2_url="None"
    if request.method=="POST":
        url=request.form.get("url")
        h2_url="http://"+get_server_ip()+"/d/"
        h_url="http://localhost/d/"
        u_cod=register_url(url)
        h_url=h_url+u_cod
        h2_url=h2_url+u_cod
        return render_template("index.html",h_url=h_url,h2_url=h2_url)
    return render_template("index.html",h_url=h_url,h2_url=h2_url)

if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)
