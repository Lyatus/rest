from fastapi import APIRouter, Response, status
from fastapi.responses import FileResponse
import subprocess
import os
import uuid

NAME = "steve"
GIT_REPO = "https://github.com/Lyatus/steve"

router = APIRouter(prefix="/steve")

@router.get("/configurations")
def get_configurations():
  return os.listdir("program/steve/cfg")

@router.post("/run")
def post_steve_run(configuration: str, response: Response):
  config_path = f"program/steve/cfg/{configuration}.steve.json"
  if not os.path.exists(config_path):
    response.status_code = status.HTTP_404_NOT_FOUND
    return {}

  output_path = f"tmp/{str(uuid.uuid4())}"
  error = subprocess.call(
    ["program/steve/bld/Debug/steve",
     "--mid",
     "--random",
     f"--out={output_path}",
     f"--config={config_path}"])
  if error != 0:
    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return {}

  output_mid_path = f"{output_path}.mid"
  return FileResponse(path=output_mid_path, media_type="audio/midi", filename=os.path.basename(output_mid_path))
