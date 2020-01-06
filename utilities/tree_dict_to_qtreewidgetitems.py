from PyQt5.QtWidgets import QTreeWidgetItem
from tree_dict import tree_structure

# example tree_structure:
#
# tree_structure = {
#     "a": {},
#     "b": {
#         "b-a": {
#             "b-a-a": {},
#             "b-a-b": {},
#         },
#         "b-b": {}
#     },
#     "c": {},
# }
#
# example output structure:
#
# [a]
# [b]
# - [b-a]
# -- [b-a-a]
# -- [b-a-b]
# - [b-b]
# [c]
#
# the function expand_tree_macro() returns
# only top level items like [a],[b],[c] in
# the example.
#


def dict_to_tree(name: str, tree_dict: dict):
    item = QTreeWidgetItem()
    item.setText(0, name)
    for i in tree_dict:
        item.addChild(dict_to_tree(i, tree_dict[i]))
    return item


def expand_tree_dict(tree=tree_structure):
    top_level = []
    for i in tree:
        top_level.append(dict_to_tree(i, tree[i]))
    return top_level


if __name__ == '__main__':
    expand_tree_macro(tree_structure)