import json, os, socket, subprocess

GRAPH_DIR = "graphs"
ROUTER_MAP_FILE = "router_map.json"
OTP_PORT_START = 8800

def restart_router(router_id):
    router_id = router_id.replace("\\", "/").strip()
    graph_path = os.path.join(GRAPH_DIR, router_id, "Graph.obj")


    container_name = f"otp-{router_id}"


    container_graph_dir = f"/app/graphs/{router_id}"
    subprocess.run([
        "docker", "exec", container_name,
        "rm", "-f", f"{container_graph_dir}/Graph.obj"
    ])
    subprocess.run(["docker", "cp", graph_path, f"{container_name}:{container_graph_dir}/Graph.obj"])

    container_name = f"otp-{router_id}"
    subprocess.run(["docker", "restart", container_name])

    subprocess.run(["docker", "exec", "otp-nginx", "nginx", "-s", "reload"])

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python launch_router.py <router_id>")
    else:
        restart_router(sys.argv[1])
