from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from threading import Timer
import os
import steve
import subprocess
import uvicorn

if __name__ == "__main__":
  uvicorn.run("main:app", reload=True)
  exit(0)

programs = [steve]

shutting_down = False

@asynccontextmanager
async def lifespan(app: FastAPI):
  global shutting_down
  yield
  shutting_down = True

app = FastAPI(lifespan=lifespan)
for program in programs:
  app.include_router(program.router)

allow_origins = ["https://lutopia.net"]
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

second = 0
def update():
  global shutting_down
  global second
  if shutting_down:
    return

  if (second % 60) == 0:
    print("Updating server...")
    subprocess.run(["git", "pull", "--ff-only"])
    for program in programs:
      program_dir = f"program/{program.NAME}"
      if not os.path.exists(program_dir):
        subprocess.run(["git", "clone", program.GIT_REPO, program_dir])
      print(f"Updating program: {program.NAME}...")
      subprocess.run(["git", "-C", program_dir, "pull", "--ff-only"])

      project_dir = program_dir
      if hasattr(program, 'PROJECT_DIR'):
        project_dir = os.path.join(project_dir, program.PROJECT_DIR)
      build_dir = os.path.join(project_dir, 'bld')

      subprocess.run(["cmake", "-S", project_dir, "-B", build_dir, "-DCMAKE_BUILD_TYPE=Release"])
      subprocess.run(["cmake", "--build", build_dir, "--config", "Release"])
    os.system(f"find tmp -type f -mmin +15 -delete")
  second += 1
  Timer(1, update).start()

update()
