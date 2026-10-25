from fastapi import HTTPException

from schemas import TaskCreate,TaskResponse,TaskUpdate


# Temporary storage: data disappears when process restarts
tasks : dict[int,TaskResponse] = {}
nextId = 1

def create(payload: TaskCreate) -> TaskResponse : 
    global nextId 
    # make resp model n assign id
    task = TaskResponse(id=nextId,**payload.model_dump())

    tasks[nextId] = task
    nextId += 1
    return task

def listTask(
        completed: bool | None=None,
        skip: int = 0,
        limit: int=20,
)-> list[TaskResponse]:
    #filter n paginate
    result = list(tasks.values())

    if completed is not None:
        result = [task for task in result if task.completed == completed]


    return result[skip: skip+limit] # for now slicing list

def get(taskId:int) -> TaskResponse:

    task = tasks.get(taskId)

    if task is None:
        raise HTTPException(status_code=404,detail="Task not found")

    return task

def update(taskId:int,payload:TaskUpdate)->TaskResponse:
    task = tasks.get(taskId)

    if task is None:
        raise HTTPException(status_code=404,detail="Task not found")

    #include files only client supplied
    #create a replacement rather than mutating existing object
    upTask = payload.model_dump(exclude_unset=True)
    updated = task.model_copy(update=upTask)
    tasks[taskId] = updated

    return updated

def delete(taskId:int) -> None:
    get(taskId) #auto check if present,then
    del tasks[taskId]


def reset_tasks() -> None:
    """Reset in-memory storage for isolated tests."""
    global nextId
    tasks.clear()
    nextId = 1