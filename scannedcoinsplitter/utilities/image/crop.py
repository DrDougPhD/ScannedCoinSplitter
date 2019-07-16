#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy
import logging
import cv2
import pathlib
from datetime import datetime
from PIL import Image

logger = logging.getLogger(__name__)

from . import ImageFromScan


class CroppingBox:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.centroid = numpy.array([x + (w / 2), y + (h / 2)])

    def area(self):
        return self.w * self.h

    def expand(self, padding, offset):
        box = CroppingBox(
            x=self.x + offset - padding,
            y=self.y + offset - padding,
            w=self.w + (2*padding),
            h=self.h + (2*padding),
        )
        logger.debug("Expanding borders of {0} by {1} pixels".format(self, padding))
        return box

    def getCorners(self):
        return {
            "min_x": self.x,
            "max_x": self.x + self.w,
            "min_y": self.y,
            "max_y": self.y + self.h,
        }

    def __str__(self):
        return "<CroppingBox(area={0}, w={1}, h={2}, upper_left={3}, lower_right={4})>".format(
            self.area(),
            self.w,
            self.h,
            (self.x, self.y),
            (self.x + self.w, self.y + self.h),
        )


class ImageCropper(object):
    def __init__(self, original_file_path, dest):
        self.dest = pathlib.Path(dest)
        self.filename = pathlib.Path(original_file_path)\
            .name.split(".")[0]
        self.img = cv2.imread(str(original_file_path))
        self.n = 0

        self.dest.mkdir(exist_ok=True, parents=True)

    def crop(self, min_x, max_x, min_y, max_y):
        cropped_img = self.img[min_y:max_y, min_x:max_x]
        cropped_img_url = self.dest / "{0}_{1}.png".format(
            self.n, self.filename)
        cv2.imwrite(str(cropped_img_url), cropped_img)
        self.n += 1
        return str(cropped_img_url)


class SplitScan(object):
    def __init__(self):
        self.split_imgs = []

    def add(self, box, img):
        self.split_imgs.append(ImageFromScan(box=box, img=img))

    def reorderByMinimumDistance(self, other_split_scan):
        original_images = list(self.split_imgs)
        reordered_images = []
        for img in other_split_scan:
            distance = lambda i: numpy.linalg.norm(i.box.centroid - img.box.centroid)
            i = min(original_images, key=distance)
            logger.debug("{0} distance between\n\t{1} and\n\t {2}".format(
                distance(i), img.box, i.box
            ))
            reordered_images.append(i)
            original_images.remove(i)
        self.split_imgs = reordered_images

    def __iter__(self):
        for i in self.split_imgs:
            yield i

    def __len__(self):
        return len(self.split_imgs)


class CroppedImageMerger(object):
    WHITE = (255, 255, 255)

    def __init__(self, dest):
        self.n = 0
        self.results = []
        self.dest = pathlib.Path(dest)

        self.dest.mkdir(exist_ok=True, parents=True)

    def merge(self, img1, img2):
        # If the aspect ratio of one of the images is less than 1, with some wiggle
        #  room, then the two files will be vertically merged. Otherwise, horizontal
        #  merging.
        if (img1.h / float(img1.w)) < 0.95:
            result = self.verticalMerge(img1, img2)

        else:
            result = self.horizontalMerge(img1, img2)

        url_safe_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        merged_url = str(self.dest / f'{url_safe_datetime}_{self.n}.png')

        self.n += 1
        result.save(merged_url)

        self.results.append(merged_url)
        return merged_url

    def verticalMerge(self, img1, img2):
        logger.info("Vertical merging of {0} and {1}".format(img1.url, img2.url))
        max_width = max(img1.w, img2.w)
        concatenated_height = img1.h + img2.h
        result = Image.new(
            "RGBA",
            (max_width, concatenated_height),
            color=self.WHITE
        )
        result.paste(Image.open(img1.url), (0, 0))
        result.paste(Image.open(img2.url), (0, img1.h))
        return result

    def horizontalMerge(self, img1, img2):
        logger.info("Horizontal merging of {0} and {1}".format(img1.url, img2.url))
        max_height = max(img1.h, img2.h)
        concatenated_width = img1.w + img2.w
        result = Image.new(
            "RGBA",
            (concatenated_width, max_height),
            color=self.WHITE)
        result.paste(Image.open(img1.url), (0, 0))
        result.paste(Image.open(img2.url), (img1.w, 0))
        return result
