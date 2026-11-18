from unittest.mock import Mock

import pytest
from requests import ConnectionError, HTTPError, Timeout
from vk_api.bot_longpoll import VkBotEvent, VkBotMessageEvent


@pytest.fixture
def handlers(monkeypatch):
    monkeypatch.setenv('BOT_TOKEN', 'test')
    monkeypatch.setenv('DB_DSN', 'postgresql://test@localhost/test')
    monkeypatch.setenv('GROUP_ID', '123')
    monkeypatch.setenv('MARKETING_URL', 'https://marketing.example')
    monkeypatch.setenv('PRINT_URL', 'https://print.example')
    monkeypatch.setenv('PRINT_URL_QR', 'https://print.example/qr/')
    from src import handlers

    return handlers


def test_longpoll_keeps_cursor_and_processes_the_whole_batch(handlers, mocker):
    ignored = VkBotEvent({'type': 'message_reply', 'group_id': 123, 'object': {}})
    allow = VkBotEvent({'type': 'message_allow', 'group_id': 123, 'object': {'user_id': 1}})
    messages = [
        VkBotMessageEvent(
            {
                'type': 'message_new',
                'group_id': 123,
                'object': {'message': {'from_id': user_id, 'peer_id': user_id, 'text': 'help', 'attachments': []}},
            }
        )
        for user_id in (2, 3)
    ]
    longpoll = Mock()
    longpoll.check.side_effect = [Timeout(), [ignored, allow, *messages], KeyboardInterrupt()]
    create_longpoll = mocker.patch.object(handlers.vk, 'create_longpoll', side_effect=[ConnectionError(), longpoll])
    sleep = mocker.patch.object(handlers.time, 'sleep')
    main_page = mocker.patch.object(handlers.kb, 'main_page')
    analyzer = mocker.patch.object(handlers, 'message_analyzer', side_effect=[Timeout(), None])
    mocker.patch.object(handlers.vk, 'send', side_effect=Timeout())

    with pytest.raises(KeyboardInterrupt):
        handlers.event_loop()

    assert create_longpoll.call_count == 2
    assert sleep.call_count == 2
    main_page.assert_called_once()
    assert [call.args[0].user_id for call in analyzer.call_args_list] == [2, 3]


def test_membership_http_error_is_not_treated_as_membership(handlers, mocker):
    response = Mock()
    response.raise_for_status.side_effect = HTTPError()
    response.json.return_value = {'detail': 'service unavailable'}
    mocker.patch.object(handlers.auth.requests, 'get', return_value=response)

    with pytest.raises(HTTPError):
        handlers.auth.check_union_member(Mock(user_id=1), 'Иванов', '123')
    response.json.assert_not_called()
