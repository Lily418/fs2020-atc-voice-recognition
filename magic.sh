#!/bin/bash

convert $1 \
-channel RGB -negate \
grey-$1