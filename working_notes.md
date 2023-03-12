# Working notes for this simulations. Note, this is not committed.

The engine defines an Agent as:
```python
class Agent:
  """A generic, autonomous agent."""
  _state: AgentState              # The initial configuration for the various state fields.
  _style: AgentStyle              # Define's the agent's look.
  _identity: AgentIdentity        # All of the agent's IDs.
  _physicality: AgentPhysicality  # The agent's physical attributes.
  _position: AgentPosition        # All the attributes related to where the agent is.
  _movement: AgentMovement        # Attributes used for movement.  
```

It can... 

```python
class Agent:
  def transition_state(self) -> None:
    self._state.transition_to_next_action()

  def select(self) -> None:
    self._state.selected = True

  def deselect(self) -> None:
    self._state.selected = False

  def reset(self) -> None:
    self._state.reset()

  def face(self, direction: Vector2d) -> None:
    """Set the direction the agent is facing."""
    self._position.facing = direction
    self._state.require_scene_graph_update = True

  def move_to(self, new_location: Coordinate, cell_size: Size):
    """Tell the agent to walk to the new location in the maze."""
    self._position.move_to(new_location)
    self._state.require_scene_graph_update= True
    self._physicality.calculate_aabb(self._position.location, cell_size)
```

It has the public properties...
``` python
class Agent:
  @property
  def style(self) -> AgentStyle:
    return self._style

  @property
  def state(self) -> AgentState:
    return self._state

  @property
  def identity(self) -> AgentIdentity:
    return self._identity

  @property
  def physicality(self) -> AgentPhysicality:
    return self._physicality
  
  @property
  def position(self) -> AgentPosition:
    return self._position
  
  @property
  def movement(self) -> AgentMovement:
    return self._movement

  @property
  def agent_scene_graph_changed(self) -> bool:
    return self._state.require_scene_graph_update

  @property
  def agent_render_changed(self) -> bool:
    return self._state.require_render

  @property 
  def selected(self) -> Boolean:
    return self._state.selected
```

The main hook is the _Agent.transition_state()_ method. It call's the internal
instance of AgentState's _transition_to_next_action_ method.

The AgentState class is responsible for everything internal to the agent.
What they're thinking, how they're feeling, etc... This is probably the proper 
place to extend the agent model.

Currently the AgentState class leverages an ActionSelector to pick what the agent
should do next. The default is to use a lookup table of states. It determines
the next action by using an AgentStateMap which is a constant. 


``` python
@dataclass
class ActionSelector:
  model: Dict[AgentActionState, AgentActionState]

  # TODO: Eventually, this will be probabilistic.
  def next_action(self, current_action: AgentActionState) -> AgentActionState:
    """Find the mapped next action."""
    return self.model[current_action]

AgentStateMap = {
  AgentActionState.IDLE: AgentActionState.IDLE,
  AgentActionState.RESTING: AgentActionState.PLANNING,
  AgentActionState.PLANNING: AgentActionState.ROUTING,
  AgentActionState.ROUTING: AgentActionState.TRAVELING,
  AgentActionState.TRAVELING: AgentActionState.RESTING
}
```

A thought is to expand the _SceneBuilder_ class to allow associating an agent
with a project specific ActionSelector. 

```toml
agents = [
  { id = 1, crest='green', location=[10,10], action_selector='my_action_selector'}
]
```

Really, if we go that route, all of the core agent aspects should be override-able.

```toml
[[agents]]
  id = 1
  action_selector     = 'my_action_selector'
  state_builder       = 'my_agent_state_builder'
  style_builder       = 'my_agent_style_builder'
  physicality_builder = 'my_agent_physicality_builder'
  position_builder    = 'my_agent_position_builder'
  movement_builder    = 'my_agent_movement_builder'
```

Working through the concept of agent aspects...
Currently using data classes for the various aspects and Agent explicitly declares
an instance of each aspect. A thought is to make Agent just a generic container 
of aspects.

```python
class AgentAspect(ABC):
  pass

class AgentState(AgentAspect):
  pass

class AgentStyle(AgentAspect):
  pass

class AgentIdentity(AgentAspect):
  pass

class AgentPhysicality(AgentAspect):
  pass

class AgentPosition(AgentAspect):
  pass

class AgentMovement(AgentAspect):
  pass

class Agent:
  """One thought is to make Agent just a container of aspects."""
  aspects: dict[str, AgentAspect]
  def add_aspect(label:str, aspect: AgentAspect) -> Self:
    self.aspects['label'] = aspect
    return self
```

What does this look like using protocols rather than abstract classes?
Protocols enable defining structural definitions that don't require inheritance.


```python
from typing import Protocol
from abc import abstractmethod

class SupportsClose(Protocol):
  @abstractmethod
  def close(self) -> None:
    pass

class SupportsReset(Protocol):
  @abstractmethod
  def reset(self) -> None:
    pass

class CoreStateBehavior(Protocol):
  pass

class AgentState(SupportsClose, SupportsReset, CoreStateBehavior):
  def close(self) -> None:
    ...

  def reset(self) -> None:
    ...
```

**Tasks**
- [ ] Define abstract classes for the injectable aspects of agents.
- [ ] Provide a defaults for the various agent aspects (e.g. AgentState)
- [ ] Move AgentStateMap and AgentActionState into the a_star_navigation demo.
- [ ] Have the emotional_agents project define its own agent aspects.
- [ ] AgentActionState needs to not be an enum. You can't extend an enumeration 
      class with inheritance. 
- [ ] Add a new registration decorator: _register_agent_next_action_handler_
