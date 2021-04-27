#! /usr/bin/env python
# -*- coding: utf-8 -*-

import common_setup

from common_setup import IssueConfig, IssueExperiment

import os

from lab.reports import Attribute

from lab.environments import LocalEnvironment, BaselSlurmEnvironment

from downward import suites

from downward.reports.absolute import AbsoluteReport

REVISIONS = ["main"]

CONFIGS = [
        IssueConfig("translate", [],
                driver_options=[]),
]

BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]
REPO = os.environ["DOWNWARD_REPO"]

if common_setup.is_running_on_cluster():
    SUITE = ["organic-synthesis-opt18-strips",
             "organic-synthesis-sat18-strips"]
    ENVIRONMENT = BaselSlurmEnvironment(
        partition="infai_2",
        export=["PATH", "DOWNWARD_BENCHMARKS"],
    )
else:
    SUITE = ["organic-synthesis-opt18-strips:p01.pddl",
             "organic-synthesis-opt18-strips:p10.pddl"]
    ENVIRONMENT = LocalEnvironment(processes=2)

exp = common_setup.IssueExperiment(
    revisions=REVISIONS,
    configs=CONFIGS,
    environment=ENVIRONMENT,
)

TIME_LIMIT=1800
MEMORY_LIMIT=8192


for task in suites.build_suite(BENCHMARKS_DIR, SUITE):
    run = exp.add_run()
    run.add_resource('domain', task.domain_file, symlink=True)
    run.add_resource('problem', task.problem_file, symlink=True)
    run.add_command(
        'run-translator',
        ["strace", REPO+'/builds/release/bin/translate/translate.py',
         task.domain_file, task.problem_file],
        time_limit=TIME_LIMIT,
        memory_limit=MEMORY_LIMIT)
    run.set_property('domain', task.domain)
    run.set_property('problem', task.problem)
    run.set_property('algorithm', 'translator')
    run.set_property('revision', "main")
    run.set_property('id', [task.domain, task.problem])


#exp.add_suite(BENCHMARKS_DIR, SUITE)

exp.add_parser(exp.TRANSLATOR_PARSER)
ATTRIBUTES = [
    "translator_peak_memory",
    "translator_time_done"
]

exp.add_step("build", exp.build)
exp.add_step("start", exp.start_runs)
exp.add_fetcher(name="fetch")
exp.add_report(
    AbsoluteReport(attributes=ATTRIBUTES),
               outfile='report.html')

exp.run_steps()
