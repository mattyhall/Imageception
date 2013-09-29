from flask import Flask, render_template, request, redirect
from flaskext.uploads import IMAGES, UploadSet, configure_uploads
import os
import flickr
from average_colour import folder
import urllib
import urlparse
import csv
import pycurl
import cStringIO
import xml.etree.ElementTree as xml


app = Flask(__name__)
photos = UploadSet('uploads', IMAGES, default_dest=lambda x: 'uploads')
configure_uploads(app, (photos))
print app.config['SEND_FILE_MAX_AGE_DEFAULT']
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1
print app.config['SEND_FILE_MAX_AGE_DEFAULT']


@app.route('/')
def index():
    return render_template('ui.html')


@app.route('/start_download')
def start_download():
    tag = request.args.get('tag', 'olympics')
    return render_template('start_download', tag=tag)


@app.route('/upload', methods=['POST'])
def upload():
    filename = photos.save(request.files['file'])
    tag = request.form['flickr_tag']
    short_filename = 'uploads/' + os.path.splitext(filename)[0]
    return redirect('/make?filename=' + short_filename + '&set=' + tag)


@app.route('/download')
def download():
    tag = request.args.get('tag', 'olympics')
    number = 1
    search_results = []
    print 'Getting search results'
    for license in [1, 2, 3, 4, 5, 6, 7]:
        search_results += flickr.photos_search(tags=[tag], per_page=number,
          license=str(license))
    #search_results = flickr.photos_search(tags=[tag], per_page=number)
    if not os.path.isdir(folder + tag):
        os.mkdir(folder + tag)
    attributions = []
    for pic in search_results:
        # anything not 0 is CC or public domain
        # source: http://www.flickr.com/services/api/flickr.photos.licenses.getInfo.html
        #self.download_progress.set_text('Finding next CC image')
        #if pic.license == '0':
        #    continue
        try:
            url = pic.getURL(size='Square', urlType='source')
            image = urllib.URLopener()
            image.retrieve(url, folder + tag + '/' +
              os.path.basename(urlparse.urlparse(url).path))
            print 'Downloading', url
        except:
            continue
        attributions.append([folder + tag + '/' + os.path.basename(
          urlparse.urlparse(url).path), pic.owner.username])
    f = open(folder + tag + '/attributions.csv', 'a')
    writer = csv.writer(f, delimiter=',')
    writer.writerows(attributions)
    f.close()
    return 'Done'


@app.route('/make')
def make_image():
    filename = request.args.get('filename', '')
    short_filename = os.path.splitext(os.path.basename(
      filename))[0]
    image_set = request.args.get('set', 'olympics')
    return render_template('make.html', filename=filename, image_set=image_set,
      short_filename=short_filename)


@app.route('/actually_make_the_thing')
def actually_make_the_thing():
    filename = request.args.get('filename', '')
    image_set = request.args.get('set', 'olympics')
    print image_set
    os.system('python average_colour.py ' + filename + '.jpg ' + image_set)
    return 'Done done done'


@app.route('/view')
def view():
    filename = request.args.get('filename', 'done')
    print filename
    return render_template(filename + '_done.html')


@app.route('/imgur')
def imgur():
    filename = request.args.get('filename', '')
    print filename
    response = cStringIO.StringIO()
    c = pycurl.Curl()
    values = [('key', 'bce0bef7f42fcdd9e0cadac633499e5b'),
      ("image", (c.FORM_FILE, 'static/' + str(filename) + '_done.jpg'))]
    c.setopt(c.URL, "http://api.imgur.com/2/upload.xml")
    c.setopt(c.HTTPPOST, values)
    c.setopt(c.WRITEFUNCTION, response.write)
    c.perform()
    c.close()
    xml_doc = xml.parse(cStringIO.StringIO(response.getvalue()))
    root = xml_doc.getroot()
    print root.find('.//imgur_page').text
    return redirect(root.find('.//imgur_page').text)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
