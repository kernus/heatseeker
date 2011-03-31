#!/usr/bin/python
#
# This code generates heat maps.  Given a list of 2D positions and a background image, this code
# generates clusters of positions, colors them by intensity, and blends them with the background
# image.  
#
# This code has the following dependencies:
#   * spot.png - A radial gradient used to mark individual heat points.
#   * colors.png - An image describing the range of colors to map to heat intensity.
#
# It takes the following command line arguments:
#   * event file - A text file of 2D event positions, one per line, in the format x,y.
#   * background image - An image over which the heat map will be blended.
#   * canvas size x - The width of the output image (usually the width of the background image).
#   * canvas size y - The height of the output image (usually the height of the background image).
#   * scale - A value indicating the level of bias in heat map composition.  Optional, defaults
#       to 1.0 (no bias).
#
# This script generates a file called "heatmap.png" as its output.
#
#
# The algorithm for generating a heat map is as follows:
#   1. Read in the list of event positions, and maintain a reference count for common positions.
#   2. The position with the highest reference count indicates the hottest spot on the map.  Call
#     the number of references at that spot value M.
#   3. Generate an empty white canvas image.
#   4. For each unique event location, multiply the spot graphic to the canvas image at the location
#     of the event.  Fade the spot opacity to ((N / M) * scale * 100)%, where N is the number of 
#     references at the current event location.
#   5. Colorize the image by inverting it and then mapping the intensity of each pixel to a Y
#     position in the color range file.  This will make hot spots red, cold spots blue, etc.
#   6. Overlay the resulting image with the specified background image.
#
'''
To use this script make the following changes:

replace event_file with the file containing your x and y coordinates.
replace canvas_size_x with the width of the output image
replace canvas_size_y with the height of the output image
replace level_file with the background image of the level or screen
replace [scale] with the level of bias you want. Defaults to 1
'''
import os
import sys
import subprocess

"""Tool for generating heat maps using ImageMagick"""


def main(argv):
  """This is the main function."""

  if len(argv) < 4:
    sys.exit('Usage: process.py event_file level_file canvas_size_x canvas_size_y [scale]')
  
  if not os.path.exists(argv[0]):
    sys.exit('ERROR: File %s was not found!' % argv[0])
    
  if not os.path.exists(argv[1]):
    sys.exit('ERROR: File %s was not found!' % argv[1])
  
  scale = 1.0
  if len(argv) > 4:
    scale = float(argv[4])
    
  GenerateHeatMap(argv[0], argv[1], argv[2], argv[3], scale)
  
  return
  
def GenerateHeatMap(event_file, level_image, canvas_size_x, canvas_size_y, scale):
  """Generates a heat map and saves it as heatmap.png."""

  print "Reading %s..." % event_file
  
  # Read the input event file and accumulate references to common locations.
  file = open(event_file, "r")
  uniqueLocations = { }
  maxRepetitions = 0
  # One location per line, x,y format.
  for location in file:
    if location not in uniqueLocations:
      uniqueLocations[location] = 1   # first reference
    else:
      uniqueLocations[location] += 1

    if uniqueLocations[location] > maxRepetitions: 
      maxRepetitions = uniqueLocations[location]
  
  # Generate the canvas image
  Execute(['convert', '-size', canvas_size_x + 'x' + canvas_size_y, 'pattern:gray100', 
      'empty.miff'])
  
  # maxRepetitions indicates the number of events at the hottest point on the map.
  print "%d max repetitions" % maxRepetitions
  
  total_count = len(uniqueLocations)
  ten_percent = total_count / 10
  count = 0
  percent = 0
  
  # For each spot on the map, calculate an opacity and multiply the spot image to the canvas.
  for location in uniqueLocations:
    xy = location.split(",")
    
    # Spot image is 64x64, so center it
    # TODO: this should probably use ImageMagick's "identify" to pull the size of the image.
    x = (int(xy[0]) / 2) - 32
    
    # GL space (+X+Y) to screen space (+X-Y) flip
    # TODO: This should probably be an option.
    y = (int(canvas_size_y) - (int(xy[1]) / 2)) - 32  
    
    # ImageMagicl requires coordinates in the form +X+Y.  We only need to prepend a "+" if the 
    # value is positive, as str() will insert a minus if it is negative.
    x_str = "+%d" % x
    if (x < 0):
      x_str = "%d" % x
    y_str = "+%d" % y
    if (y < 0):
      y_str = "%d" % y
          
    # Calculate the opacity of this dot.
    weight = uniqueLocations[location]
    contribution = float(weight) / maxRepetitions
    contribution *= scale
    
    # Invert the opacity.  We'll lighten the spot image by this amount to produce the desired
    # effect.
    contribution = 1.0 - contribution
    
    if (contribution > 0.0):
      # ImageMagick power user command line!
      # This takes spot.png, bends it with semi-transparent white, offsets it to our xy location,
      # multiplies the result to empty.miff, and then outputs the resulting image as empty.miff.
      # Note that I'm using the MIFF image format so that ImageMagick can store this data in a
      # floating point pixel format (if configured to use HDRI), hopefully preserving as much 
      # resolution as possible.
      Execute(['convert', 'empty.miff', 
          '(', 'spot.png', '-fill', 'white', '-colorize',  '%g%%' % (contribution * 100,), ')', 
          '-geometry', x_str + y_str, 
          '-compose', 'multiply', 
          '-composite', 'empty.miff'])

    count += 1
    # Output a status update every 10%.  This script can be pretty slow.
    if (count > ten_percent):
      percent += 10
      print "%d%%..." % percent
      count = 0
  
  # Colorize the image
  Execute(['convert', 'empty.miff', '-negate', 'full.miff'])
  Execute(['convert', 'full.miff', 'colors.png', '-fx', 'v.p{0,u*v.h}', 'final.miff'])
  
  # Composite over the background image, output final result.
  Execute(['composite', '-blend', '40%', 'final.miff', level_image, 'heatmap.png'])

  print "Complete."
  
  return

  
def Execute(args):
    """Executes a command"""
    if subprocess.call(args) > 0:
        raise RuntimeError('FAILED: ' + ' '.join(args))


if __name__ == '__main__':
  main(sys.argv[1:])
