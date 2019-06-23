#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random

r = lambda: random.randint(0, 255)
random_color = lambda: (r(), r(), r())
