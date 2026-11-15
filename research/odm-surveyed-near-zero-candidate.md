# Surveyed near-zero imagery candidate: Madeira Beach

This is a feasibility investigation, **not an ODM ground-truth test**. No image,
survey data, or binary has been added to the repository or uploaded as an
artifact. A full pipeline on these images has not been run.

## Sources and reuse

Brown, Kranenburg and Morgan, USGS, *Time Series of Aerial Imagery from Small
Unmanned Aircraft Systems and Associated Ground Control Points: Madeira Beach,
Florida, July 2017 to June 2018*, [DOI 10.5066/P91TH157](https://doi.org/10.5066/P91TH157).
The [imagery metadata](https://cmgds.marine.usgs.gov/catalog/spcmsc/MadeiraBeachFL_UAS_Imagery_metadata.txt)
and [GCP metadata](https://cmgds.marine.usgs.gov/catalog/spcmsc/2017-2018_MadeiraBeachFL_GCPs_metadata.txt)
state that USGS-authored data are public domain and freely redistributable with
metadata and source attribution. This is source-specific evidence, not an owner
approval for a package or release.

## Observations

* The bounded GCP ZIP inspection in hosted runs 43721714189 and 43722350331
  found the 2017-08-16 survey has 52 points, nine within ±0.25 m NAVD88,
  including six marked check points. The closest absolute height is 0.021 m,
  and it is a check point. This is **near zero, not measured exact zero**.
  GCP archive SHA-256:
  `5a1517c4348a13db80722ca4781d2d8f3226c00970b344be91abdd96880e9a32`.
  July's GCP file is absent from that archive; use a matched survey date.
* GCP metadata states NAD83(2011) UTM zone 17N and NAVD88 orthometric
  elevations using GEOID12B, with 5 cm recommended vertical accuracy. This
  is a dataset-level statement, not a point-specific uncertainty estimate.
* The August imagery ZIP is 7,555,083,495 bytes and contains 466 JPEGs.
  Run 43722196942 read only bounded ZIP ranges and sampled ten images
  (164,870,650 bytes total); all had EXIF GPS and dimensions 4944×3280.
  Their camera positions were approximately 13.8–186.5 m from the nearest
  near-zero check point. This does **not** establish visibility, overlap,
  camera calibration or accurate pixel observations.
* The imagery metadata explicitly says camera vertical positions are **above
  ground level**, with ±5 m vertical uncertainty. Image positions may be off by
  as much as 20 m horizontally because of geotagging and clock precision. AGL
  EXIF heights cannot be treated as NAVD88 or ellipsoidal elevations; relying on
  them would invalidate an absolute-height comparison. Imagery metadata SHA-256
  in hosted run 43722350331:
  `b9b6f8f9e4a8f221c38a7920af81fe7f6a70a89717c096bd7aa62333171a1fd8`.
* The supplied GCP files contain geographic positions but not ODM image-pixel
  observations. The source's check-point designation alone does not establish
  independence in a new reconstruction. GCP coordinates and image positions
  need verified target identification in overlapping images, and checkpoints
  must be withheld from reconstruction and alignment. A surface sample must
  also represent the actual surveyed target rather than water, nodata or an
  unrelated DSM object.

## Next experiment and limitations

Identify several control targets in sufficient images spanning both submodels;
record reproducible image-pixel observations and uncertainty. Select separate
near-zero checkpoints that were never used for either model or its alignment.
Use a verified NAD83(2011)/NAVD88 GEOID12B transformation and make the
camera-height datum explicit; do not interpret AGL EXIF heights as absolute.
Verify independent submodel coverage and compare their unmodified DEMs and merged
output at the withheld target locations, recording errors and masks. A low
absolute height within survey uncertainty is not proof of an exact physical
zero, and forcing a zero would only be a controlled intervention.

The existing [real-derived trial](odm-real-data-zero-evidence.json) and
[SRTM-format overlap trial](odm-srtm-zero-overlap-evidence.json) test different
properties; neither supplies this independent validation. Their direct-app
split invocation bypasses restrictions in the private research launcher and is
not supported production behavior. Release, licensing, ABI and owner approval
gates remain unchanged.
