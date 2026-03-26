import subprocess
import os
import traceback
import uuid
import shutil

from manager import SessionManager

class SandboxExecTool:

    def __init__(self, image="agent-python:latest"):
        self.image = image

    def run_python(self, code: str, timeout=10):
        """
        执行 Python 代码
        """
        print("Run Python Code ...")
        return self._run_in_docker("python", code, timeout=timeout)

    def run_bash(self, command: str, timeout=10):
        """
        执行 Bash 命令
        """
        print("Run Bash Script ...")
        return self._run_in_docker("bash", command, timeout=timeout)

    def _run_in_docker(self, exec_type: str, content: str, timeout=10):
        job_id = str(uuid.uuid4())
        workdir = f"./tmp/agent_sandbox/{job_id}"
        os.makedirs(workdir, exist_ok=True)

        print(f"Working in {workdir} ...")

        # 临时文件名
        filename = "code.py" if exec_type == "python" else "script.sh"
        file_path = os.path.join(workdir, filename)

        try:
            with open(file_path, "w") as f:
                f.write(content)
            if exec_type == "bash":
                os.chmod(file_path, 0o755)  # 给 bash 脚本加执行权限
        except Exception:
            return {
                "success": False,
                "error": "Failed to write file:\n" + traceback.format_exc()
            }

        data_dir = os.path.abspath("./data")

        # Docker 命令
        cmd = [
            "docker", "run", "--rm",
            "--memory=512m",
            "--cpus=1",
            "--pids-limit=64",
            "--tmpfs", "/tmp",
            "-v", f"{workdir}:/app",
            "-v", f"{data_dir}:/data",
            "-w", "/app",
            self.image,
        ]

        # 执行 Python 或 Bash
        if exec_type == "python":
            cmd += ["python", filename]
        else:
            cmd += ["bash", filename]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Execution timeout"}
        except Exception:
            return {"success": False, "error": traceback.format_exc()}
        finally:
            # 清理临时目录
            try:
                shutil.rmtree(workdir)
            except Exception:
                pass

    def _run_in_docker_stream(self, exec_type: str, content: str, session_id: str, timeout=10):
        workdir = f"./tmp/agent_sandbox/{session_id}"
        os.makedirs(workdir, exist_ok=True)

        print(f"Working in {workdir} ...")

        # 临时文件名
        filename = "code.py" if exec_type == "python" else "script.sh"
        file_path = os.path.join(workdir, filename)

        print(f"{content}")

        try:
            with open(file_path, "w") as f:
                f.write(content)
            if exec_type == "bash":
                os.chmod(file_path, 0o755)  # 给 bash 脚本加执行权限
        except Exception:
            return {
                "success": False,
                "error": "Failed to write file:\n" + traceback.format_exc()
            }

        data_dir = os.path.abspath("./data")

        # Docker 命令
        cmd = [
            "docker", "run", "--rm",
            "--memory=512m",
            "--cpus=1",
            "--pids-limit=64",
            "--tmpfs", "/tmp",
            "-v", f"{workdir}:/app",
            "-v", f"{data_dir}:/data",
            "-w", "/app",
            self.image,
        ]

        # 执行 Python 或 Bash
        if exec_type == "python":
            cmd += ["python", filename]
            cmd_str = f"python {filename}"
        else:
            cmd += ["bash", filename]
            cmd_str = f"bash {filename}"

        cwd = "/app"
        yield {
            "type": "tool_start",
            "cmd": cmd_str,
            "cwd": cwd
        }

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for line in process.stdout:
            yield {
                "type": "tool_stdout",
                "content": line
            }

        process.wait()

        yield {
            "type": "tool_status",
            "content": f"exit code: {process.returncode}"
        }

        yield {
            "type": "tool_end"
        }

    def run_bash_stream(self, script: str, session_id: str):
        yield {"type": "step", "content": "Run Bash"}

        yield from self._run_in_docker_stream("bash", script)


    def run_python_stream(self, code: str, session_id: str):
        yield {"type": "step", "content": "Run Python"}

        yield from self._run_in_docker_stream("python", code)


