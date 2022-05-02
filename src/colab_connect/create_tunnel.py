from pyngrok import ngrok

class Ngrok:
    def __init__(self,token=None) -> None:
        if token:
            ngrok.set_auth_token(token)

    def tcp(self,host_or_port):
        return ngrok.connect(host_or_port,'tcp')

    def http(self,host_or_port):
        return ngrok.connect(host_or_port,'http')

    def kill(self):
        ngrok.kill()

    def disconnect(self,public_url):
        ngrok.disconnect(public_url)
    
    def get_tunnels(self):
        return ngrok.get_tunnels()


class Cloudflare:
    def __init__(self,with_auth=False) -> None:
        pass