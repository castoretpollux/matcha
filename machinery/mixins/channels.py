import logging
from django.conf import settings


logger = logging.getLogger("django")

class ChannelMixin(object):

    def _send_msg(self, msg):
        "This must be overridden"
        raise NotImplementedError

    def send_log(self, text: str) -> None:
        if settings.DEBUG:
            logger.debug(self.channel_id, "LOG    :", text)
        self._send_msg({'type': 'runner.log', 'message': {'content': text, 'session_id': self.session_id}})

    def send_partial(self, data: dict) -> None:
        if settings.DEBUG:
            logger.debug(self.channel_id, "PARTIAL:", data)
        self._send_msg({'type': 'runner.partial', 'message': {'data': data}})

    def send_result(self, data: dict) -> None:
        if settings.DEBUG:
            logger.debug(self.channel_id, "RESULT :", data)
        self._send_msg({'type': 'runner.result', 'message': {'data': data}})

    def send_error(self, data: dict) -> None:
        if settings.DEBUG:
            logger.debug(self.channel_id, "ERROR  :", data)
        self._send_msg({'type': 'runner.error', 'message': {'data': data, 'session_id': self.session_id}})

    def send_message(self, data: dict) -> None:
        if settings.DEBUG:
            logger.debug(self.channel_id, "Message    :", data)
        self._send_msg({'type': 'runner.message', 'message': {'data': data}})

    def send_title(self) -> None:
        if settings.DEBUG:
            logger.debug(self.session_id, "Title    :", self.session_title)
        self._send_msg({'type': 'runner.title', 'message': {'session_id': self.session_id, 'title': self.session_title}})
