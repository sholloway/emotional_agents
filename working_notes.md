# Working notes for this simulations. 

## What are the hierarchy of Systems?
Perhaps there are multiple hierarchies of systems: 
- Physical Systems (Circulatory system, Digestive, Skeletal...)
- Mental Systems (Beliefs, Desires, Mood, Feeling)

### Physical Systems

An agent has groupings of data attributes. 

```python
class AgentLike(Protocol):
  """Behaves like an autonomous agent."""
  agent_state: AgentStateLike        # The internal state of the agent.
  style: AgentStyleLike              # Define's the agent's look.
  identity: AgentIdentityLike        # All of the agent's IDs.
  physicality: AgentPhysicalityLike  # The agent's physical attributes.
  position: AgentPositionLike        # All the attributes related to where the agent is.     
  movement: AgentMovementAttributes  # Attributes used for movement.
```

Can we expand this definition to include subsystems?

```python
from more_itertools import consume
from types import OrderedDict

class AgentSystem(Protocol):
  name: str
  subsystems: OrderedDict[str, AgentSystem]

  def process(self) -> None:
    self.before_subsystems_processed()
    self.process_subsystems()
    self.after_subsystems_processed() 

  def register_system(self, system: AgentSystem) -> Self:
    if system.name not in self.internal_systems:
      self.internal_systems[system.name] = system
    return self 

  def process_subsystems(self) -> None:
    consume(map(lambda subsystem: subsystem.process(), self.subsystems.items())) 

  def before_subsystems_processed(self) -> None:
    pass
  
  def after_subsystems_processed(self) -> None:
    pass

class AgentLike(Protocol):
  internal_systems: OrderedDict[str, AgentSystem]

  def register_system(self, system: AgentSystem) -> Self:
    if system.name not in self.internal_systems:
      self.internal_systems[system.name] = system
    return self

  def process(self) -> None:
    # Loop over the subsystems.
    consume(map(lambda subsystem: subsystem.process(), self.internal_systems.items()))
```

This could be used like...

```python
# Generic (Could be driven by a scene file.)
agent = DefaultAgent()
agent. \
  register_system(ImmuneSystem()). \
  register_system(MuscularSystem())

# Via subclass defined in a project.
class EmotionalAgent(AgentLike):
  def __init__(self) -> None:
    self.register_system(ImmuneSystem())
    self.register_system(MuscularSystem())
```

The use of a dict or OrderedDict to store the systems is giving me heartburn.
I don't like the idea of having to lookup systems with self.internal_systems['some system name']

A SimpleNamespace would enable named attribute lookup. If these are registered 
via TOML, then the SceneBuilder can produce a SimpleNamespace of the registered
systems. 

```python
from more_itertools import consume
from types import SimpleNamespace

class AgentSystem(Protocol):
  name: str
  subsystems: SimpleNamespace

  def register_system(self, system: AgentSystem) -> Self:
    if not hasattr(self.internal_systems, system.name):
      self.internal_systems.__setattr__(system.name, system)
    return self 
```

This will enable implementations to be able to access systems as attributes.

```python
self.internal_systems.muscular_system.refresh()
```

## Feedback Loops
- Mental Systems Drive Behavior (i.e. Next Action)
- Physical Systems influence mental systems. 
  For example if the body suffers damage, then the agent may become afraid.
  If the body is hungry, the agent may feel irritable.
- Physical systems have sensors that propagate sensation.
  Stimuli -> Sensations -> Emotion -> (Moods | Feelings/Beliefs) -> Behavior

## What are the hierarchy of States?


**Tasks**
- [ ] ?