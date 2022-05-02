import json
import os

class File:
    def __init__(self,path) -> None:
        self.path = path
    
    #read file
    def read(self):
        with open(self.path,'r') as f:
            return f.read()

    #write file
    def write(self,text):
        with open(self.path,'w') as f:
            f.write(text)
    
    def jdump(self,data):
        with open(self.path,'w') as f:
            json.dump(data,f)
    
    def jload(self):
        with open(self.path,'r') as f:
            return json.load(f)
    
    @staticmethod
    def exists(path):
        return os.path.exists(path)

def safe_username(username):
    #linux safe username
    return username.replace('/','_')