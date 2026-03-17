import subprocess
import tempfile
import os
import traceback
import uuid


class PythonExecTool:

    def __init__(self, image="agent-python:latest"):
        self.image = image

    def run(self, code: str):
        job_id = str(uuid.uuid4())
        workdir = f"./tmp/agent_sandbox/{job_id}"
        os.makedirs(workdir, exist_ok=True)

        print(f"work in {workdir} ...")

        code_path = os.path.join(workdir, "code.py")

        data_dir = os.path.abspath("./data")

        # ✅ 写入代码文件
        try:
            with open(code_path, "w") as f:
                f.write(code)
                print(f"code: \n{code}")
        except Exception:
            return {
                "success": False,
                "error": "Failed to write code:\n" + traceback.format_exc()
            }

        # ✅ Docker 执行命令
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
            "python", "code.py"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10  # 防止死循环
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Execution timeout"
            }
        except Exception:
            return {
                "success": False,
                "error": traceback.format_exc()
            }
        finally:
            # ✅ 清理目录（很重要）
            try:
                import shutil
                shutil.rmtree(workdir)
            except Exception:
                pass
