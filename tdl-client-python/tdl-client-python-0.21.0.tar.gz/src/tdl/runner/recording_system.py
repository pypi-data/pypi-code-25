import unirest

RECORDING_SYSTEM_ENDPOINT = "http://localhost:41375"

class RecordingEvent:
    def __init__(self):
        pass

    ROUND_START = 'new'
    ROUND_SOLUTION_DEPLOY = 'deploy'
    ROUND_COMPLETED = 'done'


class RecordingSystem:

    def __init__(self, recording_required):
        self._recording_required = recording_required

    def is_recording_system_ok(self):
        return RecordingSystem.is_running() if self._recording_required else True

    @staticmethod
    def is_running():
        try:
            response = unirest.get("{}/status".format(RECORDING_SYSTEM_ENDPOINT))

            if response.code == 200 and response.body.startswith("OK"):
                return True
        except Exception as e:
            print("Could not reach recording system: {}".format(str(e)))

        return False

    def notify_event(self, round_id, event_name):
        print('Notify round "{}", event "{}"'.format(round_id, event_name))

        if not self.is_recording_system_ok():
            return

        try:
            response = unirest.post("{}/notify".format(RECORDING_SYSTEM_ENDPOINT),
                                    params="{}/{}".format(round_id, event_name))

            if response.code != 200:
                print("Recording system returned code: {}".format(response.code))
                return

            if not response.body.startswith("ACK"):
                print("Recording system returned body: {}".format(response.body))

        except Exception as e:
            print("Could not reach recording system: {}".format(str(e)))

    def on_new_round(self, round_id):
        self.notify_event(round_id, RecordingEvent.ROUND_START)
