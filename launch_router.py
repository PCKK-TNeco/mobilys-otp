import json, os, socket, subprocess

GRAPH_DIR = "graphs"
ROUTER_MAP_FILE = "router_map.json"
OTP_PORT_START = 8800

def get_available_port(start=OTP_PORT_START, end=9000):
    # Load router_map.json to see already assigned ports
    try:
        with open(ROUTER_MAP_FILE, "r") as f:
            router_map = json.load(f)
            used_ports = set(router_map.values())
    except FileNotFoundError:
        used_ports = set()

    # Scan for a free port not in use AND not in the router_map
    for port in range(start, end):
        if port in used_ports:
            continue
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port

    raise RuntimeError("No available ports in the specified range.")

def launch_router(router_id):
    router_id = router_id.replace("\\", "/").strip()
    graph_path = os.path.join(GRAPH_DIR, router_id, "Graph.obj")
    print("this is graph_path", graph_path)
    if not os.path.exists(graph_path):
        print(f"[!] Graph.obj missing at {graph_path}")
        return

    if os.path.exists(ROUTER_MAP_FILE):
        with open(ROUTER_MAP_FILE, "r") as f:
            router_map = json.load(f)
    else:
        router_map = {}


    if router_id in router_map:
        print(f"[✓] Router {router_id} already exists.")
        return

    port = get_available_port()

    # 🔧 Get absolute path to host-side graph directory
    host_graph_dir = os.path.abspath(os.path.join(GRAPH_DIR, router_id))
    print(f"[DEBUG] Mounting graph from: {host_graph_dir}")

    subprocess.run([
        "docker", "run", "-d",
        "--name", f"otp-{router_id}",
        "-p", f"{port}:8080",
        "-v", f"{host_graph_dir}:/app/graphs/{router_id}",
        "-e", f"ROUTER_ID={router_id}",
        "otp-router-image"
    ])

    router_map[router_id] = port
    with open(ROUTER_MAP_FILE, "w") as f:
        json.dump(router_map, f, indent=2)

    subprocess.run(["python", "generate_nginx_routes.py"])
    subprocess.run(["docker", "exec", "otp-nginx", "nginx", "-s", "reload"])

    print(f"[✓] Launched router {router_id} at http://localhost:{port}/otp/routers/{router_id}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python launch_router.py <router_id>")
    else:
        launch_router(sys.argv[1])
