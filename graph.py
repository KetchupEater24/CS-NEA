# # node class for decks in the graph
# class DeckNode:
#     def __init__(self, deck_id, deck_name, wrong_count):
#         self.deck_id = deck_id
#         self.deck_name = deck_name
#         self.wrong_count = wrong_count
#         self.children = []

# # build a simple graph from a sorted list of deck tuples
# def build_deck_graph(deck_list):
#     # deck_list is assumed to be sorted descending by wrong_count
#     if not deck_list:
#         return None
#     # use the first deck as root
#     root = DeckNode(deck_list[0][0], deck_list[0][1], deck_list[0][2])
#     # attach all other decks as children of the root
#     for deck in deck_list[1:]:
#         node = DeckNode(deck[0], deck[1], deck[2])
#         root.children.append(node)
#     return root

# # perform BFS on the deck graph and return nodes in order
# def bfs_deck_graph(root):
#     if root is None:
#         return []
#     queue = [root]
#     order = []
#     while queue:
#         node = queue.pop(0)
#         order.append(node)
#         # since all children were added in sorted order, extending the queue here preserves that order
#         queue.extend(node.children)
#     return order

# node class for decks in the graph

class DeckNode:
    def __init__(self, deck_id, deck_name, difference):
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.difference = difference
        self.children = []

# build a simple graph from a sorted list of deck tuples
def build_deck_graph(deck_list):
    # deck_list is assumed to be sorted ascending by difference (lowest difference = highest priority)
    if not deck_list:
        return None
    # use the first deck as root
    root = DeckNode(deck_list[0][0], deck_list[0][1], deck_list[0][2])
    # attach all other decks as children of the root
    for deck in deck_list[1:]:
        node = DeckNode(deck[0], deck[1], deck[2])
        root.children.append(node)
    return root

# perform BFS on the deck graph and return nodes in order
def bfs_deck_graph(root):
    if root is None:
        return []
    queue = [root]
    order = []
    while queue:
        node = queue.pop(0)
        order.append(node)
        queue.extend(node.children)
    return order


