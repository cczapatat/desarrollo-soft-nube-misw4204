from models.task import Task
from models.declarative_base import engine, Base

print("[DB-Init] Running...")
print("Task:: {}".format(Task.__table__))
Base.metadata.create_all(engine)
print("[DB-Init] Finished")

