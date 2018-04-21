from django.apps import AppConfig

class ActivityStreamAppConfig(AppConfig):
  def ready(self):
    from actstream import registry
    for model in self.stream_models:
      registry.register(self.get_model(model))
