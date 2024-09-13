from fastapi import APIRouter, HTTPException
import subprocess
import os

NAME = "robin"
GIT_REPO = "https://github.com/Lyatus/robin"
PROJECT_DIR = "cli"

router = APIRouter(prefix="/robin")

@router.post("/render")
async def render(filename : str):
  mid_path = f"tmp/{filename}"
  if not os.path.exists(mid_path):
    raise HTTPException(status_code=404, detail=f"File '{filename}' not found")

  robin_exe = "program/robin/cli/bld/Release/rbncli.exe"
  if not os.path.exists(robin_exe):
    robin_exe = "program/robin/cli/bld/rbncli"

  error = subprocess.call([robin_exe, "render", mid_path])
  if error != 0:
    raise HTTPException(status_code=500, detail=f"Robin process returned {error}")

  wav_path = os.path.splitext(mid_path)[0] + '.wav'
  return [wav_path]
