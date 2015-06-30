from git import Repo

from command import AggregatedCommand, Command, CommandException


repo = Repo('.')

_FEATURE_BRANCH_PREFIX = 'feature_'


def _start(feature):
    if feature is None:
        raise CommandException('No feature name given')

    feature_branch = '%s%s' % (_FEATURE_BRANCH_PREFIX, feature)
    if repo.is_dirty():
        raise CommandException('Please commit all untracked files before creating a feature branch')

    if map(lambda head: head.name, repo.heads).count(feature_branch) != 0:
        raise CommandException("Feature branch '%s' already exists." % feature_branch)

    repo.git.fetch()
    repo.create_head(feature_branch, 'origin/master')
    repo.heads[feature_branch].checkout()


def _finish():
    current_branch = repo.git.rev_parse('--abbrev-ref', 'HEAD')
    if current_branch.startswith(_FEATURE_BRANCH_PREFIX) == False:
        raise CommandException('Please checkout to feature branch')
    repo.git.fetch()
    repo.git.rebase('-i', 'origin/master')
    repo.git.push('-f', 'origin', 'HEAD:%s' % current_branch)
    repo.git.push('origin', 'HEAD:master')
    repo.git.checkout('master')
    repo.git.rebase('origin/master')
    repo.git.push('origin', ':%s' % current_branch)
    repo.git.branch('-D', current_branch)


command = AggregatedCommand('feature', 'Manages a feature branches.', [
    Command('start', 'Creates a new feature branch.', _start, '<feature name>'),
    Command('finish', 'Closes and pushes a feature to a master branch.', _finish)
])