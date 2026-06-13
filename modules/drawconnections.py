import networkx as nx
import matplotlib.pyplot as plt

corro = [
 ['60','185','5','5','Air/Waste','Reactant: water','Reactant: Phenol1','Reactant: Iminodiacetic acid sol.','Apparatus: Reactor1 IN','Syringe','2 servos, 4 exits','2'],
 ['10','118','10','10','Air/Waste','Apparatus: Reactor1 IN','Reactant: NaOH sol.','Not in use','Not in use','Syringe','2 servos, 4 exits','2'],
 ['60','185','5','5','Air/Waste','Reactant: water','Apparatus: Reactor1 OUT','Not in use','Not in use','Syringe','2 servos, 4 exits','2'],
 ['10','118','0','0','Air/Waste','Not in use','Not in use','Not in use','Not in use','Syringe','2 servos, 4 exits','2'],
 ['60','185','0','0','Air/Waste','Not in use','Not in use','Not in use','Not in use','Syringe','2 servos, 4 exits','2'],
 ['50','120','0','0','Reactant: water','Apparatus: Reactor1 OUT','Not in use','Not in use','Not in use','Peristaltic','2 ports','1'],
 ['10','118','0','0','Air/Waste','Not in use','Not in use','Not in use','Not in use','Syringe','2 servos, 4 exits','2']
]

# === Graph building ===
G = nx.DiGraph()
pos = {}

dx = 3
y_actuator = 2
y_valve = 1
y_target = 0

targets_seen = {}

def classify_target(name):
    if name.startswith("Reactant"):
        return "reagent"
    if name.startswith("Apparatus"):
        return "apparatus"
    if name == "Air/Waste":
        return "air"
    return "other"

all_targets = []

for i, s in enumerate(corro):
    x = i * dx

    actuator_type = s[9]  # Syringe or Peristaltic
    actuator_name = f"{actuator_type}_{i+1}"

    # Nodo attuatore
    G.add_node(actuator_name, type=actuator_type.lower())
    pos[actuator_name] = (x, y_actuator)

    if actuator_type == "Syringe":
        # Valve under syringe
        valve_name = f"Valve_{i+1}"
        G.add_node(valve_name, type="valve")
        pos[valve_name] = (x, y_valve)
        G.add_edge(actuator_name, valve_name)

        ports = s[4:9]  # 5 ports

        for port in ports:
            if port == "Not in use":
                continue
            if port not in targets_seen:
                targets_seen[port] = classify_target(port)
                all_targets.append(port)
            G.add_edge(valve_name, port)

    elif actuator_type == "Peristaltic":
        # Peristaltic: only IN and OUT
        ports = s[4:6]  # only 2 ports

        for port in ports:
            if port == "Not in use":
                continue
            if port not in targets_seen:
                targets_seen[port] = classify_target(port)
                all_targets.append(port)
            G.add_edge(actuator_name, port)

# Sort targets: reagents → apparatus → air → other
all_targets_sorted = sorted(
    all_targets,
    key=lambda t: {"reagent": 0, "apparatus": 1, "air": 2, "other": 3}[targets_seen[t]]
)

# Targets positioning
for idx, target in enumerate(all_targets_sorted):
    tx = idx * 2
    pos[target] = (tx, y_target)
    G.add_node(target, type=targets_seen[target])

# === Drawing ===
plt.figure(figsize=(20, 8))

color_map = {
    "syringe": "lightblue",
    "peristaltic": "yellow",
    "valve": "orange",
    "reagent": "lightgreen",
    "apparatus": "violet",
    "air": "gray",
    "other": "white"
}

node_colors = []
labels = {}

for n, data in G.nodes(data=True):
    node_type = data["type"]
    node_colors.append(color_map[node_type])
    labels[n] = n

nx.draw(
    G, pos,
    with_labels=True,
    labels=labels,
    node_color=node_colors,
    node_size=2000,
    font_size=8,
    arrows=False
)

plt.title("CORRO Robot – Connection graph")
plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.05)
plt.show()
