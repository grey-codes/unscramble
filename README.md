# Unscramble
**CY420 Project 2**

This is an attempt to to solve and reverse scrambling (translation, 180 degree rotation) applied to an image, as in the following:


![Scrambled Image](https://github.com/grey-r/unscramble/blob/master/Messed32.jpg?raw=true)

Typically, the program is able to reverse around 70% of the image once the top-left corner is identified by the user.
From there, the user can identify which piece IDs belong at which row/column locations and add those to the input.
The result is that with just a few guided executions, the program can quickly unscramble a 4x8 grid.

## Methodology

While not ideal, the semi-automated solution wasn't the first attempt at this project.
At first, a fully automated solution was sought; however, this presents a number of issues, most related to the rotation

1. What direction is up?
2. Without knowing what direction is up, how can pieces be added in an orderly fashion?
3. If pieces can't be added in an orderly fashion, how can they be assembled?

Question 1 was outright unaddressable without some form of user input.

Question 2 could possibly be addressed; a piece could either be treated as flipped or not, and then the build up/right applied.
However, even if the above method were used, there's little way of telling which piece is a corner.

Question 3 is more difficult to address, and requires checking an arbitrary number of edges in an assortment of shapes.

The current approach ultimately proved much simpler to program given the constraints of time and prior forensic experience.

## Installation

Unscramble is meant to run on Python 3.7, and in theory higher versions.

It depends on libraries matplotlib, numpy, and (for jpg reading) pillow.

## Usage

Once the requirements are dealt with, the program may be ran using **python3 unscramble.py**.

It will read Messed32.jpg with hardcoded row count 4 and column count 8, modifiable in source.

Given the contents of sample_input.txt, this is enough data to entirely find the correct image.
