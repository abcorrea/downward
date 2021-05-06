#! /usr/bin/env python
# -*- coding: utf-8 -*-

import common_setup

from common_setup import IssueConfig, IssueExperiment

import os

from lab.reports import Attribute

from lab.environments import LocalEnvironment, BaselSlurmEnvironment

from downward import suites
from downward.experiment import FastDownwardExperiment
from downward.reports.absolute import AbsoluteReport

REVISIONS = ["issue1015"]

CONFIGS = []

class ModifiedIssueExperiment(IssueExperiment):
    
    def __init__(self, revisions=None, configs=None, path=None, **kwargs):
        IssueExperiment.__init__(self, revisions, configs, path, **kwargs)

    def _add_runs(self):
        """
            From https://lab.readthedocs.io/en/stable/downward.tutorial.html#id2
        """
        FastDownwardExperiment._add_runs(self)
        for run in self.runs:
            command = run.commands["planner"]
            # Slightly raise soft limit for output to stdout.
            command[1]["soft_stdout_limit"] = 100 * 1024
            command[1]["hard_stdout_limit"] = 100 * 1024


for i in range(5):
    CONFIGS.append(IssueConfig("translate-"+str(i), ["--search-option", str(i)],
                               driver_options=["--translate"]))

BENCHMARKS_DIR = os.environ["HTG_BENCHMARKS"]
REPO = os.environ["DOWNWARD_REPO"]

if common_setup.is_running_on_cluster():
    SUITE = ['genome-edit-distance',
             'genome-edit-distance-positional',
             'genome-edit-distance-split',
             'logistics',
             'organic-synthesis-alkene',
             'organic-synthesis-MIT',
             'organic-synthesis-original',
             'pipesworld-tankage-nosplit']
    ENVIRONMENT = BaselSlurmEnvironment(
        partition="infai_2",
        export=["PATH", "HTG_BENCHMARKS"],
    )
else:
    SUITE = ["organic-synthesis-alkene:p2.pddl",
             "organic-synthesis-alkene:p5.pddl"]
    ENVIRONMENT = LocalEnvironment(processes=2)

exp = ModifiedIssueExperiment(
    revisions=REVISIONS,
    configs=CONFIGS,
    environment=ENVIRONMENT,
)

exp.add_suite(BENCHMARKS_DIR, SUITE)

for run in exp.runs:
    command = run.commands["planner"]
    command[1]["soft_stdout_limit"] = 1024 * 100
    command[1]["hard_stdout_limit"] = 1024 * 100

exp.add_parser(exp.TRANSLATOR_PARSER)
ATTRIBUTES = [
    "translator_auxiliary_atoms",
    "translator_axioms",
    "translator_axioms_removed",
    "translator_axioms_removed_by_simplifying",
    "translator_derived_variables",
    "translator_effect_conditions_simplified",
    "translator_facts",
    "translator_final_queue_length",
    "translator_goal_facts",
    "translator_implied_preconditions_added",
    "translator_mutex_groups",
    "translator_operators",
    "translator_operators_removed",
    "translator_peak_memory",
    "translator_propositions_removed",
    "translator_relevant_atoms",
    "translator_task_size",
    "translator_time_building_dictionary_for_full_mutex_groups",
    "translator_time_building_mutex_information",
    "translator_time_building_strips_to_sas_dictionary",
    "translator_time_building_translation_key",
    "translator_time_checking_invariant_weight",
    "translator_time_choosing_groups",
    "translator_time_collecting_mutex_groups",
    "translator_time_completing_instantiation",
    "translator_time_computing_fact_groups",
    "translator_time_computing_model",
    "translator_time_computing_negative_axioms",
    "translator_time_detecting_unreachable_propositions",
    "translator_time_done",
    "translator_time_finding_invariants",
    "translator_time_generating_datalog_program",
    "translator_time_instantiating",
    "translator_time_instantiating_groups",
    "translator_time_normalizing_datalog_program",
    "translator_time_normalizing_task",
    "translator_time_parsing",
    "translator_time_preparing_model",
    "translator_time_processing_axioms",
    "translator_time_reordering_and_filtering_variables",
    "translator_time_simplifying_axioms",
    "translator_time_translating_task",
    "translator_time_writing_output",
    "translator_total_mutex_groups_size",
    "translator_total_queue_pushes",
    "translator_uncovered_facts",
    "translator_variables"
]

exp.add_step("build", exp.build)
exp.add_step("start", exp.start_runs)
exp.add_fetcher(name="fetch")
exp.add_report(
    AbsoluteReport(attributes=ATTRIBUTES),
               outfile='report.html')

exp.run_steps()
