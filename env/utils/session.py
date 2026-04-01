from database.db import close_auth_session, create_auth_session, update_auth_last_login


class SessionManager:
    def __init__(self):
        self.current_user = None
        self.current_session_id = None

    def login(self, user_data):
        user_id = user_data["id"]
        update_auth_last_login(user_id)
        self.current_session_id = create_auth_session(user_id)
        self.current_user = user_data

    def logout(self):
        if self.current_session_id is not None:
            close_auth_session(self.current_session_id)
        self.current_session_id = None
        self.current_user = None

    def is_authenticated(self):
        return self.current_user is not None
