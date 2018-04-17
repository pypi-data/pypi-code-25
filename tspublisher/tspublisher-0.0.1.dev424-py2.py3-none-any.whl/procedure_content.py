from __future__ import print_function

import os
import subprocess
import sys
import shutil


from publisher import settings
from publisher.classes import Commit


class WorkingDirectory(object):
    """ Context manager for changing directory"""
    def __init__(self, new_dir):
        self.new_dir = new_dir
        self.old_dir = None

    def __enter__(self):
        self.old_dir = os.getcwd()
        os.chdir(self.new_dir)

    def __exit__(self, *_):
        os.chdir(self.old_dir)


def git_installed():
    try:
        subprocess.check_output(['git', '--version'])
    except OSError:
        print("Git not installed")
        return False
    return True


def call_command_and_print_exception(command, message):
    try:
        return subprocess.check_output(command)
    except Exception as e:
        print(message)
        raise e


def check_and_create_directory(path):
    try:
        if not os.path.exists(path):
            os.mkdir(path)
    except Exception:
        print("Could not find or create the directory")
        raise


def check_and_create_file(path):
    try:
        if not os.path.exists(path):
            subprocess.check_output(['touch', path])
    except Exception:
        print("Could not find or create the file")
        raise


def setup_username():
    print("Please enter your name here:")
    sys.stdout.flush()
    username = raw_input('')
    subprocess.check_output(['git', 'config', '--global', 'user.name', username])

    print("Please enter your touch surgery email here:")
    sys.stdout.flush()
    email = raw_input('')
    subprocess.check_output(['git', 'config', '--global', 'user.email', email])


def setup_users_machine():
    """
    User Setup for publish
        1. Check if git is installed
        2. Setup SSH
        3. Cloning the repo and git pull
    """
    if not git_installed():
        win_msg = 'Please install Github for windows from https://desktop.github.com/ before coming back and ' \
                  'continuing and running setup again.'
        mac_msg = 'Please install Git for Mac from https://git-scm.com/download/mac before running setup again.'

        print("%s" % win_msg if 'win' in sys.platform.lower() else mac_msg)
        sys.exit(1)

    print("Configuring ssh config file")
    check_and_create_directory(settings.SSH_DIRECTORY_PATH)
    check_and_create_file(settings.SSH_CONFIG_PATH)
    if not has_private_key():
        raise RuntimeError("Unable to proceed without a key. Please contact Hansel before trying again")
    configure_ssh_config()

    print("Installing and configuring git lfs")
    install_git_lfs()
    configure_git_lfs()

    check_and_create_directory(settings.GIT_DIRECTORY)

    print("Setting up the content repo")
    clone_content_repo()
    pull_content_repo()

    print("Setting up the channel repo")
    clone_channel_repo()
    pull_channel_repo()

    setup_username()


def build_procedure_list():

    """ Lists all current branches of the repository
    """

    def filter_junk(b):
        return b not in ['master', 'HEAD', '->'] and b.strip() != ''

    if os.path.exists(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
            subprocess.check_output(['git', 'fetch'])
            procedure_list = subprocess.check_output(['git', 'branch', '-r']).split()
            new_procedure_list = []
            for name in procedure_list:
                if 'origin' in name:
                    new_procedure_list.append(name.split('/')[-1])
                else:
                    new_procedure_list.append(name)

            new_procedure_list = filter(filter_junk, new_procedure_list)
            return new_procedure_list

    else:
        raise Exception("You do not have the content-production repository, please run the setup command.")


def display_procedures():
    print('\n'.join(build_procedure_list()))


def build_phase_list():
    """ Returns a list of phases for the current module"""
    current_procedure = ""

    all_subdirectories = [folder for folder in os.walk(settings.PROCEDURE_CHECKOUT_DIRECTORY)]
    immediate_subdirectories_and_files = all_subdirectories[0]
    immediate_subdirectories = immediate_subdirectories_and_files[1]
    for directory in immediate_subdirectories:
        if not directory.startswith("."):
            current_procedure = directory
            continue

    phase_folder = os.path.join(settings.PROCEDURE_CHECKOUT_DIRECTORY, current_procedure)
    # Find folders in the procedure directory, return as a list for future use
    with WorkingDirectory(phase_folder):
        output = subprocess.Popen(['ls'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        phase_list = (output.communicate()[0].split("\n"))
        updated_phase_list = []
        for phase in phase_list:
            if os.path.isdir(os.path.join(phase_folder, phase)) and phase != "assets":
                updated_phase_list.append(phase)
        return updated_phase_list


def display_phases():
    print("Current modules for procedure:" + "\n")
    print("\n".join(build_phase_list()))


def change_procedure(procedure):
    """Switches git branch to the procedure selected
    """

    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        command = ['git', '-c', 'filter.lfs.clean=', '-c', 'filter.lfs.smudge=', '-c', 'filter.lfs.process=', '-c',
                   'filter.lfs.required=false', 'checkout', procedure]
        message = "Could not find the specified procedure. Make sure you have run setup and entered the correct " \
                  "procedure name"
        call_command_and_print_exception(command, message)

        print("Retrieving procedure assets")
        subprocess.call(['git', '-c', 'filter.lfs.clean=', '-c', 'filter.lfs.smudge=', '-c', 'filter.lfs.process=',
                         '-c', 'filter.lfs.required=false', 'pull'])
        subprocess.call(['git', 'lfs', 'pull'])
        subprocess.call(['git', 'clean', '-df'])


def has_private_key():
    """Check whether the user has the correct private key
    """
    return os.path.exists(os.path.expanduser("~/.ssh/touchsurgery-studio.pem"))


def configure_ssh_config():
    """Creates and sets up an ssh config file, or appends the necessary entry to an existing one
    """
    shutil.copyfile(os.path.expanduser(settings.SSH_CONFIG_PATH), os.path.expanduser(settings.SSH_CONFIG_PATH + '.bak'))

    ssh_config_stanza = (
        'Host studio-git.touchsurgery.com\n'
        ' User ubuntu\n'
        ' IdentitiesOnly true\n'
        ' IdentityFile ~/.ssh/touchsurgery-studio.pem\n'
    )

    try:

        with open(os.path.expanduser(settings.SSH_CONFIG_PATH), "r") as config_file:
            current_config_text = config_file.read()
            ssh_config_missing = ssh_config_stanza not in current_config_text

        if ssh_config_missing:
            with open(os.path.expanduser(settings.SSH_CONFIG_PATH), "a+") as config_file:
                config_file.write('\n' + '\n' + ssh_config_stanza)

    except Exception:
        print("Unable to configure the ssh config")
        raise


def install_git_lfs():
    """Install git lfs
    """
    if 'darwin' in sys.platform.lower():
        call_command_and_print_exception(['brew', 'install', 'git-lfs'], "brew lfs install failure")

    call_command_and_print_exception(['git', 'lfs', 'install'], "lfs install failure")


def configure_git_lfs():
    """Set relevant  lfs settings
    """
    call_command_and_print_exception(['git', 'config', '--global', 'lfs.url',
                                      'https://live.touchsurgery.com/api/v3/lfs'], "lfs config failure")
    call_command_and_print_exception(['git', 'config', '--global', 'lfs.activitytimeout', '60'], "lfs config failure")


def clone_content_repo():
    """Clone the content repo
    """
    if not os.path.exists(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        try:
            with WorkingDirectory(settings.GIT_DIRECTORY):
                call_command_and_print_exception(['git', 'lfs', 'clone',
                                                  settings.PROCEDURE_REPOSITORY,
                                                  settings.PROCEDURE_CHECKOUT_DIRECTORY], "Clone repo failure")
        except Exception as e:
            print("Unable to clone the content repo")
            raise e
    else:
        print("Procedure repo already exists")


def pull_content_repo():
    """Run a git pull in the content repo
    """
    try:
        with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
            call_command_and_print_exception(['git', 'lfs', 'pull', 'origin', 'master'], "Git pull failure")
    except Exception as e:
        print("Unable to run a git pull in the content repo")
        raise e


def clone_channel_repo():
    """Clone the channel repo
    """
    if not os.path.exists(settings.CHANNELS_CHECKOUT_DIRECTORY):
        try:
            with WorkingDirectory(settings.GIT_DIRECTORY):
                call_command_and_print_exception(['git', 'lfs', 'clone',
                                                  settings.CHANNELS_REPOSITORY,
                                                  settings.CHANNELS_CHECKOUT_DIRECTORY], "Clone repo failure")
        except Exception as e:
            print("Unable to clone the content repo")
            raise e
    else:
        print("Channel repo already exists")


def pull_channel_repo():
    """Run a git pull in the channel repo
    """
    try:
        with WorkingDirectory(settings.CHANNELS_CHECKOUT_DIRECTORY):
            call_command_and_print_exception(['git', 'lfs', 'pull', 'origin', 'master'], "Git pull failure")
    except Exception as e:
        print("Unable to run a git pull in the channel repo")
        raise e


def save_working_changes(message, initial=False, procedure_code=None):
    """Commits and pushes with the current changes to the repo
    """
    try:
        # Git stage, commit with message and push
        with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
            subprocess.check_output(['git', 'stage', '.'])
            commit_output = subprocess.Popen(['git', 'commit', '-a', '-m', '"'+message+'"'], stdout=subprocess.PIPE)
            if initial:
                subprocess.check_output(['git', 'push', '--set-upstream', 'origin', procedure_code])
            else:
                pull_and_merge()
                text_commit_output = commit_output.communicate()[0].decode('utf-8')

                if 'nothing to commit' in text_commit_output:
                    print('No changes detected.')
                    sys.exit(0)
                subprocess.check_output(['git', 'push'])

    except subprocess.CalledProcessError:
        print("Could not commit/push the changes.")
        raise


def publish(selected_commit_and_dist_group):
    """ Publishes the procedure with a git note containing the distribution group to the chosen commit
    """

    all_commits = get_commits()
    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        try:
            clear_similar_historical_notes(selected_commit_and_dist_group, all_commits)
            edit_note(selected_commit_and_dist_group)
        except Exception:
            print("Could not publish the procedure to the specified distribution group.")
            raise


def publish_with_display(dist_group, number_of_commits_shown):

    dist_group = dist_group or "TS-Testing"  # Default distribution group
    number_of_commits_shown = number_of_commits_shown or 10  # Default number of commits shown

    print("Current module:")
    print(subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']))
    print("Which commit would you like to publish?" + "\n")

    all_commits = get_commits()
    if not all_commits:
        raise Exception("Either there were no previous commits or you set the optional '--number' argument to be "
                        "zero. Please either save your work first or input a positive integer to the --number "
                        "argument.")
    printable_commits = get_commits()[:int(number_of_commits_shown)]

    for number, commit in enumerate(printable_commits):
        print(number + 1, str(commit))
    print("\n" + "Enter the number of the version you want to publish here, type 0 to cancel:")
    sys.stdout.flush()

    user_input = int(raw_input(''))
    if user_input == 0:
        print("Publishing Cancelled.")
        sys.exit(0)
    elif user_input not in range(1, len(printable_commits) + 1):
        raise Exception("Please publish again and enter the number of an existing commit.")

    selected_commit = all_commits[user_input - 1].copy_with_new_note(dist_group)
    publish(selected_commit)
    print("Commit", user_input, "has been published to the", dist_group, "group.")


def get_author(commit_hash):
    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        output = subprocess.Popen(['git', 'show', '--format="%aN <%aE>"', commit_hash], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        author = output.communicate()[0].split('"')[1]
        return author


def get_commits():
    """Get the previous notes and commits.
    """
    commit_list = []
    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):

        subprocess.check_output(['git', 'fetch', 'origin', 'refs/notes/*:refs/notes/*'])
        log_list = subprocess.check_output(['git', 'log', '--oneline']).split("\n")
        for counter, log in enumerate(log_list):

            if log != "":
                commit_id = log.split()[0]
                comment = log.split(" ", 1)[1]
                note = get_commit_note(commit_id)
                author = get_author(commit_id)

                commit_list.append(Commit(commit_id, comment, author, note))

    return commit_list


def get_commit_note(commit_object):
    # Get the notes for the previous commits
    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):

        try:
            output = subprocess.Popen(['git', 'notes', 'show', commit_object],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            note, error = output.communicate()

            if "no note found" not in error.lower():
                note = note.split("\n")[0]
            else:
                note = None
        except subprocess.CalledProcessError:
            note = None

    return note


def clear_similar_historical_notes(commit, commit_history):

    similar_commits = commit.filter_similar_commits(commit_history)

    for similar_commit in similar_commits:
        update_note('', similar_commit.id)

    push_notes()


def edit_note(commit):
    update_note(commit.note, commit.id)
    push_notes()


def update_note(note, commit_id):
    """ Use the commit object obtained from the get notes command to overwrite a previous note
    """
    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        try:
            subprocess.check_output(['git', 'notes', 'add', '-f', '-m', note, commit_id])
        except subprocess.CalledProcessError:
            print("Could not change the distribution group for the specified commit")


def push_notes():
    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        subprocess.check_output(['git', 'push', 'origin', 'refs/notes/*'])


def delete_unstaged_changes():
    """Deletes all unstaged changes
    """
    try:
        with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
            subprocess.check_output(['git', 'checkout', '.'])
    except Exception:
        print("Could not delete local changes.")
        raise


def has_unstaged_changes():
    """Returns whether or not there are uncomitted changes
    """
    try:
        with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
            response = subprocess.check_output(['git', 'diff'])
            return True if len(response) else False
    except Exception:
        print("Could not retrieve the git diff. Please ensure the git repo is setup correctly")
        raise


def create_procedure_branch(procedure):
    """ Creates a new branch for the given procedure_code
    """
    try:
        with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
            subprocess.check_output(['git', 'checkout', 'master'])
            subprocess.check_output(['git', 'branch', procedure])
            change_procedure(procedure)
    except Exception:
        print("Unable to create a new procedure with name {}".format(procedure))
        raise


def pull_and_merge():
    """ Try a git pull and request user input to decide how a merge conflict is resolved if there is one
    """
    # Find the author of any potential merge conflicts
    try:
        subprocess.check_output(['git', 'pull'])
    except subprocess.CalledProcessError:
        # Ask the user which commit they would like to keep
        diff = subprocess.Popen(['git', 'diff'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(diff.communicate()[0])
        print("\n" + "There is a merge error.")
        print("Someone made a commit that conflicts with yours.")
        print("Would you like to accept your changes or theirs?")
        print("Type 'MINE' or 'THEIRS' to choose." + "\n")
        sys.stdout.flush()
        user_input = raw_input()

        if user_input == "MINE":
            subprocess.check_output(['git', 'checkout', '--ours', '.'])
            subprocess.check_output(['git', 'add', '.'])
            subprocess.check_output(['git', 'commit', '-a', '-m', 'merge'])
        elif user_input == "THEIRS":
            subprocess.check_output(['git', 'checkout', '--theirs', '.'])
            subprocess.check_output(['git', 'add', '.'])
            subprocess.check_output(['git', 'commit', '-a', '-m', 'merge'])
        else:
            sys.exit(1)
