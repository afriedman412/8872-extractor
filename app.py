from extract8872 import app
import os

if __name__=="__main__":
   if 'PRODUCTION' in os.environ:
      app.run()
   else:
      app.run(debug=True)