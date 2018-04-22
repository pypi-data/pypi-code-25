from . import repo


def run():
    scilicet_repo = repo.load()
    repo.dump(scilicet_repo)
