from collections import defaultdict

class PerfectHeuristic(object):
    """Compute the perfect heuristic from iPDB runs.

    """

    def __init__(self):
        self.tasks_to_costs = defaultdict(lambda:None)

    def _get_task(self, run):
        return (run["domain"], run["problem"])

    def _compute_difference(self, cost, h_star):
        if cost is None or h_star is None:
            return None
        return abs(h_star - cost)

    def store_costs(self, run):
        if 'ipdb' in run["algorithm"]:
            cost = run.get("cost")
            if cost is not None:
                assert run["coverage"]
                self.tasks_to_costs[self._get_task(run)] = cost
        return True

    def add_diff_h_star(self, run):
        run["diff_h_star"] = self._compute_difference(
            run.get("initial_h_value"), self.tasks_to_costs[self._get_task(run)]
        )
        return run
