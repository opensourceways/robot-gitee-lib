from abc import ABC, abstractmethod
import gitee

from robotgitee.logutil import LogUtil


class NoteEventHandler(ABC):
    @abstractmethod
    def handle_note_event(self, event: gitee.NoteEvent, log: LogUtil) -> None:
        pass


class PullRequestEventHandler(ABC):
    @abstractmethod
    def handle_pull_request_event(self, event: gitee.PullRequestEvent,
                                  log: LogUtil) -> None:
        pass


class IssueEventHandler(ABC):
    @abstractmethod
    def handle_issue_event(self, event: gitee.IssueEvent,
                           log: LogUtil) -> None:
        pass


class PushEventHandler(ABC):
    @abstractmethod
    def handle_push_event(self, event: gitee.PushEvent, log: LogUtil) -> None:
        pass


class _Handlers(object):
    _field_url = "url"
    _field_action = "action"

    def __init__(self):
        self.pull_request_handler = None
        self.issue_event_handler = None
        self.push_event_handler = None
        self.note_event_handler = None

    def register_handler(self, robot: object) -> None:
        if isinstance(robot, PullRequestEventHandler):
            self.pull_request_handler = robot

        if isinstance(robot, IssueEventHandler):
            self.issue_event_handler = robot

        if isinstance(robot, PushEventHandler):
            self.push_event_handler = robot

        if isinstance(robot, NoteEventHandler):
            self.note_event_handler = robot

    def get_handlers(self) -> dict:
        d = dict()

        if self.pull_request_handler is not None:
            d[gitee.EVENT_TYPE_PR] = self.handle_pull_request_event

        if self.issue_event_handler is not None:
            d[gitee.EVENT_TYPE_ISSUE] = self.handle_issue_event

        if self.push_event_handler is not None:
            d[gitee.EVENT_TYPE_PUSH] = self.handle_push_event

        if self.note_event_handler is not None:
            d[gitee.EVENT_TYPE_NOTE] = self.handle_note_event

        return d

    def handle_pull_request_event(self, payload, log: LogUtil) -> None:
        try:
            event = gitee.convert_to_pr_event(payload)

            log.field(self._field_url, event.pull_request.html_url)
            log.field(self._field_action, event.action_desc)

            self.pull_request_handler.handle_pull_request_event(event, log)

        except Exception as e:
            log.error(str(e))

    def handle_issue_event(self, payload, log: LogUtil) -> None:
        try:
            event = gitee.convert_to_issue_event(payload)

            log.field(self._field_url, event.issue.html_url)
            log.field(self._field_action, event.action)

            self.issue_event_handler.handle_issue_event(event, log)

        except Exception as e:
            log.error(str(e))

    def handle_push_event(self, payload, log: LogUtil) -> None:
        try:
            event = gitee.convert_to_push_event(payload)

            repo = event.repository
            log.field("org", repo.namespace)
            log.field("repo", repo.path)
            log.field("ref", event.ref)
            log.field("head", event.after)

            self.push_event_handler.handle_push_event(event, log)

        except Exception as e:
            log.error(str(e))

    def handle_note_event(self, payload, log: LogUtil) -> None:
        try:
            event = gitee.convert_to_note_event(payload)

            log.field("commenter", event.comment.user.login)
            log.field(self._field_url, event.comment.html_url)
            log.field(self._field_action, event.action)

            self.note_event_handler.handle_note_event(event, log)

        except Exception as e:
            log.error(str(e))
