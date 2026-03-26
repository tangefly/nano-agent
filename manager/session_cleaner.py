import threading
import time

class SessionCleaner:

    def __init__(self, session_manager, ttl=600):
        self.sm = session_manager
        self.ttl = ttl

    def start(self):
        def loop():
            while True:
                now = time.time()
                to_delete = []

                for sid, session in self.sm.sessions.items():
                    if now - session["last_active"] > self.ttl:
                        to_delete.append(sid)

                for sid in to_delete:
                    print(f"[CLEAN] destroy session {sid}")
                    self.sm.destroy_session(sid)

                time.sleep(5)

        threading.Thread(target=loop, daemon=True).start()
