import docker
import os

client = docker.from_env()

class DockerManager:
    def __init__(self, image="agent-python:latest"):
        self.image = image

    def create_container(self, session_id):
        # 工作目录和数据目录
        workdir = os.path.abspath(f"./tmp/agent_sandbox/{session_id}")
        os.makedirs(workdir, exist_ok=True)
        data_dir = os.path.abspath("./data")

        # 挂载目录
        volumes = {
            workdir: {"bind": "/app", "mode": "rw"},
            data_dir: {"bind": "/data", "mode": "rw"}
        }

        container = client.containers.run(
            image=self.image,           # 镜像
            command="bash",             # 启动 bash
            detach=True,                # 后台运行
            tty=True,                   # 分配 tty，支持交互
            stdin_open=True,            # 打开 stdin
            name=f"agent-{session_id[:8]}",  # 容器名字
            working_dir="/app",         # 容器内默认工作目录
            volumes=volumes,            # 挂载目录
            mem_limit="4g",           # 内存限制
            nano_cpus=4_000_000_000,    # 1 CPU
            pids_limit=64,              # 最大进程数
            tmpfs={"/tmp": ""},          # tmpfs 挂载
            auto_remove=False           # 不自动删除，方便多次 exec
        )

        return container.id

    def exec(self, container_id, cmd):
        container = client.containers.get(container_id)
        result = container.exec_run(cmd, stdout=True, stderr=True)
        return result.output.decode()

    def exec_stream(self, container_id, cmd):
        """
        流式执行命令，返回 generator，每次 yield 一行输出
        cmd: list[str] 推荐列表形式 ["python", "script.py"]
        """
        container = client.containers.get(container_id)

        # 创建 exec 对象
        exec_instance = client.api.exec_create(
            container.id,
            cmd,
            stdout=True,
            stderr=True,
            stdin=False,
            tty=False  # tty=False 可以保证输出逐行
        )

        # 获取输出流
        output_stream = client.api.exec_start(exec_instance['Id'], stream=True)

        for chunk in output_stream:
            # chunk 是 bytes，需要 decode
            line = chunk.decode(errors="replace")
            # 按行 yield，如果 chunk 里包含多行
            for l in line.splitlines(keepends=True):
                yield l

        # 获取返回码
        inspect = client.api.exec_inspect(exec_instance['Id'])
        # yield f"[EXIT_CODE] {inspect['ExitCode']}"

    def destroy_container(self, container_id):
        try:
            container = client.containers.get(container_id)
            container.stop()
            container.remove()
        except Exception:
            pass
