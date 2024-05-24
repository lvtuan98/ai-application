from app import create_app
from flask import jsonify, request

app = create_app()


@app.route('/', methods = ['GET', 'POST']) 
def home(): 
  if(request.method == 'GET'): 
      data = "This is Backend"
      return jsonify({'data': data}) 


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)