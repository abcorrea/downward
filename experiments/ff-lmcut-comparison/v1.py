#! /usr/bin/env python
# -*- coding: utf-8 -*-

import itertools
import os

from lab.environments import LocalEnvironment, BaselSlurmEnvironment
from lab.reports import Attribute, geometric_mean

from downward.reports.compare import ComparativeReport

import common_setup
from common_setup import IssueConfig, IssueExperiment

from perfect_heuristic import PerfectHeuristic

DIR = os.path.dirname(os.path.abspath(__file__))
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]
REVISIONS = ["ff-lmcut-comparison-v1"]
BUILDS = ["release"]
CONFIG_NICKS = [
    ('ipdb', ['--search', 'astar(ipdb(max_time=1200))']),
    ('lmcut', ['--search', 'astar(lmcut)']),
    ('ff', ['--search', 'astar(ff)']),
    ('hmax', ['--search', 'astar(hmax)']),
    ('add', ['--search', 'astar(add)']),
]

CONFIGS = [
    IssueConfig(
        config_nick,
        config
    for config_nick, config in CONFIG_NICKS
]

SUITE = common_setup.DEFAULT_OPTIMAL_SUITE
ENVIRONMENT = BaselSlurmEnvironment(
    partition="infai_2",
    export=["PATH", "DOWNWARD_BENCHMARKS"])

if common_setup.is_test_run():
    SUITE = IssueExperiment.DEFAULT_TEST_SUITE
    ENVIRONMENT = LocalEnvironment(processes=4)

exp = IssueExperiment(
    revisions=REVISIONS,
    configs=CONFIGS,
    environment=ENVIRONMENT,
)
exp.add_suite(BENCHMARKS_DIR, SUITE)

exp.add_parser(exp.EXITCODE_PARSER)
exp.add_parser(exp.TRANSLATOR_PARSER)
exp.add_parser(exp.SINGLE_SEARCH_PARSER)
exp.add_parser(exp.PLANNER_PARSER)

exp.add_step('build', exp.build)
exp.add_step('start', exp.start_runs)
exp.add_fetcher(name='fetch')



ATTRIBUTES = [
    "coverage",
    "initial_h_value",
    "cost",
    "diff_h_star"
]
#attributes = exp.DEFAULT_TABLE_ATTRIBUTES
#attributes.extend(extra_attributes)

obj = PerfectHeuristic()
exp.add_absolute_report_step(attributes=ATTRIBUTES, filter=[obj.store_costs, obj.add_diff_h_star])

exp.run_steps()
