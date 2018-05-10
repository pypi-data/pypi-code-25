import requests
import json
from docassemble.base.functions import get_config, all_variables
from docassemble.base.core import DAFileList

def send_answers():
  endpoint = get_config("answer endpoint")
  answers = all_variables(simplify=False)

  for q, a in answers.items():
    if isinstance(a, DAFileList) or isinstance(a, DAFile):
      s3_config = get_config('s3')
      local_path = a.path().replace("/tmp/", "")
      if bool(s3_config):
        bucket_name = s3_config['bucket']
        answers[q] = "s3://%s/%s" % (bucket_name, local_path)
      else:
        answers[q] = local_path

  answers = json.dumps(answers, default=lambda x: str(x))
  metadata = json.dumps(all_variables(special='metadata'), default=lambda x: str(x))

  return requests.post(endpoint, data={'answers': answers, 'metadata': metadata})