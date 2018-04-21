import random

_MW = ['en', 'en-gb']#, 'es', 'fr', 'de']

TWILIO_VOICES = {
  'alice': [
    'da-DK',
    'de-DE',
    'en-AU',
    'en-CA',
    'en-GB',
    'en-IN',
    'en-US',
    'ca-ES',
    'es-ES',
    'es-MX',
    'fi-FI',
    'fr-CA',
    'fr-FR',
    'it-IT',
    'ja-JP',
    'ko-KR',
    'nb-NO',
    'nl-NL',
    'pl-PL',
    'pt-BR',
    'pt-PT',
    'ru-RU',
    'sv-SE',
    'zh-CN',
    'zh-HK',
    'zh-TW',
  ],
  'man': _MW,
  'woman': _MW
}

_seed = ['man','man','man','woman','woman','woman']#,'alice']

def random_voice():
  v = random.choice(_seed)
  return v,random.choice(TWILIO_VOICES[v])
