from fastapi import APIRouter, HTTPException
import subprocess
import os
import uuid

NAME = "steve"
GIT_REPO = "https://github.com/Lyatus/steve"

router = APIRouter(prefix="/steve")

@router.get("/configurations")
def get_configurations():
  return list(map(lambda c: c.removesuffix('.steve.json'), os.listdir("program/steve/cfg")))

@router.post("/run")
def post_steve_run(configuration: str):
  config_path = f"program/steve/cfg/{configuration}.steve.json"
  if not os.path.exists(config_path):
    raise HTTPException(status_code=404, detail=f"Configuration '{configuration}' not found")

  # Ugly but I can't be bothered to use CMake correctly
  steve_exe = "program/steve/bld/Release/steve.exe"
  if not os.path.exists(steve_exe):
    steve_exe = "program/steve/bld/steve"

  output_path = f"tmp/{str(uuid.uuid4())}"
  error = subprocess.call(
    [steve_exe,
     "-mt",
     "--random",
     f"--out={output_path}",
     f"--config={config_path}"])
  if error != 0:
    raise HTTPException(status_code=500, detail=f"Steve process returned {error}")

  return [f"{output_path}.mid",f"{output_path}.txt"]
