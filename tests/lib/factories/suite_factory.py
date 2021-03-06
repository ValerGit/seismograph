# -*- coding: utf-8 -*-

from seismograph.suite import (
    Suite,
    MountData,
)


def mark_is_build(suite):
    suite.__is_build__ = lambda: True


class FakeSuite(Suite):
    pass


def create(**kwargs):
    config = kwargs.pop('config', None)
    suite_class = kwargs.pop('suite_class', FakeSuite)

    suite = suite_class(__name__, **kwargs)
    suite.__mount_data__ = MountData(config)

    return suite
