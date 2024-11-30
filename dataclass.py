from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    ValidationInfo,
    field_validator,
)

class CogRequest(BaseModel):
    method: str = Field(description='Either load, unload or reload.')
    file: str = Field(description='cog module to operate for this request.')

class actionRequest(BaseModel):
    action: str = Field(description='The action to perform on the bot.')

    @field_validator('action')
    @classmethod
    def validate_action(cls, act: str):
        valid_actions = {'restart', 'login', 'logout'}
        if act not in valid_actions:
            raise ValueError(f"Invalid action: {act}. Valid actions are: {', '.join(valid_actions)}")
        return act

class item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None