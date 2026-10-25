from pydantic import BaseModel, Field, model_validator

class TaskCreate(BaseModel):
    """ Fields req or accept when creating a taskk"""

    title: str = Field(min_length=1,max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool = False

class TaskUpdate(BaseModel):
    """Fields that may be changed by PATCH"""
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool | None = None

    @model_validator(mode="after")
    def validate_patch(self):
        # reject empty patch rea
        if not self.model_fields_set:
            raise ValueError("Provide at least 1 filed to update")

        #supplied title or flag can't be null
        if "title" in self.model_fields_set and self.title is None:
            raise ValueError("Title can't null bruh")

        if "completed" in self.model_fields_set and self.completed is None:
            raise ValueError("Completed can't be null bruh")

        return self

class TaskResponse(BaseModel):
    """Representation to reutrn to client api"""

    id : int
    title: str
    description : str | None
    completed : bool