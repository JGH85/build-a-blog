#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                                autoescape = True)





class Blogpost(db.Model):
    title = db.StringProperty(required=True)
    blogpost = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


#Hacker version extras:
def get_posts(limit, offset):
    # TODO: query the database for posts, and return them
    gposts = db.GqlQuery("select * from Blogpost order by created desc LIMIT " + str(limit) + "OFFSET " + str(offset))
    return gposts

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect("/blog")

class BlogHandler(webapp2.RequestHandler):
    def render_front(self, title="", blogpost="", error="", blogposts="", numofpages='',
                        next='', prev = '', nextlink='', prevlink=''):
        t = jinja_env.get_template("mainpage.html")
        #blogposts = db.GqlQuery("select * from Blogpost order by created desc LIMIT 5")

        #create GET request to draw certain number of blogposts per page
        pagenum = 1
        try:
            pagenum = int(self.request.GET["page"])
        except KeyError:
            pass
        itemsperpage = 5
        offsetnum = (pagenum-1)*itemsperpage
        blogposts = get_posts(itemsperpage, offsetnum)

        #setup page controllers: previous and next, and numbered links to results pages.
        #first get all the numbers needed: items on page, items per page, total number of posts, number of pages.
        itemsonpage = blogposts.count(offset=offsetnum, limit=itemsperpage)
        totalposts = blogposts.count(offset=0)
        #calculate num of pages, and convert to range for use in jinja
        if totalposts % itemsperpage == 0:
            numofpages = totalposts//itemsperpage
        else:
            numofpages = totalposts//itemsperpage + 1
        numofpagesrange = range(1,numofpages+1)

        #if firstpage, then no previous:
        FirstPageTest = False
        prev = "< Prev "
        prevlink = "/blog?page="+str(pagenum-1)
        if offsetnum == 0:
            FirstPageTest = True

        #if last page, no next
        next = " Next >"
        nextlink = "/blog?page="+str(pagenum + 1)
        #calculate whether it is last page
        LastPageTest = False
        if itemsonpage < itemsperpage:
            LastPageTest = True
        if pagenum == numofpages:
            LastPageTest = True

        #make both variables blank as appropriate
        if FirstPageTest:
            prev = ''
        if LastPageTest:
            next = ''

        response = t.render(title=title, blogpost=blogpost, error = error, blogposts = blogposts,
        numofpages=numofpagesrange, next = next, prev = prev, prevlink = prevlink, nextlink = nextlink)
        self.response.write(response)

    def get(self):
        self.render_front()


class newPostHandler(webapp2.RequestHandler):
    def render_front(self, title="", blogpost="", error="", blogposts=""):
        t = jinja_env.get_template("newpage.html")
        #blogposts = db.GqlQuery("select * from Blogpost order by created desc LIMIT 5")
        response = t.render(title=title, blogpost=blogpost, error = error, blogposts = blogposts)
        self.response.write(response)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        blogpost = self.request.get("blogpost")

        if title and blogpost:
            b = Blogpost(title = title, blogpost = blogpost)
            b.put()
            perm = str(b.key().id())
            self.redirect("/blog/"+ perm)
        else:
            error = "we need both a title and some content!"
            self.render_front(title, blogpost, error)


class ViewPostHandler(webapp2.RequestHandler):
    """handler that writes a single post"""

    def render_front(self, singlepost=""):
        t = jinja_env.get_template("permalink.html")
        response = t.render(singlepost=singlepost)
        self.response.write(response)

    #todo check for error in id # and return error page instead


    def get(self, id):
        id = int(id)
        singlepost = Blogpost.get_by_id(id)
        self.render_front(singlepost)


#fix redirect from / to /blog






app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', BlogHandler),
    ('/blog/newpost', newPostHandler),
    webapp2.Route(r'/blog/<id:\d+>', ViewPostHandler)
], debug=True)
