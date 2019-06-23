#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pathlib
import cv2


class IntermediateImageArchiver(object):
    def __init__(self, original_image_path, archival_directory, scale=None):
        archival_directory.mkdir(parents=True, exist_ok=True)

        original_image_filename = pathlib.Path(original_image_path).name
        self.archived_filename_prefix = original_image_filename.split(".")[0]
        self.archival_directory = archival_directory
        self.scale = scale

        self.intermediate_image_number = 1

    def archive_image(self, opencv_image, image_name):
        scaled_image = self.scale_image(opencv_image)

        archived_image_path \
            = self.archival_directory / '{prefix}_{index}_{name}.png'.format(
                prefix=self.archived_filename_prefix,
                index=self.intermediate_image_number,
                name=image_name)
        cv2.imwrite(str(archived_image_path), scaled_image)
        self.intermediate_image_number += 1

    def scale_image(self, opencv_image):
        if self.scale is not None:
            for i in range(self.scale):
                opencv_image = cv2.pyrUp(opencv_image)

        return opencv_image
