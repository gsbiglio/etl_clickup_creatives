from config import lists_id, api_token
import requests as r
import pandas as pd
from datetime import datetime


def extract(list_id):
    '''this function extract data from ClickUp API'''

    url = "https://api.clickup.com/api/v2/list/" + list_id + "/task"
    query_parameters = {
        "archived": "false",
        "include_closed": "true",
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": api_token
    }

    response = r.get(url, headers=headers, params=query_parameters)
    data = response.json()

    return data


def transform(data):
    '''this function transform data extracted form ClickUp API'''

    datamodel = {
        'id': [],
        'name': [],
        'status': [],
        'date_created': [],
        'date_updated': [],
        'date_closed': [],
        'due_date': [],
        'creator': [],
        'assignes': [],
        'ASSETS': [],
        'CHANNEL': [],
        'CLIENT': [],
        'TEAMS': [],
        'TYPE': [],
        'url': [],
    }

    for task in data['tasks']:

        datamodel['id'].append(task['id'])

        datamodel['name'].append(task['name'])

        datamodel['status'].append(task['status']['status'])

        datamodel['date_created'].append(
            datetime.utcfromtimestamp(
                int(task['date_created'])/1000).strftime('%Y-%m-%d %H:%M:%S')
        )

        datamodel['date_updated'].append(
            datetime.utcfromtimestamp(
                int(task['date_updated'])/1000).strftime('%Y-%m-%d %H:%M:%S')
        )

        # add try because if the task is not closed, the value is Null
        try:
            datamodel['date_closed'].append(
                datetime.utcfromtimestamp(
                    int(task['date_closed'])/1000).strftime('%Y-%m-%d %H:%M:%S')
            )
        except:
            datamodel['date_closed'].append(None)

        # add try because if the task doesn't have due_date, the value is Null
        try:
            datamodel['due_date'].append(
                datetime.utcfromtimestamp(
                    int(task['due_date'])/1000).strftime('%Y-%m-%d %H:%M:%S')
            )
        except:
            datamodel['due_date'].append(None)

        datamodel['creator'].append(task['creator']['email'])

        # add try because if the task doesn't have assigne, the value is Null
        try:
            datamodel['assignes'].append(task['assignes']['email'])
        except:
            datamodel['assignes'].append(None)
        
        #all custom fields have a diferent tree
        for custom_field in task['custom_fields']:

            if custom_field['type'] == 'number':

                datamodel[custom_field['name']].append(custom_field['value'])

            elif custom_field['type'] == 'drop_down':

                # extract the value for comparation
                value = custom_field['value']

                for option in custom_field['type_config']['options']:

                    if option['orderindex'] == value:

                        datamodel[custom_field['name']].append(option['name'])

            elif custom_field['type'] == 'labels':

                temp_list = []

                # extract the values for comparation
                values = custom_field['value']

                for option in custom_field['type_config']['options']:

                    if option['id'] in values:

                        temp_list.append(option['label'])

                datamodel[custom_field['name']].append(temp_list)

        datamodel['url'].append(task['url'])

    df = pd.DataFrame(data=datamodel)
    
    return df.head(5)


if __name__ == '__main__':

    for list in lists_id:
        json_data = extract(list)
        df = print(transform(json_data))
