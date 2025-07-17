import os
import json
import subprocess
import sys

CONFIG_PATH = "./config.json"
GRAPH_BASE_PATH = "./graphs"
OTP_IMAGE = "otp-router-image"  # replace with your actual image name


def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError("config.json not found.")

    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def restart_router(scenario_id):
    config = load_config()
    if scenario_id not in config:
        raise ValueError(f"No port configured for scenario_id: {scenario_id}")

    port = config[scenario_id]
    container_name = f"otp-{scenario_id}"
    graph_path = os.path.abspath(os.path.join(GRAPH_BASE_PATH, scenario_id))

    if not os.path.exists(os.path.join(graph_path, "Graph.obj")):
        raise FileNotFoundError(f"Graph.obj not found in {graph_path}. Please build the graph first.")

    print(f"Restarting container {container_name} on port {port}...")

    # Stop and remove container if it exists
    subprocess.run(["docker", "rm", "-f", container_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Recreate the container
    run_cmd = [
        "docker", "run", "-d",
        "--name", container_name,
        "-p", f"{port}:8080",
        "-v", f"{graph_path}:/otp/graphs/{scenario_id}",
        OTP_IMAGE,
        "--load", f"/otp/graphs/{scenario_id}",
        "--router", scenario_id,
        "--server"
    ]

    print("Running command:", " ".join(run_cmd))
    result = subprocess.run(run_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Failed to restart container:\n{result.stderr}")
        return {"status": "fail", "error": result.stderr}
    else:
        print(f"Container {container_name} started successfully.")
        return {"status": "success", "container": container_name}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python restart_otp_container.py <scenario_id>")
        sys.exit(1)

    scenario_id = sys.argv[1]
    try:
        result = restart_router(scenario_id)
        print(result)
    except Exception as e:
        print({"status": "error", "message": str(e)})
        sys.exit(1)
