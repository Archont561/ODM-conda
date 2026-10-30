# Combined ODM environment inventory

[Private fresh linux-64 run 41085659812](https://github.com/Archont561/ODM-conda/actions/runs/41085659812)
built the three reduced candidates locally, installed them alongside six
previously validated component binaries into a new environment, and ran the
selected preflight and scoped-OpenSfM checks. It recorded 402 installed Conda
records in [`odm-combined-conda-inventory.json`](odm-combined-conda-inventory.json).
The run did not execute the Seneca pipeline. The complete sanitized metadata
was recovered from bounded job-log chunks by read-only
[run 41088000602](https://github.com/Archont561/ODM-conda/actions/runs/41088000602).
The `source_package_url` key from the original output was renamed to the more
accurate `binary_package_url`; the original serialized JSON SHA256 is recorded
in the file. No binaries, sources or imagery were uploaded.

The report contains all nine local package identities plus 393 Conda-forge
records. Conda records omit SHA256 for all nine local-file packages; the other
393 provide SHA256. The six reused package files were independently checked in
the inventory run (see its job annotations); hashes of the three newly built
packages are not established by this inventory. Thirteen `libopenvino` records
lack a license field. 305 records have no filename matching the notice-path
heuristic; this does not establish a missing notice or compliance. Binary
package URLs are not corresponding source URLs. This snapshot does not cover
pip distributions, package file bytes, exact upstream source, license obligations,
complete source offers, or runtime ABI and security validation. Package metadata
is an observation, not legal or release approval; repeated solves may differ.
