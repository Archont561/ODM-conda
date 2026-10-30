# Disposable integration trial template

This unexecuted template builds private reduced-source Poisson, scoped OpenSfM
and OpenMVS candidates, installs them with six other packages into a fresh
prefix, checks selected imports/mode guards, and attempts the Seneca pipeline.
It is not a release workflow. Its original inputs, reduced sources, packages,
dataset and outputs must remain private and are discarded on job completion.
Dataset rights and output quality remain unverified.

The embedded historic artifact IDs have finite retention and must be verified
before use. The current sandbox could not connect to GitHub to dispatch the
trial. To run after reconnecting, copy `runner.py` to `scripts/tmp_sprint75.py`
and `workflow.yml` to `.github/workflows/tmp-sprint75.yml` on the current
session branch, validate the workflow, then push that branch. Remove the two
temporary copies after the run; they are not a production workflow. No result
should be claimed until the native job has actually completed.
