#nohup python3 manage.py runserver 8001 &

from django.shortcuts import render
from django.http import JsonResponse
import configparser
from django.views.decorators.csrf import csrf_exempt
import configparser
import json
import logging

# Create your views here.

def get_config(request):

    logging.basicConfig(filename='views.log', level=logging.INFO)
    logging.info('get_config() called')
    
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
        logging.info(request.method)
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