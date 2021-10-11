import uvicorn
from api import *
 

uvicorn.run(app, host="0.0.0.0", port=8080)
# "Open http://0.0.0.0:8080/src/dashbot.html to start DashBot"
