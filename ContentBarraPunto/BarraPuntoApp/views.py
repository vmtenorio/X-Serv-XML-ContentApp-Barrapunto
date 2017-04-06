from django.shortcuts import render
from BarraPuntoApp.models import Page
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

#update
from xml.sax import make_parser
from urllib import request, error

# Create your views here.

content_bp = {}

from xml.sax.handler import ContentHandler

class myContentHandler(ContentHandler):

    def __init__ (self):
        self.inItem = False
        self.inContent = False
        self.theContent = ""
        self.titles = []
        self.links = []

    def startElement (self, name, attrs):
        if name == 'item':
            self.inItem = True
        elif self.inItem:
            if name == 'title':
                self.inContent = True
            elif name == 'link':
                self.inContent = True

    def endElement (self, name):
        if name == 'item':
            self.inItem = False
        elif self.inItem:
            if name == 'title':
                self.titles.append(self.theContent)
                self.inContent = False
                self.theContent = ""
            elif name == 'link':
                self.links.append(self.theContent)
                self.inContent = False
                self.theContent = ""

    def characters (self, chars):
        if self.inContent:
            self.theContent = self.theContent + chars


def show_bp():
    content = ""
    for k,v in content_bp.items():
        content += "<br/><li><a href='" + v + "'>" + k + "</a></li>"
    return content

@csrf_exempt
def cms_put(request, rec):
    if request.method == "GET":
        try:
            page = Page.objects.get(name=rec)
            resp = ("<!DOCTYPE html><html><body><div>" + page.page +
                    "</div><div><ul>" + show_bp() + "</ul></body></html>")
            return HttpResponse(resp)
        except ObjectDoesNotExist:
            return HttpResponse("Content not found", status=404)
    elif request.method == "PUT":
        page = Page(name=rec, page=request.body)
        page.save()
        return HttpResponse("Succesfully added page: " + rec)
    else:
        return HttpResponse("Method not allowed", status=405)

def update(req):
    theParser = make_parser()
    theHandler = myContentHandler()
    theParser.setContentHandler(theHandler)

    url = "http://barrapunto.com/index.rss"
    xmlStream = request.urlopen(url)
    theParser.parse(xmlStream)

    for i in range(len(theHandler.titles)):
        content_bp[theHandler.titles[i]] = theHandler.links[i]

    return HttpResponse("<!DOCTYPE html><html><body><h1>Content succesfully updated!</h1>" +
                        "<p>Pages are:</p><ul>" + show_bp() + "</ul></body></html>")
