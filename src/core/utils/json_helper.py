import json 

class ToStrEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return str(obj)
        except:
            return super().default(obj)
        