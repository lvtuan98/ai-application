import os
from app import create_app
from flask import jsonify, request
from dotenv import load_dotenv
load_dotenv()

app = create_app()

@app.route('/', methods = ['GET', 'POST']) 
def home(): 
  if(request.method == 'GET'): 
      data = "This is Backend"
      return jsonify({'data': data}) 


if __name__ == '__main__':
    app.run(host=os.environ.get("BE_HOST"), 
            port=int(os.environ.get("BE_PORT")),
            debug=os.environ.get("DEBUG"))