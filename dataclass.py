from pydantic import BaseModel, Field

class CogRequest(BaseModel):
    method: str = Field(description='Either load, unload or reload.')
    file: str = Field(description='cog module to operate for this request.')

class item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None