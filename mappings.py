import json
import typing
from dataclasses import dataclass


@dataclass
class EventMappingSource(object):
    owner: str
    repository: str
    workflow_file_name: str


@dataclass
class EventMappingDestination(object):
    owner: str
    repository: str


@dataclass
class EventMapping(object):
    source: EventMappingSource
    destination: EventMappingDestination

    @staticmethod
    def read_event_mappings(json_file: typing.IO) -> typing.List['EventMapping']:
        def is_empty(a_string: str):
            return a_string is not None and a_string.strip() == ''

        def get_owner_and_repository(json_obj: typing.Dict):
            owner = json_obj['owner']
            repository = json_obj['repository']
            assert not is_empty(owner), 'the source must be non-null'
            assert not is_empty(repository), 'the target must be non-null'
            return owner, repository

        def build_event_source(json_obj: typing.Dict) -> EventMappingSource:
            owner, repository = get_owner_and_repository(json_obj)
            return EventMappingSource(owner, repository, json_obj['workflow_file_name'])

        def build_event_target(json_obj: typing.Dict) -> EventMappingDestination:
            owner, repository = get_owner_and_repository(json_obj)
            return EventMappingDestination(owner, repository)

        json_str = json_file.read()
        obs = json.loads(json_str)['mappings']
        return [EventMapping(build_event_source(em_config['source']),
                             build_event_target(em_config['target'])) for em_config in obs]
