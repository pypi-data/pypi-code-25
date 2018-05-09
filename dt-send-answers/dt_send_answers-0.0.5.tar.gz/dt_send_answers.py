import requests
import json

def send_answers(answers, metadata, endpoint):
  for q, a in answers.items():
    if isinstance(a, DAFileList):
      s3_config = get_config('s3')
      local_path = a.path().replace("/tmp/", "")
      if bool(s3_config):
        bucket_name = s3_config['bucket']
        answers[q] = "s3://%s/%s" % (bucket_name, local_path)
      else:
        answers[q] = local_path
  answers = json.dumps(answers, default=lambda x: str(x))
  metadata = json.dumps(metadata, default=lambda x: str(x))
  blank_string = ""
  r = requests.post(user_endpoint, data={'answers': answers, 'metadata': metadata})

def hello_world():
  return "hello world"