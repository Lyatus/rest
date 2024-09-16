from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from threading import Timer
import os
import steve
import robin
import subprocess
import uvicorn

if __name__ == "__main__":
  uvicorn.run("main:app", reload=True)
  exit(0)

programs = [steve, robin]

update_timer = None
@asynccontextmanager
async def lifespan(app: FastAPI):
  yield
  update_timer.cancel()

app = FastAPI(lifespan=lifespan)
for program in programs:
  app.include_router(program.router)

allow_origins = [
  "https://lutopia.net",
  "https://radio.lutopia.net"
]
if os.getenv("DEBUG"):
  print("Running in debug mode")
  allow_origins.append("*")

app.add_middleware(
  CORSMiddleware,
  allow_origins=allow_origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

os.makedirs("tmp", exist_ok=True)
app.mount("/tmp", StaticFiles(directory="tmp"), name="tmp")

def update(iteration = 0):
  global update_timer
  if (iteration % 60) == 0:
    print("Updating server...")
    subprocess.run(["git", "pull", "--ff-only"])
    for program in programs:
      program_dir = f"program/{program.NAME}"
      if not os.path.exists(program_dir):
        subprocess.run(["git", "clone", program.GIT_REPO, program_dir])
      print(f"Updating program: {program.NAME}...")
      pull_result = subprocess.run(["git", "-C", program_dir, "pull", "--ff-only"], capture_output=True)

      project_dir = program_dir
      if hasattr(program, 'PROJECT_DIR'):
        project_dir = os.path.join(project_dir, program.PROJECT_DIR)
      build_dir = os.path.join(project_dir, 'bld')

      if iteration == 0 or not "Already up to date." in str(pull_result.stdout):
        subprocess.run(["cmake", "-S", project_dir, "-B", build_dir, "-DCMAKE_BUILD_TYPE=Release"])
        subprocess.run(["cmake", "--build", build_dir, "--config", "Release"])
    os.system(f"find tmp -type f -mmin +15 -delete")
  update_timer = Timer(1, update, [iteration + 1])
  update_timer.start()

update()
