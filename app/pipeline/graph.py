"""LangGraph StateGraph: four nodes in order and one conditional edge for the Critic loop."""
from langgraph.graph import StateGraph

from app.agents.critic import Critic
from app.agents.outliner import Outliner
from app.agents.researcher import Researcher
from app.agents.writer import Writer
from app.core.constants import PIPELINE
from app.pipeline.routing import route_after_critic
from app.pipeline.state import State

AGENTS = {a.name: a for a in (Researcher(), Outliner(), Writer(), Critic())}

g = StateGraph(State)
for name in PIPELINE:
    g.add_node(name, AGENTS[name].run)
g.set_entry_point(PIPELINE[0])
for a, b in zip(PIPELINE, PIPELINE[1:]):
    g.add_edge(a, b)
g.add_conditional_edges(PIPELINE[-1], route_after_critic)
graph = g.compile()
