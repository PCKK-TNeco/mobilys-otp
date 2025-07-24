import json
import os
import subprocess
import sys

ROUTER_MAP_FILE = "router_map.json"

def delete_router(router_id: str):
    router_id = router_id.replace("\\", "/").strip()

    try:
        with open(ROUTER_MAP_FILE, "r") as f:
            router_map = json.load(f)
    except FileNotFoundError:
        print(f"[!] router_map.json not found, nothing to delete.", file=sys.stderr)
        sys.exit(1)

    if router_id not in router_map:
        print(f"[!] Router '{router_id}' not found in map.", file=sys.stderr)
        sys.exit(1)

    container_name = f"otp-{router_id}"
    try:
        subprocess.run(["docker", "stop", container_name], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["docker", "rm", container_name], check=True, stdout=subprocess.DEVNULL)
        print(f"[Delete Router] Stopped and removed container '{container_name}'")
    except subprocess.CalledProcessError as e:
        print(f"[Error] Failed to stop/remove container '{container_name}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        del router_map[router_id]
        with open(ROUTER_MAP_FILE, "w") as f:
            json.dump(router_map, f, indent=2)
        print(f"[Delete Router] Removed '{router_id}' from {ROUTER_MAP_FILE}")
    except Exception as e:
        print(f"[Error] Unable to update {ROUTER_MAP_FILE}: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        subprocess.run(["python3", "generate_nginx_routes.py"], check=True)
        subprocess.run(
            ["docker", "exec", "otp-nginx", "nginx", "-s", "reload"],
            check=True,
            stdout=subprocess.DEVNULL
        )
        print("[Delete Router] Regenerated nginx config and reloaded proxy")
    except subprocess.CalledProcessError as e:
        print(f"[Error] Failed to regenerate or reload nginx: {e}", file=sys.stderr)
        sys.exit(1)

    # Sukses
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 delete_router.py <router_id>", file=sys.stderr)
        sys.exit(1)
    delete_router(sys.argv[1])
