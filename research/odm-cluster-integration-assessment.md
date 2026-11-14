# ClusterODM integration: static assessment, not a distributed test

Scope: ODM 3.6.2 source pinned at
[`47f41f1f2d09f7c15dff33dd3c15ab29c8a97d45`](https://github.com/OpenDroneMap/ODM/tree/47f41f1f2d09f7c15dff33dd3c15ab29c8a97d45).
No ClusterODM/NodeODM service was started, and no remote processing or
network protocol compatibility has been demonstrated. The private launcher still
rejects `--sm-cluster` and split/DTM. Self-hosted runner testing remains skipped.

## What ODM does

- `ODMSplitStage` selects `LocalRemoteExecutor` for a configured `--sm-cluster`;
  without one, the tested split path is local. Upstream executor creates a
  PyODM `Node` from that URL. If the node is offline, it can fall back to local
  processing, so successful output alone does **not** prove remote work.
- Reconstruction tasks upload images and seed files, request OpenSfM features,
  matches, tracks and reconstruction; toolchain tasks upload a seed including
  reconstruction/tracks and request orthophoto, DEM, report and georeferencing
  results. Task completion, download/extraction and cleanup use PyODM APIs.
- The coordinating process merges downloaded outputs locally. A remote worker
  executes its **own ODM environment**; the local Conda solve does not prove its
  engine version, dependencies, model cache, licensing or result compatibility.
  Classification/DTM requires suitable model availability and compatible workers.
- ODM task arguments come from `get_submodel_args_dict`; our private patch removes
  explicit `split_image_groups` from derived child arguments. This is a static
  code observation, not an end-to-end remote compatibility result.

## Next validation, before enabling

1. Pin a NodeODM/ClusterODM version and separately review its source, dependency
   and model distribution rights; define an owner-approved isolated endpoint.
2. Test the PyODM info/task/upload/status/download/remove API using generated
   minimal data and mocks or a disposable service; assert a remote task was
   actually created and completed, not merely local fallback.
3. Exercise failure, disconnect/retry, task cleanup, seed archive and extracted
   output safety, bounded resources, and classification/model availability.
4. Compare remote worker package/engine identities and returned CRS, dimensions,
   point counts, rasters and merge outputs against the scoped local checks.
   Avoid uploading unreviewed source, models or datasets to public artifacts.

No general release, network safety, or license approval is implied.
