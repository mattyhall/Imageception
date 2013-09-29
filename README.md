Imageception
============

Imageception creates images from other images and was built for YRS 2012.

Usage
-----
Create a directory called images and then create directories under that with images you want it to use. Also create a directory called static and uploads. For example:

    imageception/
      average_colour.py
      server.py
      src_image.jpg
      templates/
      static/
      uploads/
      images/
        olympics/
          bolt.jpg
          5454.jpg
        holiday/
          beach.jpg
          castle.jpg

You can then run:

    python2.7 average_colour.py src_image.jpg olympics

To generate a version of src_image.jpg out of the photos in the images/olympics folder. The finished image can be found at static/src_image_done.jpg. You can also run server.py and go to 127.0.0.1:8080/view/src_image to view the image. Clicking on an image inside the image will run average_colour.py on that image using the same set as the parent was created with. If you want to be able to download images from Flickr edit flickr.py with your key(s)
