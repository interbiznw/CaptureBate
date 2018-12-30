import socket
import connection
import modellists
from datetime import datetime
from time import sleep
from config import *
from thread import *
from model import CBModel

if __name__ == '__main__':
    ## Main section
    # Set logging
    Logging()
    # Create directories
    Preconditions(Video_folder)
    # Connecting
    client_factory = connection.ClientFactory()
    client = connection.Connection(client_factory)
    # Get the models list and create main list
    Models_list_store = modellists.Models_list(client)
    # Select models for recording according to wishlist
    Selected_models = modellists.Select_models(Models_list_store)

    if not Selected_models:
        Selected_models = Models_list_store
        print (datetime.now().strftime("%Y-%m-%d %H:%M:%S ") + 'Empty Whitelist, using complete favorite list')

    # Loop to send which model to capture
    for model in Selected_models: # type: CBModel
        # For thread to work it needs to be a tuple
        model = (model,)
        # Starting a new thread
        start_new_thread(modellists.addmodel, model)
        sleep(1)
    print (datetime.now().strftime("%Y-%m-%d %H:%M:%S ") + 'Models currently recorded: ' + str(models_online))
    logging.info('Waiting for %d seconds' % Time_delay)
    sleep(Time_delay)
    while True:
        ## Reassign updated main models list
        # Connecting to server
        client = connection.Connection(client_factory)
        logging.info(str(len(Models_list_store)) + ' Models in the list before checking: ' + str(Models_list_store))
        # Requesting to server list of models currently captured
        Models_list_store = modellists.Compare_lists(modellists.Models_list(client), models_online)
        Selected_models = modellists.Select_models(Models_list_store)
        # Loop to start new models
        for model in Selected_models: # type: CBModel
            # For thread to work it needs to be a tuple
            model = (model,)
            # Starting a new thread
            start_new_thread(modellists.addmodel, model)
            sleep(1)
        logging.info('[Loop]Model list after check looks like: %d models:\n %s \n and models currently being recorded are:\n %s' % (len(Models_list_store), str(Models_list_store), str(models_online)))
        logging.info('[Sleep] Waiting for next check (%d seconds)' % Time_delay)
        print (datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' Models currently recorded: ' + str(models_online))
        sleep(Time_delay)
