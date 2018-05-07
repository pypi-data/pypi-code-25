import logging
from eurydike.eventdetectors.onband import OnBand
from eurydike.eventdetectors.onthreshold import OnThreshold


class EventDetectorFactory:
    @staticmethod
    def create_element(config_element, parent_logger, mqtt_client):
        logger = parent_logger.getChild(__name__)
        element = None
        if config_element["active"]:
            if config_element["type"].lower() == "onband":
                element = OnBand(config_element, parent_logger, mqtt_client)
            elif config_element["type"].lower() == "onthreshold":
                element = OnThreshold(config_element, parent_logger, mqtt_client)
            else:
                logger.error("EventDetectorFactory.create_element - unknown type '{}'".
                              format(config_element["type"].lower()))
                raise ValueError("Factory.create_element - unknown type '{}'".
                                 format(config_element["type"].lower()))
        else:
            logger.info("EventDetectorFactory.create_element - skipping inactive element '{}.{}'.".
                        format(config_element["type"].lower(), config_element["name"]))

        return element

    @staticmethod
    def create_elements(config_elements, parent_logger, mqtt_client):
        logger = parent_logger.getChild(__name__)
        element_list = []

        logger.info("EventDetectorFactory.create_elements - start")

        for config_element in config_elements:
            element = EventDetectorFactory.create_element(config_element, parent_logger, mqtt_client)
            if element is not None:
                element_list.append(element)

        logger.info("EventDetectorFactory.create_elements - finished")

        return element_list


