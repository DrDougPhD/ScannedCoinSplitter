#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ImageFromScan(object):
    def __init__(self, box, img):
        self.url = img
        self.box = box
        self.h = box.h
        self.w = box.w
