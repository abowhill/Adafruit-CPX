import board
from adafruit_circuitplayground.express import cpx
import adafruit_fancyled.adafruit_fancyled as fancy
import math
import adafruit_lis3dh

## Shows g-force on x,y,z axes as:
##   Green (forward/backward)
##   Blue (left/right)
##   Red (up/down)
##
## Facing the CPX, with the USB socket at the top:
##   positive values start to the left of the USB socket
##   negative values start to the right of the USB socket
##
## Shaking the device along one axis produces the corresponding color
## scaled by the magnitude of the shaking force.

leds = 10        # total leds
accel_range = 4  # max accelerometer range in Gs (set below)

# accelerometer max range in Gs: can be 2,4,8 or 16 - higher is less accurate
# from https://circuitpython.readthedocs.io/projects/circuitplayground/en/latest/_modules/adafruit_circuitplayground/express.html
cpx._lis3dh.range = adafruit_lis3dh.RANGE_4_G

# default max values for scaling
max_led = leds - 1

# number of reading samples per program cycle
samples = 37

cpx.pixels.auto_write = True  # Refresh pixels only when we say
cpx.pixels.brightness = 1.0   # applies to whole board, upper limit, lossy, 0-1

class Axis:
   'Base class for an axis'

   def __init__(self,r,g,b,axis):
      # axis for this object
      self.axis = axis
      # buckets for each base measurement
      self.buckets  = [0,0,0,0,0,0,0,0,0,0]
       # measurement counts for each bucket
      self.count    = [0,0,0,0,0,0,0,0,0,0]
      # Black
      self.palette = [fancy.CRGB(0.0, 0.0, 0.0),0]
      # user-defined color
      self.palette[1] = fancy.CRGB(r,g,b)
      self.reading = 0.0
      self.max = accel_range + 1

   # clear_list function - sets an integer list to all-zeros
   # k = list to clear

   def clear_list(self, k):
     for idx in range(len(k)): k[idx]=0.0

   # scaling function - returns reading scaled from current range to new range
   #
   # val = reading
   # of_min = lower limit of current scale
   # of_max = upper limit of current scale
   # to_min = lower limit of destination scale
   # to_max = upper limit of destination scale
   # https://stackoverflow.com/questions/1456000/rescaling-ranges

   def scale(self, val, of_min = -5, of_max = 5, to_min = 1,  to_max = 9):
     a = val - of_min
     b = to_max -  to_min
     c = of_max - of_min
     d = to_min
     e = a * b
     f = c + d
     g = e / f

     return g
#     return( ((val - of_min) * (to_max - to_min)) / ((of_max - of_min) + to_min))

   def clear(self):
      self.clear_list(self.buckets)
      self.clear_list(self.count)

   def save(self):
      # store max reading for all runtime
      self.max = max(self.reading, self.max)
      # scale -5 to +5 readings into 0-9 led numbers
      _scale = self.scale ( (self.reading), -5, 5, 0, 9 )
      _int = math.floor(_scale)         # isolate integer part
      self.buckets[_int - 5] += _scale  # add to bucket index[integer part]
      self.count[_int - 5] += 1         # bump up reading count

   # not really consquential. Determines brightness of lights.
   def remainder(self,pixel):
      _remainder = (self.buckets[pixel] - int(self.buckets[pixel]) )
      if self.count[pixel]: _remainder /= self.count[pixel]
      return _remainder

   def log(self,id):
      print(id)
      print(self.count,)
      print(self.buckets,)
      input('->')




x = Axis(0.0,0.0,1.0,'x')
y = Axis(0.0,1.0,0.0,'y')
z = Axis(1.0,0.0,0.0,'z')

while True:

   cpx.red_led = True

   x.clear()
   y.clear()
   z.clear()

   for reading in range(samples):
      x.reading, y.reading, z.reading = \
         [value / 9.806 for value in cpx.acceleration]
      x.save()
      y.save()
      z.save()

  # x.log('x')
  # y.log('y')
  # z.log('z')

   cpx.red_led = False

   for pixel in range(10):
      
      xcolor = fancy.palette_lookup(x.palette, x.remainder(pixel))
      ycolor = fancy.palette_lookup(y.palette, y.remainder(pixel))
      combined_color = fancy.mix(xcolor,ycolor)

      zcolor = fancy.palette_lookup(z.palette, z.remainder(pixel))
      combined_color = fancy.mix(combined_color,zcolor)

      cpx.pixels[pixel] = combined_color.pack()

   cpx.pixels.show()
