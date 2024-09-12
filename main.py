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
      if not os.path.exists(f"program/{program.NAME}"):
        subprocess.run(["git", "clone", program.GIT_REPO, f"program/{program.NAME}"])
      print(f"Updating program: {program.NAME}...")
      pull_result = subprocess.run(["git", "-C", f"program/{program.NAME}", "pull", "--ff-only"], capture_output=True)

      if not "Already up to date." in str(pull_result.stdout):
        os.system(f"cmake -S program/{program.NAME} -B program/{program.NAME}/bld")
        os.system(f"cmake --build program/{program.NAME}/bld")
    os.system(f"find tmp -type f -mmin +15 -delete")
  second += 1
  Timer(1, update).start()

update()
