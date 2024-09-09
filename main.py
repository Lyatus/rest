from fastapi import FastAPI
from contextlib import asynccontextmanager
from threading import Timer
import steve
import os
import uvicorn

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

os.makedirs("tmp", exist_ok=True)

second = 0
def update():
  global shutting_down
  global second
  if shutting_down:
    return

  if (second % 60) == 0:
    os.system(f"git pull --ff-only")
    for program in programs:
      os.system(f"git clone {program.GIT_REPO} program/{program.NAME}")
      os.system(f"git -C program/{program.NAME} pull")
      os.system(f"cmake -S program/{program.NAME} -B program/{program.NAME}/bld")
      os.system(f"cmake --build program/{program.NAME}/bld")
    os.system(f"find tmp -type f -mmin +15 -delete")
  second += 1
  Timer(1, update).start()

update()

if __name__ == "__main__":
  uvicorn.run("main:app", port=5000, log_level="info", reload=True)
