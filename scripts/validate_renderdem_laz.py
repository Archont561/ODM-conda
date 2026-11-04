#!/usr/bin/env python3
"""Validate RenderDEM against a synthetic LAZ using a separately installed PDAL CLI.

This is integration research, not a release gate or proof of all LAZ formats.
The supplied prefix must include the candidate renderdem and pdal executables.
"""
from __future__ import annotations

import argparse
import os
import struct
import tempfile
from pathlib import Path

from common import ScaffoldError, fail_cli
from functional_test import execute, test_renderdem, tiff_first_ifd


def validate(prefix: Path) -> None:
    prefix=Path(prefix).resolve()
    renderdem=prefix/'bin/renderdem'; pdal=prefix/'bin/pdal'
    if not renderdem.is_file() or not pdal.is_file():
        raise ScaffoldError('Prefix must contain renderdem and the separate pdal CLI')
    env=os.environ.copy()
    try:
        os.environ['PATH']=str(prefix/'bin')+os.pathsep+os.defpath
        os.environ['PROJ_DATA']=os.environ['PROJ_LIB']=str(prefix/'share/proj')
        with tempfile.TemporaryDirectory(prefix='renderdem-laz-') as temp:
            work=Path(temp)
            test_renderdem(renderdem,work)
            las=work/'points.las'; laz=work/'points.laz'
            execute([str(pdal),'translate',str(las),str(laz)],work)
            data=laz.read_bytes()
            if len(data)<227 or data[:4]!=b'LASF' or not data[104]&0x80:
                raise ScaffoldError('PDAL did not produce a compressed LAS/LAZ file')
            execute([str(renderdem),'-i',str(laz),'-u','laz','-r','1','-s','1.5','-t','256','-x','1','-c','2'],work)
            outputs=list((work/'laz').glob('*.tif'))
            if len(outputs)!=1: raise ScaffoldError('Expected exactly one LAZ raster')
            raster=outputs[0].read_bytes(); tags=tiff_first_ifd(raster)
            if (tags.get(256),tags.get(257),tags.get(258),tags.get(339),tags.get(259,(1,))) != ((65,),(65,),(32,),(3,),(1,)):
                raise ScaffoldError('Unexpected LAZ raster shape or encoding')
            if tags.get(33550)!=(1.0,1.0,0.0) or tags.get(33922)!=(0.0,0.0,0.0,0.0,65.0,0.0):
                raise ScaffoldError('Unexpected LAZ raster geotransform')
            pixels=b''.join(raster[start:start+size] for start,size in zip(tags[273],tags[279]))
            if len(pixels)!=65*65*4 or struct.unpack('<4225f',pixels)!=(42.0,)*4225:
                raise ScaffoldError('Unexpected LAZ raster elevations')
    finally:
        os.environ.clear(); os.environ.update(env)
    print('PASS: generated PLY, LAS and compressed LAZ fixtures; 65x65 float raster elevations and geotransform',flush=True)


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix',required=True,type=Path)
    validate(parser.parse_args().prefix)


if __name__=='__main__': fail_cli(main)
