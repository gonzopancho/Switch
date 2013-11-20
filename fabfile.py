#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fabric.api import *

@hosts('localhost')
def clean():
	run("find src/ -type f -iname '*.pyc' -print0 | xargs --replace --null rm -fv '{}'")
	run("rm -rf fabfile.pyc")

