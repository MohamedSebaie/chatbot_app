import warnings
warnings.filterwarnings("ignore")
import sys
import os
from pathlib import Path
import subprocess
import time
import signal
import logging
from typing import List, Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class ServiceManager:
    def __init__(self):
        self.project_root = project_root
        self.processes: List[subprocess.Popen] = []
        self.running = True

    def start_vllm_server(self) -> Optional[subprocess.Popen]:
        """Start the vLLM server."""
        try:
            command = [
                "vllm",
                "serve",
                "NousResearch/Meta-Llama-3-8B-Instruct",
                "--dtype", "float16",
                "--max_num_seqs", "2",
                "--max_model_len", "4096",
                "--gpu_memory_utilization", "0.8",
                "--distributed_executor_backend", "ray",
                "--tensor_parallel_size", "4",
                "--enforce_eager",
                "--host", "0.0.0.0",
                "--port", "8000"
            ]
            logger.info(f"Starting vLLM server with command: {' '.join(command)}")
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env={
               **os.environ,
               "NCCL_DEBUG": "INFO",
               "NCCL_IB_DISABLE": "1",
               "NCCL_P2P_DISABLE": "1"
           }
            )
            # Wait for server to start
            time.sleep(100)  # Increased wait time as model loading takes longer
            if process.poll() is not None:
                # Process has terminated, get error output
                _, stderr = process.communicate()
                logger.error(f"vLLM server failed to start: {stderr}")
                return None
            self.processes.append(process)
            logger.info("Started vLLM server")
            return process
        except Exception as e:
            logger.error(f"Failed to start vLLM server: {str(e)}")
            return None

    def start_fastapi_server(self) -> Optional[subprocess.Popen]:
        """Start the FastAPI server."""
        try:
            process = subprocess.Popen(
                [
                    "uvicorn", 
                    "app.api.routes:router", 
                    "--host", "0.0.0.0",
                    "--port", "8080",
                    "--reload"
                ],
                cwd=self.project_root
            )
            self.processes.append(process)
            logger.info("Started FastAPI server")
            return process
        except Exception as e:
            logger.error(f"Failed to start FastAPI server: {e}")
            return None

    def start_streamlit(self) -> Optional[subprocess.Popen]:
        """Start the Streamlit frontend."""
        try:
            process = subprocess.Popen(
                [
                    "streamlit", 
                    "run", 
                    "frontend/app.py",
                    "--server.port", "8501",
                    "--server.address", "0.0.0.0"
                ],
                cwd=self.project_root
            )
            self.processes.append(process)
            logger.info("Started Streamlit server")
            return process
        except Exception as e:
            logger.error(f"Failed to start Streamlit: {e}")
            return None

    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info("Received shutdown signal")
        self.shutdown()

    def shutdown(self):
        """Shutdown all services."""
        self.running = False
        logger.info("Shutting down services...")
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)  # Wait up to 5 seconds
            except subprocess.TimeoutExpired:
                process.kill()  # Force kill if not terminated
            except Exception as e:
                logger.error(f"Error shutting down process: {e}")

    def check_port_available(self, port: int) -> bool:
        """Check if a port is available."""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0

    def wait_for_service(self, port: int, timeout: int = 30):
        """Wait for a service to become available."""
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.check_port_available(port):
                return True
            time.sleep(1)
        return False

    def run(self):
        """Run all services."""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Check ports
        ports = [8000, 8080, 8501]
        for port in ports:
            if not self.check_port_available(port):
                logger.error(f"Port {port} is already in use")
                return

        # Create necessary directories
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(settings.VECTOR_STORE_PATH).mkdir(parents=True, exist_ok=True)

        # Start services
        vllm_server = self.start_vllm_server()
        if not vllm_server:
            logger.error("Failed to start vLLM server")
            self.shutdown()
            return

        # Wait for vLLM server to start
        logger.info("Waiting for vLLM server to start...")
        if not self.wait_for_service(8000):
            logger.error("vLLM server failed to start")
            self.shutdown()
            return

        # Start other services
        if not self.start_fastapi_server():
            logger.error("Failed to start FastAPI server")
            self.shutdown()
            return

        if not self.start_streamlit():
            logger.error("Failed to start Streamlit")
            self.shutdown()
            return

        logger.info("All services started successfully")
        logger.info("Available at:")
        logger.info("- vLLM API: http://localhost:8000/v1")
        logger.info("- FastAPI: http://localhost:8080")
        logger.info("- Streamlit: http://localhost:8501")

        # Keep running until shutdown
        try:
            while self.running:
                # Check if any process has terminated
                for process in self.processes:
                    if process.poll() is not None:
                        logger.error(f"Process terminated unexpectedly: {process}")
                        self.shutdown()
                        return
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start services
    service_manager = ServiceManager()
    service_manager.run()