import os
import logging
import sys
import OpenSSL.crypto
from Crypto.Util import asn1
from OpenSSL import crypto
from os import listdir
from os.path import isfile, join
import re
import csv
import os 
import pandas 
from pandas import DataFrame
import datetime
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

#------------------ MENU ------------------#
def switch(_value: int):
    cases = {
        '1': lambda: logging.info('Matching State ==> {}\n'.format(match_between_key_n_certificate())),
        '2': lambda: list_Cert(),
        '3': lambda: insert_Cert(),
        '4': lambda: exit(),
    }
    cases.get(_value, lambda: print("This value is incorrect or doesn't exist...please try again !"))()
def menu():
    logging.info('Press Enter button to continue...')
    input()
    os.system('cls')
    print('Selection Menu : please choose an option => ',
        '1. VERIFY matching(key/certificate)',
        '2. LIST all key(in folder)',
        '3. ADD Certification',
        '4. EXIT\n',
        sep='\n',
    )
    choice = input('Select => ')
    return choice 
#------------------------------------------#


#----------------- GLOBAL -----------------#
PATH = os.getcwd()
#------------------------------------------#

#--------------- FUNCTIONS ----------------#

# - Option 1 - #

# Retrieve a certificate in the directory
def get_certificate():

    Path=(PATH+"/certificates")
    FILES = [f for f in listdir(Path) if isfile(join(Path, f))]
    CERT_LIST = []
    while(True):
        response=input('Saissisez un choix d\'extension de fichier(pem/crt) :> ')
        if response == 'pem' or response == 'crt':
            i = 1
            print("Here is the list of certificates :")
            for f in FILES: 
                    # search given pattern in the line  
                    match = re.search("\."+response+"$", f) 
                    if match: 
                        CERT_LIST.append(f)
                        print("{1}/ {0}".format(os.path.join(Path, f),(i)))  
                        i+=1
            response=int(input("\nPut the id of the key :> "))
            cert  = os.path.join(Path, CERT_LIST[response-1])                 
            logging.warning('\nU choose : {}. Is that correct ? (y/n)'.format(cert))
            if input() == 'y':
                return CERT_LIST[response-1]
            logging.warning('\nYou didn\'t choose a certificate file or there is no such file\n')
            if input('quit ? (yes/no)') == 'yes':
                return False
        else:
            logging.warning('You must choose between pem and cer')
# Retrieve a key in the directory
def get_key():

    Path= (PATH+"/keys")
    FILES = [f for f in listdir(Path) if isfile(join(Path, f))]
    KEY_LIST = []
    while(True):
        i = 1
        print("Here is the list of keys : ")
        for f in FILES: 
            # search given pattern in the line  
            match = re.search("\.key$", f) 
            if match: 
                KEY_LIST.append(f)
                print("{1}/ {0}".format(os.path.join(Path, f),(i)))  
                i+=1
        response=int(input("\nPut the id of the key :> "))
        key  = os.path.join(Path, KEY_LIST[response-1])                 
        logging.warning('\nU choose : {}. Is that correct ? (y/n)'.format(key))
        if input() == 'y':
            return KEY_LIST[response-1]
        logging.warning('\nYou didn\'t choose a certificate file or there is no such file\n')
        if input('quit ? (yes/no)') == 'yes':
            return False
# This function checks the concordance between a key and a certifcate
def match_between_key_n_certificate():
    """
    :type cert: str
    :type private_key: str
    :rtype: bool
    """
    #retrieve certificate and key
    cert=os.path.join(PATH+"/certificates/",get_certificate())
    if cert:   
        private_key=os.path.join(PATH+"/keys/",get_key())
    if private_key:
        try:
            private_key_file = open(private_key, 'r')
            private_key_data = private_key_file.read()
            private_key_obj = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, private_key_data)
        except OpenSSL.crypto.Error:
            raise Exception('private key is not correct: %s' % private_key_file)

        try:
            cert_file = open(cert, 'r')
            cert_data = cert_file.read()
            certificate = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
        except OpenSSL.crypto.Error:
            raise Exception('certificate is not correct: %s' % cert_file)

        context = OpenSSL.SSL.Context(OpenSSL.SSL.TLSv1_METHOD)
        context.use_privatekey(private_key_obj)
        context.use_certificate(certificate)
        try:
            context.check_privatekey()
            logging.info('For PK => {0} and Cert => {1}'.format(private_key,cert))
            return True
        except OpenSSL.SSL.Error:
            return False 
    else:
        return    
# - Option 2 - #
def list_Cert():
    csv = list_csv()
    for i,file in enumerate(csv):
        print("{0}/ File : {1}\n".format((i+1),file))
        keyCert = pandas.read_csv(PATH+"/csv/"+file, usecols=['KeyFile','CertFile','Date'], sep=';',)
        print(keyCert)  
        print("\n")

        
# - Option 3 - #
def insert_Cert_Create(csv_file: str,new_file: bool,key_file: str,cert_file: str):

    myDateTime = datetime.datetime.today()     
    DATE = ("{0}-{1}-{2}_{3}-{4}-{5}".format(myDateTime.year, myDateTime.month, myDateTime.day,myDateTime.hour, myDateTime.minute,myDateTime.second))

    C = {'KeyFile': [key_file],
    'CertFile': [cert_file],
    'Date': [DATE]
    }
    df = DataFrame(C, columns= ['KeyFile', 'CertFile', 'Date'])
    File_Dest=PATH+"/csv/"+csv_file
    if new_file:       
        export_csv = df.to_csv(File_Dest,mode='a', header=True, encoding='utf-8', sep=';')
    else:
        export_csv = df.to_csv(File_Dest,mode='a', header=False, encoding='utf-8', sep=';')
def insert_Cert():
        cert=get_certificate()
        private_key=get_key()
        if cert and private_key:
            csv=list_csv()        
            print("Here is the list of csv :")
            create=True
            i = 1
            for f in csv: 
                print("{1}/ {0}".format(os.path.join(PATH+"/csv/", f),(i)))  
                i+=1
            print('0/ Create new csv ?\n')
            response=int(input("Put the id of the csv :> "))
            if response != 0: 
                create=False 
                insert_Cert_Create(csv[response-1],create,private_key,cert)
            else:
                csvName = input("Put CSV Name : ")  
                csv  = (csvName + ".csv")
                insert_Cert_Create(csv,create,private_key,cert)         
def list_csv():
    PATH=(os.getcwd()+"/csv")
    FILES = [f for f in listdir(PATH) if isfile(join(PATH, f))]
    CERT_LIST = []
    for f in FILES: 
        CERT_LIST.append(f)
    return CERT_LIST
#------------------------------------------#
