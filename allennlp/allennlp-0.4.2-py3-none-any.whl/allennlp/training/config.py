"""
An object representing the training configuration
"""
import logging
import os
from typing import NamedTuple, List

from allennlp.common import Params
from allennlp.data import Dataset, DatasetReader, Vocabulary, DataIterator
from allennlp.models import Model
from allennlp.training import Trainer

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

class Config(NamedTuple):
    # required
    dataset_reader: DatasetReader
    train_data_path: str
    vocabulary: Vocabulary
    model: Model
    iterator: DataIterator
    trainer: Trainer

    # optional
    validation_data_path: str = None
    test_data_path: str = None
    evaluate_on_test: bool = False

    @classmethod
    def from_params(cls, params: Params, serialization_dir: str) -> 'Config':
        # Now we begin assembling the required parts for the Trainer.
        dataset_reader = DatasetReader.from_params(params.pop('dataset_reader'))

        train_data_path = params.pop('train_data_path')
        logger.info("Reading training data from %s", train_data_path)
        train_data = dataset_reader.read(train_data_path)

        all_datasets: List[Dataset] = [train_data]
        datasets_in_vocab = ["train"]

        validation_data_path = params.pop('validation_data_path', None)
        if validation_data_path is not None:
            logger.info("Reading validation data from %s", validation_data_path)
            validation_data = dataset_reader.read(validation_data_path)
            all_datasets.append(validation_data)
            datasets_in_vocab.append("validation")
        else:
            validation_data = None

        test_data_path = params.pop("test_data_path", None)
        if test_data_path is not None:
            logger.info("Reading test data from %s", test_data_path)
            test_data = dataset_reader.read(test_data_path)
            all_datasets.append(test_data)
            datasets_in_vocab.append("test")
        else:
            test_data = None

        logger.info("Creating a vocabulary using %s data.", ", ".join(datasets_in_vocab))
        vocab = Vocabulary.from_params(params.pop("vocabulary", {}),
                                    Dataset([instance for dataset in all_datasets
                                                for instance in dataset.instances]))
        vocab.save_to_files(os.path.join(serialization_dir, "vocabulary"))

        model = Model.from_params(vocab, params.pop('model'))
        iterator = DataIterator.from_params(params.pop("iterator"))

        train_data.index_instances(vocab)
        if validation_data:
            validation_data.index_instances(vocab)

        trainer_params = params.pop("trainer")
        trainer = Trainer.from_params(model,
                                      serialization_dir,
                                      iterator,
                                      train_data,
                                      validation_data,
                                      trainer_params)

        evaluate_on_test = params.pop("evaluate_on_test", False)
        params.assert_empty('base train command')

        return cls(dataset_reader=dataset_reader,
                   train_data_path=train_data_path,
                   validation_data_path=validation_data_path,
                   test_data_path=test_data_path,
                   evaluate_on_test=evaluate_on_test,
                   vocabulary=vocab,
                   model=model,
                   iterator=iterator,
                   trainer=trainer)
