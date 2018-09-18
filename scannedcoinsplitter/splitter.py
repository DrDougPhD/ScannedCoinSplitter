#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import cv2
import numpy

logger = logging.getLogger(__name__)

import config
from . import utilities


def extract_ingots(raw_scanned_image_path):
    raw_scanned_image = cv2.imread(str(raw_scanned_image_path))
    archiver = utilities.IntermediateImageArchiver(
        original_image_path=raw_scanned_image_path,
        archival_directory=config.defaults.intermediate_archival_directory
    )

    border_width = config.defaults.border_reduction
    reduced_border_image = raw_scanned_image[
        border_width:-border_width,
        border_width:-border_width
    ]

    gray_scanned_image = cv2.cvtColor(
        reduced_border_image,
        cv2.COLOR_BGR2GRAY
    )
    archiver.archive_image(opencv_image=gray_scanned_image, image_name='gray')

    threshold = cv2.adaptiveThreshold(
        gray_scanned_image,
        255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
        11, 2
    )
    archiver.archive_image(opencv_image=threshold, image_name='threshold')

    kernel = numpy.ones((8, 8), numpy.uint8)
    opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
    archiver.archive_image(opencv_image=opening, image_name="opening")

    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
    archiver.archive_image(opencv_image=closing, image_name="closing")

    negated = cv2.bitwise_not(closing)
    archiver.archive_image(opencv_image=negated, image_name="negated")

    _, contours, hierarchy = cv2.findContours(
        negated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    blank_image_contours = numpy.zeros(raw_scanned_image.shape, numpy.uint8)
    blank_image = numpy.zeros(raw_scanned_image.shape, numpy.uint8)

    cropper = utilities.ImageCropper(
        original_file_path=raw_scanned_image_path,
        dest=config.defaults.cropped_output_directory
    )
    split = utilities.SplitScan()

    next_countour_indices = hierarchy[0, :, 0]
    next_index = 0
    while next_index != -1:
        c = contours[next_index]
        cv2.drawContours(blank_image_contours, c, -1, (255, 0, 0), 5)
        x, y, w, h = cv2.boundingRect(c)
        box = utilities.CroppingBox(x=x, y=y, w=w, h=h)

        # scale up these coordinates to their original size
        if box.area() > config.defaults.minimum_coin_area:
            box = box.expand(border_width)
            logger.debug(box)

            img = cropper.crop(**box.getCorners())
            split.add(box=box, img=img)

            upper_left = box.x, box.y
            lower_right = box.x + box.w, box.y + box.h
            cv2.rectangle(
                blank_image, upper_left, lower_right,
                utilities.random_color(),
                10
            )

        next_index = next_countour_indices[next_index]

    archiver.archive_image(opencv_image=blank_image_contours, image_name="contours")
    archiver.archive_image(opencv_image=blank_image, image_name="bounding_boxes")

    logger.info("Number of detected objects: {0}".format(len(split)))

    return split


def merge(obverse, reverse, destination):
  merger = utilities.CroppedImageMerger(destination)

  obverse.reorderByMinimumDistance(reverse)

  for ingot1, ingot2 in zip(obverse, reverse):
    merged = merger.merge(ingot1, ingot2)
    logger.info("{0} and {1} => {2}".format(ingot1.url, ingot2.url, merged))

  if len(obverse) != len(reverse):
    logger.error(
      "For the two scans, the number of split images is not equal "
      "({0} vs {1})".format(
        len(obverse), len(reverse)
    ))

  return merger.results