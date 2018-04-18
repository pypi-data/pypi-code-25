#!/usr/bin/env python
# coding: utf-8

from .component import InquirerComponent
from .logging import logger
from .classifiers import (
    # development status
    development_status_description,
    DevelopmentStatus,
    # environment
    environment_text_description,
    environment_list_description,
    Environment,
    # framework
    framework_text_description,
    framework_list_description,
    Framework,
    # intended audience
    intended_audience_description,
    IntendedAudience,
    # license
    license_text_description,
    license_list_description,
    License,
    # natural language
    natural_language_text_description,
    natural_language_list_description,
    NaturalLanguage,
    # operating system
    operating_system_description,
    OperatingSystem,
    # programming language
    programming_language_text_description,
    programming_language_list_description,
    ProgrammingLanguage,
    # topics
    topics_text_description,
    topics_list_description,
    Topics
)
from .utils import (
    search_database,
    prettyprint,
    require_classifier,
    loop_function
)


def program(args):

    # 0. Display banner

    print """________     ___    ___  ________    ___      ________      ________
|\   __  \   |\  \  /  /||\   __  \  |\  \    |\   ____\    |\  _____\\
\ \  \|\  \  \ \  \/  / /\ \  \|\  \ \ \  \   \ \  \___|    \ \  \__/
 \ \   ____\  \ \    / /  \ \   ____\ \ \  \   \ \  \        \ \   __\\
  \ \  \___|   \/  /  /    \ \  \___|  \ \  \   \ \  \____    \ \  \_|
   \ \__\    __/  / /       \ \__\      \ \__\   \ \_______\   \ \__\\
    \|__|   |\___/ /         \|__|       \|__|    \|_______|    \|__|
            \|___|/

Welcome to pypicf.
(1) Please select or check following classifiers.
(2) To select classifiers please use '↑', '↓' arrow keys.
(3) To check classifiers checkbox please use '→', '←' arrow keys.
(4) And you need to search before selecting the classifiers
    because the particular classifiers have many many choices.
(5) You can pass through the classifier by put <Ctrl-C> key at prompt.
    However, there are classifiers that you must be select absolutely.
"""

    inquirer = InquirerComponent()
    selected_classifiers = []

    # 1. Development Status

    @require_classifier("Development Status")
    def _development_status_prompt():
        result = inquirer.prompt_list(
            development_status_description, DevelopmentStatus)
        return result

    selected_classifiers.append(_development_status_prompt())

    # 2. Environment

    @loop_function
    def _environment_prompt():
        query = inquirer.prompt_text(environment_text_description)
        choices = search_database(query, Environment)
        result = inquirer.prompt_list(environment_list_description, choices)
        return result

    try:
        selected_classifiers.append(_environment_prompt())

    except KeyboardInterrupt:
        logger.pass_through("Environment")

    # 3. Framework

    @loop_function
    def _framework_prompt():
        query = inquirer.prompt_text(framework_text_description)
        choices = search_database(query, Framework)
        result = inquirer.prompt_checkbox(framework_list_description, choices)
        return result

    try:
        selected_classifiers += _framework_prompt()

    except KeyboardInterrupt:
        logger.pass_through("Environment")

    # 4. Intended Audience

    @require_classifier("Intended Audience")
    def _intended_audience_prompt():
        result = inquirer.prompt_list(
            intended_audience_description, IntendedAudience)
        return result

    selected_classifiers.append(_intended_audience_prompt())

    # 5. License

    @require_classifier("License")
    def _license_prompt():
        query = inquirer.prompt_text(license_text_description)
        choices = search_database(query, License)
        result = inquirer.prompt_list(license_list_description, choices)
        return result

    selected_classifiers.append(_license_prompt())

    # 6. Natural Langauge

    @loop_function
    def _natural_language_prompt():
        query = inquirer.prompt_text(natural_language_text_description)
        choices = search_database(query, NaturalLanguage)
        result = inquirer.prompt_list(
            natural_language_list_description, choices)
        return result

    try:
        selected_classifiers.append(_natural_language_prompt())

    except KeyboardInterrupt:
        logger.pass_through("Natural Language")

    # 7. Operating System

    @loop_function
    def _operating_system_prompt():
        result = inquirer.prompt_checkbox(
            operating_system_description, OperatingSystem)
        return result

    try:
        selected_classifiers += _operating_system_prompt()

    except KeyboardInterrupt:
        logger.pass_through("Operating System")

    # 8. Programming Language

    @require_classifier("Programming Language")
    def _programming_language_prompt():
        query = inquirer.prompt_text(programming_language_text_description)
        choices = search_database(query, ProgrammingLanguage)
        result = inquirer.prompt_checkbox(
            programming_language_list_description, choices)
        return result

    selected_classifiers += _programming_language_prompt()

    # 9. Topics

    @require_classifier("Topics")
    def _topics_prompt():
        query = inquirer.prompt_text(topics_text_description)
        choices = search_database(query, Topics)
        result = inquirer.prompt_checkbox(
            topics_list_description, choices)
        return result

    selected_classifiers += _topics_prompt()

    print "Thank you for answered!"
    print "Please copy following classifiers and paste it your setup.py.\n"
    print "-" * 50
    prettyprint(selected_classifiers)
    print "-" * 50
    return 0
