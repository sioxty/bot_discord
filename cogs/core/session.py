from typing import overload


class Session:
    def __init__(self, session_id: int, manager):
        self.__id: int = session_id
        self.__manager: ManagerSession = manager

    @property
    def session_id(self):
        return self.__id

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.__id}>"

    def close(self):
        self.__manager.close(self.__id)


class ManagerSession:
    def __init__(self):
        self.__sessions: dict[int, Session] = dict()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__sessions}>"

    def get_session(self, session_id: int) -> Session:
        session = self.__sessions.get(session_id)

    def create(self, session: Session):
        self.__sessions[session.session_id] = session

    def is_session(self, session_id: int):
        return session_id in self.__sessions

    @overload
    def close(self, session: int) -> Session: ...

    @overload
    def close(self, session: Session) -> Session: ...

    def close(self, session: Session | int):
        if isinstance(session, int):
            self.__close(session)
        elif isinstance(session, Session):
            self.__close(session.session_id)
        else:
            raise TypeError(
                f"Expected int or Session instance, got {type(session).__name__}"
            )

    def __close(self, session_id: int):
        try:
            del self.__sessions[session_id]
        except KeyError:
            raise ValueError(f"Session with id {session_id} does not exist.")
