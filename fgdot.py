import pydot
import random
import sys
from itertools import chain

def add_implicit_nodes(g, sg_names):
    def f(a):
        if len(g.get_node(a)) == 0 and a not in sg_names:
            g.add_node(pydot.Node(a))
    for e in g.get_edges():
        f(e.get_source())
        f(e.get_destination())
    for sg in g.get_subgraphs():
        add_implicit_nodes(sg, sg_names)

def all_nodes(g):
    for n in g.get_nodes():
        yield n
    for sg in g.get_subgraphs():
        yield from all_nodes(sg)

def all_edges(g):
    for n in g.get_edges():
        yield n
    for sg in g.get_subgraphs():
        yield from all_edges(sg)

def all_subgraphs(g):
    for sg in g.get_subgraphs():
        yield sg
        yield from all_subgraphs(sg)

def node_sg_map(g, d):
    for sg in g.get_subgraphs():
        node_sg_map(sg, d)
        name = sg.get_name()
        d[name] = list(
            chain((n.get_name() for n in sg.get_nodes()),
                chain.from_iterable(
                d[ssg.get_name()] for ssg in sg.get_subgraphs())))
    return d

def style_factors(g):
    for n in all_nodes(g):
        name = n.get_name().split("factor_")
        if name[0] == '':
            n.set_shape("plain")
            n.set_label("■ " + (n.get_label() or name[1]).strip('"'))


def style_connections(g):
    for n in all_nodes(g):
        name = n.get_name().split("con_")
        if name[0] == '':
            n.set_shape("plain")
            n.set_label("□ " + (n.get_label() or name[1]).strip('"'))

def style_subgraphs(g):
    for sg in all_subgraphs(g):
        sg.set_labeljust("l")
        name = sg.get_name()
        if not sg.get_label():
            sg.set_label(name)
        if name.startswith('gate'):
            sg.set_label("")
        sg.set_name("cluster_" + name)

def connect_subgraphs(g, names):
    for e in all_edges(g):
        src, dst = e.get_source(), e.get_destination()
        if src in names and dst not in names:
            true_src = random.sample(names[src], 1)[0]
            g.del_edge(src, dst)
            g.add_edge(pydot.Edge(true_src, dst, ltail="cluster_"+src))
        elif dst in names and src not in names:
            true_dst = random.sample(names[dst], 1)[0]
            g.del_edge(src, dst)
            g.add_edge(pydot.Edge(src, true_dst, lhead="cluster_"+dst, minlen=2))
        elif dst in names and src in names:
            true_src = random.sample(names[src], 1)[0]
            true_dst = random.sample(names[dst], 1)[0]
            g.del_edge(src, dst)
            g.add_edge(pydot.Edge(true_src, true_dst, lhead="cluster_"+dst, ltail="cluster_"+src, minlen=2))

def preprocess(g):
    sg_names = set(sg.get_name() for sg in all_subgraphs(g))
    add_implicit_nodes(g, sg_names)
    g.set_compound(True)
    names = node_sg_map(g, dict())
    style_factors(g)
    style_connections(g)
    style_subgraphs(g)
    connect_subgraphs(g, names)

def to_svg(dot_str):
    g = pydot.graph_from_dot_data(dot_str)[0]
    preprocess(g)
    return g.create_svg()

def to_png(dot_str):
    g = pydot.graph_from_dot_data(dot_str)[0]
    preprocess(g)
    return g.create_png()

if __name__ == "__main__":
    if len(sys.argv) < 1:
        sys.exit("Must pass dot file as argument")
    g = pydot.graph_from_dot_file(sys.argv[1])[0]
    preprocess(g)
    sys.stdout.write(g.to_string())


