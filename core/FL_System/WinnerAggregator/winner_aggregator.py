class DFLProcess:
    def __init__(self, nodes, winner_node):
        self.nodes = nodes
        self.winner_node = winner_node

    def winner_becomes_aggregator(self):
        for node in self.nodes:
            if node['node_id'] == self.winner_node:
                node['is_aggregator'] = True
                return f"Winner node (Node {node['node_id']}) became the aggregator."
        return "The winner node was not found in the list of nodes."

# Define a list of nodes with their properties
nodes = [
    {'node_id': 1, 'is_aggregator': False},
    {'node_id': 2, 'is_aggregator': False},
    {'node_id': 3, 'is_aggregator': False}
]

# Specify the winner node
winner_node = 1  # Change this to the ID of the winner node

# Create a DFLProcess instance
dfl_process = DFLProcess(nodes, winner_node)

# Call the method to make the winner the aggregator
result = dfl_process.winner_becomes_aggregator()
print(result)

# Print the updated list of nodes
for node in nodes:
    print(f"Node {node['node_id']} is{' an' if node['is_aggregator'] else ' not an'} aggregator.")
