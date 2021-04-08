import os
import utils
import logging

#--------------- FUNCTIONS ---------------#
def certificate_chains():
    while True:     
        choice = utils.menu()
        utils.switch(choice)
#-----------------------------------------#

#--------- LAUNCHING THE PROGRAMM --------#
try:
    certificate_chains()
except Exception as e:
    logging.error(e)
#-----------------------------------------#

