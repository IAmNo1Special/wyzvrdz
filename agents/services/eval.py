"""Evaluation service for the agents package."""

from google.adk.evaluation.in_memory_eval_sets_manager import (
    InMemoryEvalSetsManager,
)
from google.adk.evaluation.local_eval_set_results_manager import (
    LocalEvalSetResultsManager,
)

from ..configs import ROOT_DIR

eval_sets_manager = InMemoryEvalSetsManager()
eval_set_results_manager = LocalEvalSetResultsManager(agents_dir=str(ROOT_DIR))
