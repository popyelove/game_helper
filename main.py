#coding:'utf-8'
import struct
import Quartz.CoreGraphics as CG
from PIL import Image
import pytesseract
import webbrowser
import time
class ScreenPixel(object):
    """Captures the screen using CoreGraphics, and provides access to
    the pixel values.
    """

    def capture(self, region = None):
        """region should be a CGRect, something like:
        >>> import Quartz.CoreGraphics as CG
        >>> region = CG.CGRectMake(0, 0, 100, 100)
        >>> sp = ScreenPixel()
        >>> sp.capture(region=region)

        The default region is CG.CGRectInfinite (captures the full screen)
        """
        #import Quartz.CoreGraphics as CG

        if region is None:
            region = CG.CGRectInfinite
        else:
            # TODO: Odd widths cause the image to warp. This is likely
            # caused by offset calculation in ScreenPixel.pixel, and
            # could could modified to allow odd-widths
            if region.size.width % 2 > 0:
                emsg = "Capture region width should be even (was %s)" % (
                    region.size.width)
                raise ValueError(emsg)

        # Create screenshot as CGImage
        image = CG.CGWindowListCreateImage(
            region,
            CG.kCGWindowListOptionOnScreenOnly,
            CG.kCGNullWindowID,
            CG.kCGWindowImageDefault)

        # Intermediate step, get pixel data as CGDataProvider
        prov = CG.CGImageGetDataProvider(image)

        # Copy data out of CGDataProvider, becomes string of bytes
        self._data = CG.CGDataProviderCopyData(prov)

        # Get width/height of image
        self.width = CG.CGImageGetWidth(image)
        self.height = CG.CGImageGetHeight(image)

    def pixel(self, x, y):
        """Get pixel value at given (x,y) screen coordinates

        Must call capture first.
        """

        # Pixel data is unsigned char (8bit unsigned integer),
        # and there are for (blue,green,red,alpha)
        data_format = "BBBB"

        # Calculate offset, based on
        # http://www.markj.net/iphone-uiimage-pixel-color/
        offset = 4 * ((self.width*int(round(y))) + int(round(x)))

        # Unpack data from string into Python'y integers
        b, g, r, a = struct.unpack_from(data_format, self._data, offset=offset)

        # Return BGRA as RGBA
        return (r, g, b, a)


def get_screenshot():
    sp = ScreenPixel()
    sp.capture()
    im = Image.frombytes("RGBA", (sp.width, sp.height), sp._data)
    b, g, r, a = im.split()

    im = Image.merge("RGBA", (r, g, b, a))
    #box = (100, 300, 700, 550)  # 设置要裁剪的区域
    box = (20,200, 400, 300)  # 设置要裁剪的区域
    region = im.crop(box)  # 此时，region是一个新的图像对象。
    region.save("test.png","PNG")

    return region

start = time.time()
get_screenshot()
new_text = pytesseract.image_to_string(Image.open('test.png'), lang='chi_sim')
#new_text = ''.join(text.split())
import urllib.parse
from urllib.request import urlopen
keys={}
keys['wd']=new_text
new_text = urllib.parse.urlencode(keys)
url = 'https://www.baidu.com/s?'+new_text
webbrowser.open(url)
end=time.time()
print('耗时====>')
print(end-start)
#print(webbrowser.get())

# html=urlopen(url)
# print(html.read().decode('utf-8'))