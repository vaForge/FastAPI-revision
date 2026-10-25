from fastapi import APIRouter, Query, Response, status

from schemas import TaskResponse,TaskUpdate,TaskCreate

#all endpoints in this router share /tasks prefix
import service
router = APIRouter(prefix="/tasks",tags=["Tasks"])

@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def createTask(payload: TaskCreate):
    return service.create(payload)

@router.get("",response_model=list[TaskResponse])
def listTask(
        completed:bool |None = None,
        skip:int = Query(default=0,ge=0),
        limit:int = Query(default=20,ge=1,le=100),
):
    return service.listTask(
        completed=completed,
        skip=skip,
        limit=limit
    )

@router.get("/{task_id}", response_model=TaskResponse)
def getTask(task_id: int):
    return service.get(task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
def updateTask(task_id: int, payload: TaskUpdate):
    return service.update(task_id, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def deleteTask(task_id: int):
    service.delete(task_id)

    # HTTP 204 means success with no response body.
    return Response(status_code=status.HTTP_204_NO_CONTENT)
