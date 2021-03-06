import os.path
import sys
from pathlib import Path

import click
from tempfile import TemporaryDirectory

from . import __VERSION__
from .constants import (
    CONFIG_DIR, CACHE_DIR, PACMAN_SYNC_CACHE_DIR, PROJECT_NAME
)
from .repository import Repository

for directory in [CONFIG_DIR, CACHE_DIR, PACMAN_SYNC_CACHE_DIR]:
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass

available_repositories = [os.path.basename(str(fn)).split('.')[:-1][0]
                          for fn in Path(CONFIG_DIR).glob('*.json')]


def is_valid_repository(ctx, param, value):
    if value and value not in available_repositories:
        click.echo('Repository with that name does not exist', file=sys.stderr)
        sys.exit(1)
    elif value:
        return Repository(value)
    return None


@click.group()
@click.version_option(prog_name=PROJECT_NAME, version=__VERSION__)
def cli():
    pass


@click.command(short_help='Initialize a new repository.')
@click.argument('repository')
@click.argument('basedir')
@click.argument('mail')
def init(repository, basedir, mail):
    _repository = Repository()

    _repository.create(repository, basedir, mail)


@click.command(short_help='Add a new package to an existing repository.')
@click.option('--repository', callback=is_valid_repository)
@click.argument('package')
def add(package, repository=None):
    if not repository:
        if len(available_repositories) != 1:
            click.echo(
                "Repository ambiguous, specify one with --repository.",
                file=sys.stderr
            )
            sys.exit(1)
        repository = Repository(available_repositories[0])

    repository.add(package)


@click.command(short_help='Remove a package from a repository')
@click.option('--repository', callback=is_valid_repository)
@click.argument('package')
def remove(repository, package):
    if not repository:
        if len(available_repositories) != 1:
            click.echo(
                "Repository ambiguous, specify one with --repository.",
                file=sys.stderr
            )
            sys.exit(1)
        repository = Repository(available_repositories[0])

    # TODO: Implementation missing
    repository.remove_and_sign(package)


@click.command('list', short_help='List repositories and related packages')
@click.option('--repository', callback=is_valid_repository)
def _list(repository):
    if repository:
        repositories = [repository]
    else:
        repositories = [Repository(name) for name in available_repositories]

    for repository in repositories:
        click.echo("{0}: {1} ({2} packages)".format(
            repository.name, repository.basedir, len(repository.packages)))

        for package in repository.packages:
            if not package.pkgs:
                click.echo(' - {0} (not built yet)'.format(package.name))
            elif len(package.pkgs) == 1 and package.name in package.pkgs:
                click.echo(' - {0} ({1})'.format(
                    package.name, package.pkgs[package.name]['version']))
            else:
                click.echo(' - {0}'.format(package.name))
                for pkg, pkginfo in package.pkgs.items():
                    click.echo('   - {0} ({1})'.format(
                        pkg, pkginfo['version']))


@click.command(short_help='Update packages in repository to latest version.')
@click.option('--repository', callback=is_valid_repository)
@click.option('--force', is_flag=True, default=False,
              help='Bypass up-to-date check.')
@click.option('--jobs', type=int, help='Number of jobs to run builds with.')
def update(repository, force, jobs):
    if repository:
        repositories = [repository]
    else:
        repositories = [Repository(name) for name in available_repositories]

    with TemporaryDirectory(prefix=PROJECT_NAME, suffix='pkgs') as pkgcache:
        for repository in repositories:
            for pkg in repository.packages:
                pkg.update(
                    force=force,
                    buildopts=dict(
                        jobs=jobs,
                        pkgcache=pkgcache
                    )
                )
                repository.save()


cli.add_command(init)
cli.add_command(add)
cli.add_command(remove)
cli.add_command(_list)
cli.add_command(update)


if __name__ == '__main__':
    cli()
