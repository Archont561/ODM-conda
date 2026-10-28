"""Property-based tests (hypothesis) for the pure packaging helpers.

Every property here stays hermetic: no network, no Pixi-only binaries, no
native builds. These fuzz the safety and round-trip invariants that the
example-based suite only probes at selected points: the installed-fixture
TIFF writer/parser pair, path-safety guards, notice extraction, package
member validation, component selection, and the human release gates.
"""
from __future__ import annotations

import copy
import struct

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from common import CHECKS, ScaffoldError, config, first_comment, relative_path, release_tag, select_components
from functional_test import tiff_first_ifd, write_tiff_f32
from package_archive import validate_member
from release_guard import reviewed_component

# Disk-touching properties (tmp_path, components.json reads) must not flake
# on slow shared runners. The function-scoped tmp_path fixture is deliberately
# shared across examples: every property either overwrites the same file or
# never writes at all, so no state accumulates between generated inputs.
hermetic = settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])

IMPLEMENTED = frozenset(config()["components"])
# Segments that can never be ".", "..", absolute, or contain separator tricks.
SAFE_SEGMENT = st.from_regex(r"[A-Za-z0-9][A-Za-z0-9._-]{0,7}", fullmatch=True)


@hermetic
@given(data=st.data())
def test_tiff_writer_round_trips_every_raster(tmp_path, data):
    width = data.draw(st.integers(1, 33), label="width")
    height = data.draw(st.integers(1, 33), label="height")
    values = data.draw(
        st.lists(st.floats(width=32, allow_nan=False, allow_infinity=False),
                 min_size=width * height, max_size=width * height),
        label="values",
    )
    path = tmp_path / "raster.tif"
    write_tiff_f32(path, width, height, values)
    blob = path.read_bytes()
    # Deterministic minimal layout: header + 12-entry IFD + geo overflow + one strip.
    assert len(blob) == 8 + 2 + 12 * 12 + 4 + 24 + 48 + 4 * width * height
    tags = tiff_first_ifd(blob)
    assert tags[256] == (width,)
    assert tags[257] == (height,)
    assert tags[258] == (32,) and tags[259] == (1,) and tags[262] == (1,)
    assert tags[277] == (1,) and tags[278] == (height,) and tags[339] == (3,)
    assert tags[33550] == (1.0, 1.0, 0.0)
    assert tags[33922] == (0.0, 0.0, 0.0, 100.0, 200.0, 0.0)
    strips = b"".join(blob[start:start + size] for start, size in zip(tags[273], tags[279]))
    assert struct.unpack(f"<{width * height}f", strips) == tuple(values)


@hermetic
@given(parts=st.lists(SAFE_SEGMENT, min_size=1, max_size=4))
def test_relative_path_accepts_safe_posix_paths(tmp_path, parts):
    value = "/".join(parts)
    assert relative_path(tmp_path, value) == (tmp_path / value).resolve()


@hermetic
@given(
    prefix=st.sampled_from(["", "safe/", "a/b/"]),
    climbs=st.lists(st.just(".."), min_size=1, max_size=3),
    tail=st.sampled_from(["", "/x", "/../y"]),
)
def test_relative_path_rejects_every_traversal_form(tmp_path, prefix, climbs, tail):
    with pytest.raises(ScaffoldError):
        relative_path(tmp_path, prefix + "/".join(climbs) + tail)


@hermetic
@given(value=st.one_of(
    st.just(""),
    st.text(max_size=30).map(lambda text: "/" + text),
    st.text(max_size=30).map(lambda text: text + "\\drive"),
))
def test_relative_path_rejects_empty_absolute_and_windows_forms(tmp_path, value):
    with pytest.raises(ScaffoldError):
        relative_path(tmp_path, value)


@hermetic
@given(
    lead=st.from_regex(r"[ \t\r\n]{0,8}", fullmatch=True),
    # The joined prefix must stay free of "*/": a body starting with b"/"
    # would otherwise close the comment at the junction (b"/*" + b"/").
    body=st.binary(max_size=200).filter(lambda chunk: b"*/" not in b"/*" + chunk),
)
def test_first_comment_extracts_the_first_block_verbatim(lead, body):
    source = lead.encode() + b"/*" + body + b"*/\nint main() { return 0; }\n"
    assert first_comment(source) == b"/*" + body + b"*/\n"


@hermetic
@given(payload=st.binary(max_size=200))
def test_first_comment_rejects_sources_without_a_leading_block(payload):
    with pytest.raises(ScaffoldError):
        first_comment(b"// " + payload)


@hermetic
@given(body=st.binary(max_size=200).filter(lambda chunk: b"*/" not in b"/*" + chunk))
def test_first_comment_rejects_unterminated_blocks(body):
    with pytest.raises(ScaffoldError):
        first_comment(b"/*" + body)


@hermetic
@given(segments=st.lists(SAFE_SEGMENT, min_size=1, max_size=4))
def test_validate_member_accepts_safe_member_names(segments):
    validate_member("/".join(segments))


@hermetic
@given(name=st.one_of(
    st.just(""),
    st.text(max_size=30).map(lambda text: "/" + text),
    st.text(max_size=30).map(lambda text: text + "\\"),
    st.text(max_size=30).map(lambda text: text + ":"),
    st.lists(st.just(".."), min_size=1, max_size=2).map("/".join),
))
def test_validate_member_rejects_unsafe_member_names(name):
    with pytest.raises(ScaffoldError):
        validate_member(name)


@hermetic
@given(name=st.text(max_size=80))
def test_select_components_never_invents_components(name):
    try:
        selected = select_components(name)
    except ScaffoldError:
        return
    assert selected and set(selected) <= IMPLEMENTED
    parts = [part.strip() for part in name.split(",")]
    assert parts == ["all"] or (len(parts) == len(set(parts)) and list(selected) == parts)


@hermetic
@given(
    name=st.sampled_from(sorted(IMPLEMENTED)),
    broken=st.sets(st.sampled_from(sorted(CHECKS)), min_size=1),
    poison=st.one_of(st.just(False), st.just("true"), st.just(1), st.just(None)),
)
def test_any_non_true_gate_blocks_release(name, broken, poison):
    data = copy.deepcopy(config())
    component = data["components"][name]
    for key in component["release_checks"]:
        component["release_checks"][key] = True
    for key in broken:
        component["release_checks"][key] = poison
    with pytest.raises(ScaffoldError, match="blocked"):
        reviewed_component(release_tag(name, component), data)


@hermetic
@given(name=st.sampled_from(sorted(IMPLEMENTED)))
def test_all_gates_true_releases_the_exact_component(name):
    data = copy.deepcopy(config())
    component = data["components"][name]
    for key in component["release_checks"]:
        component["release_checks"][key] = True
    assert reviewed_component(release_tag(name, component), data)[0] == name
