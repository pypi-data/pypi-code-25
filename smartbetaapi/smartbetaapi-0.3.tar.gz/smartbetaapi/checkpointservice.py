from .apiservice import APIService
import datetime
import pandas as pd

class CheckpointService:
    def __init__(self, api_service: APIService, execution_id: str):
        self._execution_id = execution_id
        self._api_service = api_service

    def save(self, checkpoint_name: str, data_to_save: pd.DataFrame):
        data_json = data_to_save.to_json()
        self._api_service.save_checkpoint(execution_id=self._execution_id, checkpoint_name=checkpoint_name,
                                          data_json=data_json)

    def get_checkpoint(self, checkpoint_name: str ) -> pd.DataFrame:
        data_json = self._api_service.get_checkpoint(execution_id=self._execution_id, checkpoint_name=checkpoint_name)

        df = pd.DataFrame(data_json)
        return df