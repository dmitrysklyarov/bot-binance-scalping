#nohup python3 manage.py runserver 8001 &

from django.shortcuts import render
from django.http import JsonResponse
import configparser
from django.views.decorators.csrf import csrf_exempt
import configparser
import json
import subprocess
import logging

'''
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
# Create a file handler and set its level
file_handler = logging.FileHandler('views.error.log')
file_handler.setLevel(logging.DEBUG)
# Create a formatter and set it for the file handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
# Add the file handler to the root logger
logging.getLogger().addHandler(file_handler)
'''

def get_config(request):    
    # create a ConfigParser object
    config = configparser.ConfigParser()
    config.read('../main.conf')

    # convert the data to a dictionary
    config_dict = {}
    for section in config.sections():
        section_dict = {}
        for key, value in config.items(section):
            section_dict[key] = value
        config_dict[section] = section_dict

    # print the JSON data
    return JsonResponse(config_dict)

@csrf_exempt
def set_config(request):
    try:
        # check if the request method is POST
        if request.method == 'POST':

            # get the request parameters
            config_data = request.POST.get('config')
            token = request.POST.get('token')

            # check if all parameters are present
            if config_data and token:

                # read secret config
                cp = configparser.ConfigParser()
                cp.read('../secret.conf')
                
                # check if the token is valid
                if token == cp['django']['token']:

                    config_dict = json.loads(config_data)

                    # create a ConfigParser object
                    config = configparser.ConfigParser()

                    # loop through the dictionary and add the data to the ConfigParser object
                    for section, options in config_dict.items():
                        config[section] = options

                    # write the ConfigParser object to the main configuration file
                    with open('../main.conf', 'w') as f:
                        config.write(f)
                    # return a success message as a JsonResponse object
                    return JsonResponse({'message': 'Config updated successfully.'})

                else:
                    # return an error message as a JsonResponse object
                    return JsonResponse({'error': 'Invalid token.'}, status=401)

            else:
                # return an error message as a JsonResponse object
                return JsonResponse({'error': 'Missing parameters.'}, status=400)

        else:
            # return an error message as a JsonResponse object
            return JsonResponse({'error': 'Invalid request method.'}, status=405)
    except Exception as e:
        # return an error message as a JsonResponse object
        return JsonResponse({'error': 'An error occurred. {}'.format(e).encode('utf-8')}, status=400)

@csrf_exempt
def service_action(request):
    token = request.POST.get('token')
    action = request.POST.get('action')
    service = request.POST.get('service')

    cp = configparser.ConfigParser()
    cp.read('../secret.conf')
    if token != cp['django']['token']:
        return JsonResponse({'error': 'Invalid token.'}, status=401)
    
    # check if action is valid
    if action == None or action not in ("start", "stop", "restart"):
        return JsonResponse({'error': 'Invalid action.'}, status=400)
    
    # check if service is valid
    if service == None or len(service) == 0:
        return JsonResponse({'error': 'Missing service parameters.'}, status=400)
    
    # check if service exists
    command = ['systemctl', 'status', service]
    try:
        subprocess.check_output(command)
    except subprocess.CalledProcessError:
        return JsonResponse({'error': 'Service {} does not exist.'.format(service)}, status=400)

    if action == 'start' or action == 'stop':
        # check if try to start when service is already running and stop when service is not running    
        command = ['systemctl', 'is-active', service]
        try:
            subprocess.check_output(command)
            if action == 'start':
                return JsonResponse({'error': 'Service {} already started.'.format(service)}, status=400)
        except:
            if action == 'stop':
                return JsonResponse({'error': 'Service {} already stopped.'.format(service)}, status=400)
    
    # execute action
    command = ['sudo', 'systemctl', action, service]
    #logging.info("starting try for {0} {1}".format(action, service))
    try:
        subprocess.check_output(command)
        #logging.info("command executed successfully")
        return JsonResponse({'message': 'Service {0} successfully {1}ed.'.format(service, action)})
    except Exception as err:
        #logging.error(str(err))
        return JsonResponse({'error': 'Unknown error occurred.'}, status=400)