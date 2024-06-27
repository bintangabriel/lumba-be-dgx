from django.shortcuts import render
from django.http import JsonResponse
from be_dgx.app_redis import Redis
import os
import requests
from be_dgx.celery import app

@app.task(acks_late=True)
def training_simulation_2(username, workspace, type, file_key, filename, model_type, id, model_name, epoch, learning_rate):
    try:
        ip_modeling = os.environ.get('MODELING_IP')
        port_modeling = os.environ.get('MODELING_PORT')

        training_service_url = f'http://{ip_modeling}:{port_modeling}/train/' # Change domain url on the current staging

        model_metadata = {
            'model_type': model_type,
            'model_name': model_name,
            'type': type,
            'username': username,
            'workspace': workspace,
            'filename': filename,
            'gpu': [],
            'id': id,
            'epoch': epoch,
            'learning_rate': learning_rate,
            'file_key': file_key
        }

        print(training_service_url)
        res = requests.post(training_service_url, data=model_metadata)
        print(res)
        # return Response(data=res.json()) => for non-celery task
        return res
        # return res
    except Exception as e:
        # return Response({'message': "input error"}, status=status.HTTP_400_BAD_REQUEST) => for non-celery task
        return { 'message': str(e) , 'status': 400 }


# Create your views here.
def async_train_endpoint(req):
  try:
    model_metadata = req.POST.dict()
    print('metadata: ', model_metadata)
  except:
    return JsonResponse({'message': "input error"})
  
  training_simulation_2.delay(
    model_metadata['username'],
    model_metadata['workspace'],
    model_metadata['type'],
    model_metadata['file_key'],
    model_metadata['filename'],
    model_metadata['model_type'],
    model_metadata['id'],
    model_metadata['model_name'],
    model_metadata['epoch'],
    model_metadata['learning_rate']
  )

  training_record = {
    'id' : model_metadata['id'],
    'status' : 'accepted',
  }  
  return JsonResponse(training_record)