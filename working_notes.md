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
      self.subsystems.__setattr__(system.name, system)
    return self 
```

This will enable implementations to be able to access systems as attributes.

```python
self.internal_systems.muscular_system.refresh()
```

## TOML Based State Map
If state-type isn't specified the scene builder could use NamedAgentState(name).
```toml
# Declare states
scene.agent-states = [
  { name = '', state-type=''}
]

# Define the state map.
# state (required): The name of the starting state. 
# transitions-to (required): The name of the state to transition to.
#
# when (optional): 
# The name of a conditional function to determine if the transition
# should occur. 
#
# likelihood (optional): 
# Supports probability based state rules. A value between 0 and 1. Where 
# 1 means it has 100% probability of the transition occurring and 0 means
# there is no chance. 
# 
# If both 'when' and 'likelihood' are present, the 'when' condition is ran first.
# if it evaluates to True, then the likelihood function is ran. If both are true
# then the transition occurs.                          
#
# Being able to define this in a table in the GUI would be helpful.
# Having a way to visualize this would also be helpful.
scene.agent-state-transitions = [
  { state = '<state-name>', transitions-to = '<state-name>', when='<condition>', likelihood='<>'}
]
```

# What is the underlying data structure to support a complex, conditional-based
# transition table with optional fuzzy rules?

Considerations
- A starting state can have multiple rules... Assuming rules need to be run
  in the order they are declared.
- Rules are executed based on optional condition functions.
- Rules are executed based on probabilities. 

May need a tree style data structure rather than just a dict.

```python
from random import choices
from more_itertools import first_true

class Likelihood:
  coin: str = (1,0) # heads or tails.
  def __init__(self, weight: float) -> None:
    self.weight = weight

  def coin_flip(self) -> bool:
    """
    Flip a weighted coin based on the likelihood value, calculate whether to do an action or not.
    Returns True when heads is flipped.
    """
    return choices(Likelihood.coin, cum_weights=(self.weight, 1.00), k = 1)[0] == 1

class AgentStateTransitionRule(NamedTuple):
  state_name: str
  transition_to: str
  condition: Callable[AgentLike, bool] # Give this a function that always returns true rather than make it optional.
  likelihood: Likelihood


class AgentActionStateRulesSet:
  rules: List[AgentStateTransitionRule]

  def evaluate(self, agent: AgentLike) -> AgentActionStateLike:
    first_true(
      self.rules, 
      default = self._handle_no_state_transition,
      pred = lambda rule: rule.condition(agent))

class FancyPantsAgentActionSelector(AgentActionSelector):
  def __init__(self) -> None:
    self._state_map: dict[AgentActionStateLike, AgentActionStateRulesSet]

  def next_action(self, agent: AgentLike, current_action: AgentActionStateLike) -> AgentActionStateLike:
    return self._state_map.get(current_action, NoAgentActionStateRulesSet()).evaluate(agent)
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