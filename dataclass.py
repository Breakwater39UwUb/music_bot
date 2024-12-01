from typing import Literal, ClassVar
import enum
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

class ChannelProfile(BaseModel):
    name: str
    id: int

class FeaturedChannels(BaseModel):
    spend_share: ChannelProfile
    music_share: ChannelProfile
    bot_command: ChannelProfile
    welcome: ChannelProfile

class GuildProfile(BaseModel):
    name: str
    id: int
    featured_channel: FeaturedChannels | dict
    action: str = Field(default='none', description='action for guild profile modification')

    @field_validator('action')
    @classmethod
    def validate_action(cls, act: str):
        valid_actions = {'none', 'change'}
        act = act.lower()
        if act not in valid_actions:
            raise ValueError(f"Invalid Guild Profile action: {act}. Valid actions are: {', '.join(valid_actions)}")
        return act

class BotFeatures(BaseModel):
    spend_share: str = 'spend_share'
    music: str = 'music'
    bot_command: str = 'bot_command'
    welcome: str = 'welcome'
    # features: dict = {'spend_share': spend_share,
    #                   'music': music,
    #                   'bot_command': bot_command,
    #                   'welcome': welcome}
    # feature_list: list[str] = Field(description='List of bot features.')

class Features(enum.Enum):
    '''Enumerate for different Bot feature.
    If new feature is added, need to add new attribute manually.
    '''
    spend_share = 'spend_share'
    music = 'music'
    bot_command = 'bot_command'
    welcome = 'welcome'

class CogModules(enum.Enum):
    """
    Enumerate for different Cog modules.
    If new module is added, need to add new attribute manually.
    """
    # TODO: Fix moved data class in cog_manager.py
    __cogDir__ = 'cogs.'
    all = __cogDir__ + '*'
    main = __cogDir__ + 'main'
    event = __cogDir__ + 'event'
    bot_manager = __cogDir__ + 'bot_manager'
    music = __cogDir__ + 'music'
    spend_share = __cogDir__ + 'spend_share'

class item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None