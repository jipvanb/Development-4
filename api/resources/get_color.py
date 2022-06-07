def get_color():
    import sys

    if sys.version_info < (3, 0):
        from urllib2 import urlopen
    else:
        from urllib.request import urlopen

    import io

    from colorthief import ColorThief

    fd = urlopen('http://127.0.0.1:5000/color/3')
    f = io.BytesIO(fd.read())
    color_thief = ColorThief(f)
    print(color_thief.get_color(quality=1))
    print(color_thief.get_palette(quality=1))
    return {"color":color_thief.get_color(quality=1),"palette":color_thief.get_palette(quality=1)}
