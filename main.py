#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from django.utils import simplejson
from google.appengine.api import users

class Sign(db.Model):
  two_digit_id = db.StringProperty()
  name         = db.StringProperty()
  changed      = db.BooleanProperty()
  message      = db.StringProperty(multiline=True)
  default_msg  = db.StringProperty(multiline=True)
  who          = db.UserProperty()
  when         = db.DateTimeProperty(auto_now=True)

class Log(db.Model):
  two_digit_id = db.StringProperty()
  name         = db.StringProperty()
  message      = db.StringProperty(multiline=True)
  who          = db.UserProperty()
  when         = db.DateTimeProperty(auto_now=True)

class MainHandler(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url('/'))
    else:
      signs = Sign.all().fetch(100)
      self.response.out.write(template.render('templates/list.html', locals()))      

  def post(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url('/'))
    else:
      for k in self.request.arguments():
        s = Sign.get(k)
        newmessage = self.request.get(k)
        if newmessage != s.message:
          s.message = newmessage
          s.who = user
          s.changed = True
          s.put()
          log = Log(message=newmessage,who=user,name=s.name,two_digit_id=s.two_digit_id)
          log.put()
        self.redirect('/')

class ApiHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write(simplejson.dumps([{"two_digit_id":m.two_digit_id,"name":m.name,"message":m.message} for m in Sign.all().filter("changed ==",True)]))
    for m in Sign.all().filter("changed == ",True).fetch(100):
      m.changed = False
      m.put()

class ApiAllHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write(simplejson.dumps([{"two_digit_id":m.two_digit_id,"name":m.name,"message":m.message} for m in Sign.all()]))

class ResetHandler(webapp.RequestHandler):
  def get(self):
    for m in Sign.all().fetch(100):
      m.message = m.default_msg
      m.changed = True
      m.who = None
      m.put()
    self.response.out.write("OK")

class CreateHandler(webapp.RequestHandler):
  def get(self):
    for m in Sign.all().fetch(100):
      m.delete()
    s = Sign(changed=True,name="Lobby Left",two_digit_id="04",default_msg="Welcome to\r\nHacker Dojo")
    s.put()
    s = Sign(changed=True,name="Lobby Center",two_digit_id="30",default_msg="Welcome")
    s.put()
    s = Sign(changed=True,name="Lobby Right",two_digit_id="05",default_msg="Please sign in\r\nEnjoy your visit")
    s.put()
    s = Sign(changed=True,name="140B",two_digit_id="40",default_msg="140B")
    s.put()
    s = Sign(changed=True,name="Savanna",two_digit_id="03",default_msg="Savanna")
    s.put()
    self.response.out.write("OK")
    
def main():
   application = webapp.WSGIApplication([('/', MainHandler),('/api', ApiHandler),('/api/all', ApiAllHandler),('/reset', ResetHandler),('/create', CreateHandler)], debug=True)
   util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
