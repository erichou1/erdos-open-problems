import unittest

from research_state import graph_as_dict, make_statement_lock, parse_subgoal_graph


class ResearchStateTests(unittest.TestCase):
    def test_statement_lock_is_stable_and_exact(self):
        first = make_statement_lock("  For all n, P(n).  ")
        second = make_statement_lock("For all n, P(n).")
        self.assertEqual(first, second)
        self.assertEqual(first.original_statement, "For all n, P(n).")

    def test_rejects_cyclic_subgoal_graph(self):
        graph = {"subgoals": [
            {"id": "A", "claim": "A", "dependencies": ["B"], "centrality": 1},
            {"id": "B", "claim": "B", "dependencies": ["A"], "centrality": 1},
        ]}
        with self.assertRaisesRegex(ValueError, "cycle"):
            parse_subgoal_graph(graph)

    def test_rejects_unknown_dependencies(self):
        graph = {"subgoals": [
            {"id": "A", "claim": "A", "dependencies": ["MISSING"], "centrality": 1},
        ]}
        with self.assertRaisesRegex(ValueError, "unknown dependencies"):
            parse_subgoal_graph(graph)

    def test_rejects_missing_goal_or_unknown_bottleneck(self):
        missing_goal = {"subgoals": [
            {"id": "A", "claim": "A", "dependencies": [], "centrality": 1},
        ]}
        nodes = parse_subgoal_graph(missing_goal)
        with self.assertRaisesRegex(ValueError, "GOAL"):
            graph_as_dict(missing_goal, nodes)

        bad_bottleneck = {"bottleneck_ids": ["MISSING"], "subgoals": [
            {"id": "GOAL", "claim": "goal", "dependencies": [], "centrality": 5},
        ]}
        nodes = parse_subgoal_graph(bad_bottleneck)
        with self.assertRaisesRegex(ValueError, "unknown bottlenecks"):
            graph_as_dict(bad_bottleneck, nodes)


if __name__ == "__main__":
    unittest.main()
