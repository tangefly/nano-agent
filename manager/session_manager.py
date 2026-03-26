import uuid
import time

from .docker_manager import DockerManager

class SessionManager:

    def __init__(self):
        self.sessions = {}
        self.docker = DockerManager()

    def create_session(self):
        session_id = str(uuid.uuid4())

        container_id = self.docker.create_container(session_id)

        self.sessions[session_id] = {
            "container_id": container_id,
            "last_active": time.time()
        }

        return session_id

    def exec(self, session_id, cmd):
        session = self.sessions.get(session_id)
        if not session:
            raise Exception("session not found")

        output = self.docker.exec(session["container_id"], cmd)

        # 更新活跃时间
        session["last_active"] = time.time()

        return output

    def exec_stream(self, session_id, cmd):
        """
        流式执行命令，每次 yield 一行输出
        cmd: list[str] 推荐列表形式
        """
        session = self.sessions.get(session_id)
        if not session:
            raise Exception("session not found")

        # 更新活跃时间
        session["last_active"] = time.time()

        # 调用 DockerManager 流式执行
        for line in self.docker.exec_stream(session["container_id"], cmd):
            # yield line
            yield {
                "type": "tool_stdout",
                "content": line
            }

    def destroy_session(self, session_id):
        session = self.sessions.pop(session_id, None)
        if session:
            self.docker.destroy_container(session["container_id"])
