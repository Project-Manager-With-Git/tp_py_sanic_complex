import sys
from test_sanic.serv import Serv

serv = Serv()
serv(sys.argv[1:])
