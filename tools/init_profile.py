#!/usr/bin/env python3
"""Create one new private CLI profile outside this delivery; never overwrite."""
import argparse
import json
import os
from pathlib import Path
import stat
import sys
import uuid

# Only these verified root-level operating-system aliases are accepted.
OS_ALIASES = {Path('/tmp'): Path('/private/tmp'), Path('/var'): Path('/private/var'), Path('/etc'): Path('/private/etc')}


def new_destination(argument, delivery):
    requested = Path(argument)
    absolute = requested if requested.is_absolute() else Path.cwd() / requested
    parts = absolute.parts[1:]
    current = Path('/')
    aliases = []
    for index, part in enumerate(parts):
        if part in ('', '.'):
            continue
        if part == '..':
            current = current.parent
            continue
        child = current / part
        try:
            info = child.lstat()
        except FileNotFoundError:
            if index != len(parts) - 1:
                raise ValueError('O diretório pai do novo perfil deve existir.')
            destination = child
            break
        if index == len(parts) - 1:
            raise ValueError('O destino já existe; escolha um diretório novo.')
        if stat.S_ISLNK(info.st_mode):
            allowed = OS_ALIASES.get(child)
            if allowed is None or child.resolve(strict=True) != allowed:
                raise ValueError('Ancestral simbólico de usuário recusado.')
            aliases.append({'alias': str(child), 'physical_path': str(allowed)})
            current = allowed
        elif stat.S_ISDIR(info.st_mode):
            current = child
        else:
            raise ValueError('Um ancestral do destino não é diretório.')
    else:
        raise ValueError('O destino precisa ser um diretório novo explícito.')
    if destination == delivery or delivery in destination.parents:
        raise ValueError('O perfil deve ficar fora da entrega.')
    return destination, aliases


def open_directory_without_links(path):
    descriptor = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for component in path.parts[1:]:
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, help='Diretório novo do perfil, fora desta entrega; o pai deve existir.')
    args = parser.parse_args()
    created = False
    destination = None
    try:
        if os.name != 'posix' or not all(hasattr(os, name) for name in ('O_NOFOLLOW', 'O_DIRECTORY')):
            raise ValueError('Requer POSIX com O_NOFOLLOW e O_DIRECTORY.')
        delivery = Path(__file__).resolve(strict=True).parents[1]
        destination, aliases = new_destination(args.root, delivery)
        try:
            from zuuuin_engine import __version__
            from zuuuin_engine.state import atomic_json, now, validate_state
        except ModuleNotFoundError as exc:
            raise ValueError('Runtime ausente: instale o wheel local nesta venv antes de criar o perfil.') from exc
        stamp = now()
        identity = str(uuid.uuid4())
        private = destination / 'private'
        state = {'schema_version': '1.0', 'id': identity, 'run_id': identity,
                 'revision': 0, 'state_revision': 0,
                 'created_at': stamp, 'updated_at': stamp, 'started_at': stamp,
                 'phase': 'local', 'phase_status': 'in_progress',
                 'events': [], 'evidence_refs': [],
                 'roots': {'work': str(destination), 'private': str(private),
                           'source': str(destination / 'source'), 'test': str(destination / 'test'),
                           'release': str(destination / 'release')}}
        validate_state(state)
        parent_fd = open_directory_without_links(destination.parent)
        try:
            os.mkdir(destination.name, mode=0o700, dir_fd=parent_fd)
            created = True
        finally:
            os.close(parent_fd)
        for relative in ('private', 'source', 'test', 'release', 'private/state',
                         'private/state/events', 'private/policies', 'private/requests', 'private/outputs'):
            (destination / relative).mkdir(mode=0o700)
        # Recheck canonical ancestors before persisting the private control files.
        descriptor = open_directory_without_links(private / 'state')
        os.close(descriptor)
        atomic_json(private / 'state/execution.json', state)
        atomic_json(private / 'policies/bootstrap.json', {
            'external_publication_enabled': False,
            'external_installation_enabled': False,
            'skill_roots': []})
        atomic_json(private / 'policies/authorizations.json', {'authorizations': {}})
        print(json.dumps({'status': 'created', 'profile_root': str(destination),
                          'private_root': str(private), 'runtime_version': __version__,
                          'normalized_os_aliases': aliases}, ensure_ascii=False))
        return 0
    except (OSError, ValueError) as exc:
        error = {'status': 'refused', 'error': str(exc), 'profile_directory_created': created}
        if created:
            error['partial_profile_root'] = str(destination)
            error['next_step'] = 'Preserve o perfil parcial e escolha outro destino novo; nada será apagado ou sobrescrito automaticamente.'
        print(json.dumps(error, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
