from fastapi import FastAPI, UploadFile, Form, File, HTTPException
import os
import shutil
import subprocess
import threading
import time
import osmium

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

    pbf_source = f"./preloaded_osm_files/{prefecture}.osm.pbf"
    pbf_dest = os.path.join(build_dir, f"{prefecture}.osm.pbf")
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

@app.post("/delete_graph")
async def delete_graph(scenario_id: str = Form(...)):
    print(f"[Delete Graph] Starting delete for scenario {scenario_id}")
    build_dir = f"./graphs/{scenario_id}"

    if os.path.exists(build_dir):
        try:
            shutil.rmtree(build_dir)
            print(f"[Delete Graph] Successfully deleted graph directory for {scenario_id}")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete graph directory: {e}"
            )
        
    else:
        print(f"[Delete Graph] No graph directory found for {scenario_id}")
        return {
            "status": "success",
        }

    proc = subprocess.run(
        ["python3", "delete_router.py", scenario_id],
        capture_output=True,
        text=True
    )
    if proc.returncode != 0:
        err = proc.stderr.strip() or proc.stdout.strip()
        print(f"[Delete Graph] delete_router.py failed: {err}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting router instance: {err}"
        )

    time.sleep(1)
    print(f"[Delete Graph] Successfully deleted router instance for {scenario_id}")

    return {
        "status": "success",
    }

@app.get("/pbf_bbox")
async def get_pbf_bbox(prefecture: str):
    pbf_path = f"./preloaded_osm_files/{prefecture}.pbf"
    if not os.path.exists(pbf_path):
        raise HTTPException(status_code=404, detail="PBF file not found")

    try:
        reader = osmium.io.Reader(pbf_path)
        header = reader.header()
        box = header.box()
        print("Box dir:", dir(box))
        print("Box repr:", repr(box))
        reader.close()
        if box is not None:
            bbox = {
                "min_lon": box.bottom_left.x / 1e7,
                "min_lat": box.bottom_left.y / 1e7,
                "max_lon": box.top_right.x / 1e7,
                "max_lat": box.top_right.y / 1e7,
            }
        else:
            bbox = None
        return {
            "status": "success",
            "bbox": bbox
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract bounding box: {e}")