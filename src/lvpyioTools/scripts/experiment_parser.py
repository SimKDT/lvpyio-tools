r"""
Experiment set parser
---------------------
Shows a children tree hierarchy of the provided set.
"""
from pathlib import Path
from rich import prompt, tree
from rich import print

if __name__ == "__main__":
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from lvpyioTools.set import LVSet
else:
    from ..set import LVSet

def make_tree(lvset:LVSet, parents: list[LVSet], children: list[LVSet]):
    # list parents
    parents_with_self = parents + [lvset]
    print(len(parents_with_self))
    top = tree.Tree(f"[bold]{parents_with_self[0].get_name()}[/bold]")
    current = top
    for parent in parents_with_self[1:]:
        current = current.add(f"[bold]{parent.get_name()}[/bold]")

    # add children
    for i, child in enumerate(children):
        current.add(f"[green]{i}[/green]: {child.get_name()}")

    return top

def recursive_explorer(lv_set: LVSet, parents: list[LVSet] = []):
    children = lv_set.get_children()

    s = sorted(children, key=lambda c: c.get_name().lower())
    print(make_tree(lv_set, parents, s))

    if len(children) == 0:
        return None
    
    choice = prompt.Prompt.ask("Enter your choice", 
                               choices=[str(i) for i in range(len(children))])
    choice = int(choice)
    if 0 <= choice < len(children):
        child = children[choice]
        return recursive_explorer(child, parents + [lv_set])
    return None

def tree_set(lv_set: LVSet, current: tree.Tree | None = None, depth_max: int | None = None, depth: int | None = None):
    if current is None:
        current = tree.Tree(f"[bold]{lv_set.get_name()}[/bold]")
    if depth is None:
        depth = 1

    children = lv_set.get_children()
    for i, child in enumerate(children):
        child_tree = current.add(f"[cyan]{child.get_name()}[/cyan]")
        if depth_max is None or depth < depth_max:
            tree_set(child, child_tree, depth_max=depth_max, depth=depth+1)

    return current


def main():
    import argparse

    doc = __doc__.strip() if __doc__ is not None else "Experiment set parser"
    parser = argparse.ArgumentParser(
        description=doc,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("set", type=Path, help="Path to the DaVis experiment set file")
    parser.add_argument("--depth", type=int, default=None, help="Maximum depth to display in the tree")
    args = parser.parse_args()

    lv_set = LVSet(args.set)
    # recursive_explorer(lv_set)
    print(tree_set(lv_set, depth_max=args.depth))

if __name__ == "__main__":
    main()