from fastapi import FastAPI, UploadFile, Form, File
import os
import shutil
import subprocess
import threading
import time

app = FastAPI()

def launch_router(router_id):
    subprocess.run(["python3", "launch_router.py", router_id])

def restart_router(scenario_id):
    subprocess.run(["python3", "restart_router.py", scenario_id])

@app.post("/build_graph")
async def build_graph(scenario_id: str = Form(...), prefecture: str = Form(...), gtfs_file: UploadFile = None):
    print(f"[Build Graph] Starting build for scenario {scenario_id} with prefecture {prefecture}")
    build_dir = f"./graphs/{scenario_id}"
    os.makedirs(build_dir, exist_ok=True)

    pbf_source = f"./preloaded_osm_files/{prefecture}.pbf"
    pbf_dest = os.path.join(build_dir, f"{prefecture}.pbf")
    shutil.copy(pbf_source, pbf_dest)

    gtfs_dest = os.path.join(build_dir, gtfs_file.filename)
    with open(gtfs_dest, "wb") as f:
        f.write(await gtfs_file.read())

    process = subprocess.Popen(
        ["java", "-Xmx8G", "-jar", "otp-1.5.0-shaded.jar", "--build", build_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    output_lines = []
    for line in process.stdout:
        line = line.strip()
        output_lines.append(line)
        print(f"[OTP Build] {line}")

    process.wait()
    exit_code = process.returncode

    os.remove(gtfs_dest)
    os.remove(pbf_dest)
    os.sync()  
    time.sleep(2)
    launch_router(scenario_id)
    return {
        "status": "success" if exit_code == 0 else "fail",
    }

@app.post("/edit_graph")
async def edit_graph(scenario_id: str = Form(...), prefecture: str = Form(...), gtfs_file: UploadFile = File(...)):
    print(f"[Edit Graph] Starting edit for scenario {scenario_id} with prefecture {prefecture}")
    build_dir = f"./graphs/{scenario_id}"
    os.makedirs(build_dir, exist_ok=True)

    graph_obj_path = os.path.join(build_dir, "Graph.obj")
    if os.path.exists(graph_obj_path):
        os.remove(graph_obj_path)

    pbf_source = f"./preloaded_osm_files/{prefecture}.pbf"
    pbf_dest = os.path.join(build_dir, f"{prefecture}.pbf")
    shutil.copy(pbf_source, pbf_dest)

    gtfs_dest = os.path.join(build_dir, gtfs_file.filename)
    with open(gtfs_dest, "wb") as f:
        f.write(await gtfs_file.read())

    process = subprocess.Popen(
        ["java", "-Xmx8G", "-jar", "otp-1.5.0-shaded.jar", "--build", build_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    output_lines = []
    for line in process.stdout:
        line = line.strip()
        output_lines.append(line)
        print(f"[OTP Build] {line}")

    process.wait()
    exit_code = process.returncode

    os.remove(gtfs_dest)
    os.remove(pbf_dest)
    os.sync()  
    time.sleep(2)
    restart_router(scenario_id)
    return {
        "status": "success" if exit_code == 0 else "fail",
    }

