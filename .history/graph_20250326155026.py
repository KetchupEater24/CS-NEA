# BST means Binary Search Tree
# ef is easiness factor (determined by spaced repitition algorithm)
class DeckNode:
    # initialises each deck as a node with deck id, deck name, avg ef, card count, left pointer and right pointer
    def __init__(self, deck_id, deck_name, avg_ef, card_count, user_id):
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.avg_ef = avg_ef  
        self.card_count = card_count
        self.user_id = None
        self.left = None
        self.right = None

# inserts a node into the BST based on avg ef (lower avg ef goes to left, else equal or higher avg ef goes to right)
def insert_node(root, node):
    if root is None:
        return node
    if node.avg_ef < root.avg_ef:
        root.left = insert_node(root.left, node)
    else:
        root.right = insert_node(root.right, node)
    return root

# performs in order traversal of the BST, returning decks sorted by avg_ef (lowest first, e.g higher deck priority) 
def in_order(root):
    nodes = []
    if root:
        nodes.extend(in_order(root.left))
        nodes.append(root)
        nodes.extend(in_order(root.right))
    return nodes
