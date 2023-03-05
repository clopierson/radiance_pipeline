import sys
import time
import logging
from pathlib import Path


# This function adds an error message to a log if it exists, otherwise creates the file first.
def recordError( inputErrorPath, error ):
    errorPath = Path( inputErrorPath )
    print(f"errorPath: {errorPath}")

    if not ( errorPath.is_file ):
        errorPath.mkdir( mode=0o777, parents=True, exist_ok=True )

    # Set config for error logging
    logging.basicConfig(filename=inputErrorPath, level=logging.ERROR, 
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    
    #   # Set config for general logging
    # logging.basicConfig(filename=outputLogPath, level=logging.INFO, 
    #                     format='%(asctime)s %(levelname)s %(name)s %(message)s')

    errorLog = logging.getLogger( __name__ )
    errorLog.error( error )

# This function prints an error to stderr
# Source: https://stackoverflow.com/questions/5574702/how-do-i-print-to-stderr-in-python#:~:text=The%20optional%20function-,eprint,-saves%20some%20repetition
def printError(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)