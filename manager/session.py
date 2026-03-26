import time

class Session:
    def __init__(self, session_id, container_id):
        self.session_id = session_id
        self.container_id = container_id
        self.last_active = time.time()