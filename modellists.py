'''
Functions such as getting models list, details for rtmpdump, etc.
'''
from config import *
from bs4 import BeautifulSoup
import re
import time, datetime
import signal, os
import subprocess
import psutil
from model import CBModel


def Models_list(client):
    # Moving to followed models page
    try:
        logging.info("Redirecting to " + URL_follwed)
        r2 = client.get(URL_follwed)
    except Exception, e:
        logging.error('Some error during connecting to ' + URL)
        logging.error(e)
        print ('error connecting to chaturbate')
        return ''
    soup = BeautifulSoup(r2.text, 'lxml')
    page_source = 'Page Source for ' + URL_follwed + '\n' + r2.text
    if Debugging == True:
        Store_Debug(page_source, "modellist.log")
    li_list = soup.findAll('li', class_="cams")
    # logging.debug(li_list)
    if Debugging == True:
        Store_Debug(li_list, "li_list.log")
    ## Finding who is not offline
    online_models = []
    for n in li_list:
        if n.text != "offline":
            span_age_list = n.parent.parent.find('span', class_="age")
            genders = {'genderf': 'female', 'genderm': 'male', 'genderc': 'couple', 'genders': 'trans'}
            gender = ''
            if len(span_age_list) and len(span_age_list.attrs['class']) > 1:
                gender = genders.get(span_age_list.attrs['class'][1], 'unknown')

            if n.parent.parent.parent.div.text == "IN PRIVATE":
                logging.warning(n.parent.parent.a.text[1:] + ' model is now in private mode')
            else:
                online_models.append(CBModel(name=n.parent.parent.a.text[1:], gender=gender))
    logging.info('[Models_list] %s models are online: %s' % (len(online_models), str(online_models)))
    return online_models


def Select_models(Models_list):
    # Select models that we need
    Wish_list = Wishlist()
    Model_list_approved = []
    logging.info('[Select_models] Which models are approved?')
    for model in Models_list: # type: CBModel
        if model.name in Wish_list:
            logging.info("[Select_models] " + model.name + ' is approved')
            Model_list_approved.append(model)
    if len(Model_list_approved) == 0:
        logging.warning('[Select_models]  No models for approving')
    return Model_list_approved


def Compare_lists(ml, mlr):
    for model in mlr: # type: CBModel
        if checkIfModelRecorded(model) == False:
            logging.debug("[Compare_lists CheckModelRecorded] Model " + model.name + " is supposed to be recording, but I could not find the process.")
            print ("[Compare_lists CheckModelRecorded] Model " + model.name + " is supposed to be recording, but I could not find the process.")
            try:
                mlr.remove(model)
            except ValueError:
                # Model was removed from the modellist WHILE we are iterating over it (recording process ended properly?)
                # Comparing old models list(Main list) to new(updated) models list
                # This loop is used for removing offline models from main list
                pass
    ml_new = []
    logging.info('[Compare_lists] Checking model list:')
    for model in ml: # type: CBModel
        if model in mlr:
            logging.info("[Compare_lists] " + model.name + " is still being recorded")
            logging.debug("[Compare_lists] Removing " + model.name + " model")
        else:
            logging.debug("[Compare_lists] " + model.name + " is online")
            ml_new.append(model)
    logging.debug("[Compare_lists] List of models after comparing:" + str(ml_new))
    return ml_new


def addmodel(added_model):
    if not added_model in models_online:
        try:
            models_online.append(added_model)
            logging.info('Starting recording of ' + added_model.name)
            timestamp = time.strftime("%d-%m-%Y_%H-%M-%S")
            path = Video_folder + '/' + added_model.name + '/' + added_model.name + '_' + timestamp + '.mp4'
            if not os.path.exists(Video_folder + '/' + added_model.name):
                logging.info('creating directory ' + Video_folder + '/' + added_model.name)
                os.makedirs(Video_folder + '/' + added_model.name)
            # Starting livestreamer
            FNULL = open(os.devnull, 'w')
            #FNULL = open('livestreamer.'+added_model.name+'.log', 'w')

            if H264_remux:
                subprocess.check_call(LIVESTREAMER + ' -Q --hls-segment-threads 2 --hls-live-edge 5 -a "-i - -c:v copy -absf aac_adtstoasc -strict -2 -movflags frag_keyframe \'' + path + '\'" -p ffmpeg http://chaturbate.com/' + added_model.name + ' best', stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
            else:
                subprocess.check_call([LIVESTREAMER, '-Q', '--hls-segment-threads', '2', '--hls-live-edge', '5', '-o', path, 'http://chaturbate.com/' + added_model.name, 'best'], stdout=FNULL, stderr=subprocess.STDOUT)
            models_online.remove(added_model)
        except Exception:
            logging.info('No stream on ' + added_model.name)


def checkIfModelRecorded(model):
    _u = lambda t: t.decode('UTF-8', 'replace') if isinstance(t, str) else t
    for proc in psutil.process_iter():
        try:
            cmd = ' '.join(proc.cmdline())
            if _u(model.name) in _u(cmd):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Process we tried to look at vanished while iterating over the processlist
            # or we have no permissions to look at it's cmdline (maybe a superuser process?)
            pass
    return False
