# -*- coding: utf8 -*-
import logging
import os
import urllib 
from google.appengine.ext.webapp import template

import cgi
import wsgiref.handlers
from google.appengine.ext import db

from google.appengine.api import users
from google.appengine.ext import webapp

from urllib import unquote
from django.utils import simplejson

class Video(db.Model):
    title = db.StringProperty()
    ytid = db.StringProperty()
    section = db.StringProperty()
    transcript = db.TextProperty()
    words = db.TextProperty()
    times = db.StringProperty()
    time_added = db.DateTimeProperty(auto_now_add=True)
    approved = db.BooleanProperty(default=False)
    time_formated = db.StringProperty()

class Language(db.Model):
    code = db.StringProperty()
    dict_link = db.StringProperty()
    translate_to_default = db.StringProperty()

class Section(db.Model):
    name = db.StringProperty()
    language = db.ReferenceProperty(Language)
    first = db.ReferenceProperty(Video)
    feed = db.StringProperty()

class Word(db.Model):
    entry = db.StringProperty()
    definition = db.StringProperty()
    details = db.StringProperty()
    
class MainPage(webapp.RequestHandler):
    def get(self):

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path,{}))

class FormLine():
    def __init__(self,l={}):
        self.text = l.get('text','Description')
        self.type = l.get('type','text')
        self.size = l.get('size','40')
        self.name = l.get('name','')
        self.value = l.get('value','')
        self.values = l.get('values',[])

class NewForm(webapp.RequestHandler):
    def get(self,kind):
        require_language = ['section','words']
        require_section = ['video']
        language_codes = ['']
        sections = ['']

        if kind in require_language:
            query = Language.all()
            query.order('code')
            languages = query.fetch(200)
            if languages:
                for l in languages:
                    language_codes.append(str(l.code))

        if kind in require_section:
            query = Section.all()
            query.order('name')
            results = query.fetch(200)
            if results:
                for s in results:
                    sections.append(str(s.name))

        lines = {
                'language' :
                    [
                        FormLine({'name':'code','text':'Language code'}),
                        FormLine({'name':'dict_link','text':'Dictionary link'}),
                        FormLine({'name':'translate_to_default','text':'Translate to by default'}),
                    ],
                'section' :
                    [
                     FormLine({'text':'Section name','name':'section'}),
                     FormLine({'text':'Feed URL','name':'feed'}),
                     FormLine(
                         {'type':'select',
                          'values':language_codes,'text':'Language',
                          'name':'code'}
                     ),
                    ],
                'video' :
                    [
                     FormLine({'text':'Title','name':'title'}),
                     FormLine({'text':'ytid','name':'ytid'}),
                     FormLine(
                         {'type':'select',
                          'values':sections,'text':'Section',
                          'name':'section'}
                     ),
                    ],
                'words' :
                    [
                        FormLine({'text':'Text','type':'textarea'}),
                        FormLine({'text':'Language'}),
                    ],
                }.get(kind,{})

        template_values = {
                'kind' : kind,
                'lines' : lines,
        }

        path = os.path.join(os.path.dirname(__file__), 'submit_new.html')
        self.response.out.write(template.render(path, template_values))

class RequestBackupFile(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'request_backup_file.html')
        self.response.out.write(template.render(path, {}))

class SubmitNew(webapp.RequestHandler):
    def submit_language(self):
        code = self.request.get('code').strip()
        translate_to_default = self.request.get('translate_to_default').strip()
        dict_link = self.request.get('dict_link').strip()
        if code:
            query = db.GqlQuery("SELECT * FROM Language WHERE code = :1 ", code)
            if not query.fetch(1):
                l = Language()
                l.code = code
                l.dict_link = dict_link
                l.translate_to_default = translate_to_default
                l.put()
                message = 'created language "'+l.code+'"<br/>dictionary link "' + l.dict_link + '"<br/>translate to "' + l.translate_to_default +'"'
            else:
                message = '"%s" -- such language code exists' % code 
        else:
            message = 'no language code is entered'
        return message

    def submit_section(self):
        language = self.request.get('code').strip()
        feed = self.request.get('feed').strip()
        language = Language.all().filter('code =',language).fetch(1)[0]
        section_name = self.request.get('section').strip()
        if not language:
            return 'no language is specified'
        if section_name:
            query = db.GqlQuery("SELECT * FROM Section WHERE name = :1 ", section_name)
            if not query.fetch(1):
                s = Section() 
                s.language = language
                s.feed = feed
                s.name = section_name
                s.put()
                message = 'section with language "%s" and name "%s" is added' % (language.code,section_name)
            else:
                message = '"%s" -- such section exists' % section_name
        else:
            message = 'no section name is entered'
        return message

    def submit_video(self):
        section = self.request.get('section').strip()
        title = self.request.get('title').strip()
        ytid = self.request.get('ytid').strip()
        if not section:
            return 'no section is specified'    
        if 'http://' in ytid:
            # start and end for parcing
            s = ytid.find('v=')
            if s > 0:
                e = ytid.find('&',s)
                if e > 0:
                    ytid = ytid[s+2:e]
                else:
                    ytid = ytid[s+2:]
            else:
                return 'Sorry. YouTube ID cannot be extracted from this URL.'

        if ytid:
            query = db.GqlQuery("SELECT * FROM Video WHERE ytid = :1 ", ytid)
            if not query.fetch(1):
                v = Video()
                v.title = title
                v.ytid = ytid
                v.section = section
                v.put()
                message = \
                'video with title "%s"<br/>ytid "%s"<br/>is added to section "%s"' % (title,ytid,section)
            else:
                message = '"%s" -- such ytid exists' % ytid
        else:
            message = 'no ytid is specified'
        return message

    def post(self,kind):

        message = { 
                'language' : self.submit_language,
                'section' : self.submit_section,
                'video' : self.submit_video,
                }[kind]()
        
        self.redirect('/admin?m=%s' % message)

class UpdateOld(webapp.RequestHandler):
    def update_language(self):
        code = self.request.get('code').strip()
        translate_to_default = self.request.get('translate_to_default').strip()
        dict_link = self.request.get('dict_link').strip()
        if code:
            query = db.GqlQuery("SELECT * FROM Language WHERE code = :1 ", code)
            l = query.fetch(1)
            if l:
                l = l[0]
                l.dict_link = dict_link
                l.translate_to_default = translate_to_default
                l.put()
                message = 'updated language "'+l.code+'"<br/>dictionary link "' + l.dict_link + '"<br/>translate to "' + l.translate_to_default +'"'
            else:
                message = '"%s" -- such language code exists' % code 
        else:
            message = 'no language code is specified'
        return message

    def update_section(self):
        section_name = self.request.get('section').strip()
        feed = self.request.get('feed').strip()
        if section_name:
            query = db.GqlQuery("SELECT * FROM Section WHERE name = :1 ", section_name)
            s = query.fetch(1)
            if s:
                s = s[0]
                s.feed = feed
                s.put()
                message = 'section "%s" updated<br/>language "%s"<br/>feed: "%s"' % (section_name,s.language.code,feed)
            else:
                message = 'section "%s" does not exist' % section_name
        else:
            message = 'no section name is entered'
        return message

    def update_video(self):
        section = self.request.get('section').strip()
        title = self.request.get('title').strip()
        ytid = self.request.get('ytid').strip()
        if not section:
            return 'no section is specified'    
        if 'http://' in ytid:
            # start and end for parcing
            s = ytid.find('v=')
            if s > 0:
                e = ytid.find('&',s)
                if e > 0:
                    ytid = ytid[s+2:e]
                else:
                    ytid = ytid[s+2:]
            else:
                return 'Sorry. YouTube ID cannot be extracted from this URL.'

        if ytid:
            query = db.GqlQuery("SELECT * FROM Video WHERE ytid = :1 ", ytid)
            v = query.fetch(1)
            if v:
                v = v[0]
                v.title = title
                v.section = section
                v.put()
                message = \
                'updated video<br/>title "%s"<br/>ytid "%s"<br/>section "%s"' % (title,ytid,section)
            else:
                message = 'this ytid does not exist' % ytid
        else:
            message = 'no ytid is specified'
        return message

    def post(self,kind):
        message = { 
                'language' : self.update_language,
                'video' : self.update_video,
                'section' : self.update_section,
                }[kind]()
        message = urllib.quote(message.encode('utf8'))
        self.redirect('/admin?m=%s' % message)

class ProcessBackup(webapp.RequestHandler):
    def post(self):

        text = self.request.get('backup_file')
        overwrite = self.request.get('overwrite')
        if overwrite == 'true':
            overwrite = True
        else:
            overwrite = False
        
        from xml.etree.cElementTree import fromstring
        tree = fromstring(text)

        section = tree.findtext('name')

        total_counter = 0
        not_overwritten_counter = 0
        overwritten_counter = 0
        new_counter = 0

        for video_entry in tree.findall('video'):
            ytid = video_entry.findtext('ytid')
            v = Video.all().filter('ytid =',ytid).fetch(1)
            if v:
                v = v[0]
                # overwrite
                if overwrite:
                    for el in video_entry.getiterator():
                        if el.tag == 'time_added' and not el.text == 'None':
                            import time, datetime
                            time_format = "%Y-%m-%d %H:%M:%S"
                            value_str = el.text[:el.text.find('.')]
                            value = datetime.datetime.fromtimestamp(time.mktime(time.strptime(value_str, time_format)))
                            v.__setattr__(el.tag,value)
                        elif not el.text == 'None':
                            v.__setattr__(el.tag,el.text)
                    v.put()
                    overwritten_counter += 1
                # do not overwrite
                else:
                    not_overwritten_counter += 1
            # create
            else:
                v = Video()
                for el in video_entry.getiterator():
                    if el.tag == 'time_added' and not el.text == 'None':
                        import time, datetime
                        time_format = "%Y-%m-%d %H:%M:%S"
                        value_str = el.text[:el.text.find('.')]
                        value = datetime.datetime.fromtimestamp(time.mktime(time.strptime(value_str, time_format)))
                        v.__setattr__(el.tag,value)
                    elif not el.text == 'None':
                        v.__setattr__(el.tag,el.text)
                v.section = section
                v.put()

                new_counter += 1
            total_counter += 1

        out = '<b>videos parsed</b><br/>'
        out += 'total: %d<br/>' % total_counter
        out += 'overwritten: %d<br/>' % overwritten_counter
        out += 'NOT overwritten: %d<br/>' % not_overwritten_counter
        out += 'new: %d<br/>' % new_counter

        self.redirect('/admin?m=%s' % out)

class SubmitTranscript(webapp.RequestHandler):
    def get(self,ytid):

        query = db.GqlQuery("SELECT * FROM Video WHERE ytid = :1", ytid)
        video = query.fetch(1)
        if video:
            v = video[0]
            t = v.transcript
            w = v.words
            times = v.times
        else:
            t = ''

        template_values = {
            'ytid' : ytid,
            'transcript' : t,
            'words' : w,
            'times' : times,
        }

        path = os.path.join(os.path.dirname(__file__), 'submit_transcript.html')
        self.response.out.write(template.render(path, template_values))

# /google-appengine-docs-20081003/appengine/articles/rpc.htmlclass RPCHandler(webapp.RequestHandler):
class RPCHandler(webapp.RequestHandler):

    """ Allows the functions defined in the RPCMethods class to be RPCed."""
    def __init__(self):
        webapp.RequestHandler.__init__(self)
        self.methods = RPCMethods()

    def post(self):
        args = simplejson.loads(self.request.body)
        func, args = args[0], args[1:]

        if func[0] == '_':
            self.error(403) # access denied
            return
     
        func = getattr(self.methods, func, None)
        if not func:
            self.error(404) # file not found
            return

        result = func(*args)
        self.response.out.write(simplejson.dumps(result))

class RPCMethods:
    """ Defines the methods that can be RPCed.
    NOTE: Do not allow remote callers access to private/protected "_*" methods.
    """
    
    def SubmitVideo(self, *args):
    # The JSON encoding may have encoded integers as strings.
    # Be sure to convert args to any mandatory type(s).
        ytid = args[0]
        if 'http://' in ytid:
            # start and end for parcing
            s = ytid.find('v=')
            if s > 0:
                e = ytid.find('&',s)
                if e > 0:
                    ytid = ytid[s+2:e]
                else:
                    ytid = ytid[s+2:]
            else:
                return 'Sorry. YouTube ID cannot be extracted from this URL.'

        # check if such video exists
        query = db.GqlQuery("SELECT * FROM Video WHERE ytid = :1 ", ytid)
        videos = query.fetch(1)
        if videos:
            return 'Video with YouTube ID <a href="/video/%s">%s</a> was added before.' % (ytid,ytid)

        dance_type = args[1]
        title = args[2]

        video = Video()
        video.ytid = ytid.strip()
        video.dance_type = dance_type
        video.title = title
        video.needs_moderation = True
        video.put()

        return """Thank you! The video with YTID "%s" will be posted after
moderation.<br/>Meanwhile you may <a href="/in_moderation/video/%s">watch it</a> with non-moderated moves.""" \
        % (ytid,ytid)

    def SubmitTranscript(self, *args):
    # The JSON encoding may have encoded integers as strings.
    # Be sure to convert args to any mandatory type(s).
        ytid = args[0]
        transcript = args[1]
        times = args[2]

        # check if such video exists
        query = db.GqlQuery("SELECT * FROM Video WHERE ytid = :1 ", ytid)
        videos = query.fetch(1)
        if videos:
            v = videos[0]
            v.transcript = transcript
            v.times = times
            v.put()

        return """Transcript is updated. Length: %d symbols""" % (len(transcript))

    def SubmitWords(self, *args):
    # The JSON encoding may have encoded integers as strings.
    # Be sure to convert args to any mandatory type(s).
        ytid = args[0]
        words = args[1]

        # check if such video exists
        query = db.GqlQuery("SELECT * FROM Video WHERE ytid = :1 ", ytid)
        videos = query.fetch(1)
        if videos:
            v = videos[0]
            v.words = words 
            v.put()

        return """Words are updated. Length: %d symbols""" % (len(words))

class AdminMain(webapp.RequestHandler):
    def get(self):

        querry = Section.all()
        sections = querry.fetch(1000)

        querry = Language.all()
        languages = querry.fetch(1000)

        message = self.request.get('m')
        logout_link = "<a href=\"%s\">Logout</a>" % users.create_logout_url("/")
        template_values = {
                'logout_link' : logout_link,
                'message' : message,
                'sections' : sections,
                'languages' : languages,
                }
        path = os.path.join(os.path.dirname(__file__), 'admin.html')
        self.response.out.write(template.render(path, template_values))

class MakeFirst(webapp.RequestHandler):
    def get(self,section,video):

        querry_section = Section.all().filter('name =',section)
        section_object = querry_section.fetch(1)[0]
        querry_video = Video.all().filter('ytid =',video)
        video_object = querry_video.fetch(1)[0]
        section_object.first = video_object
        section_object.put()

        self.redirect('/admin/edit/section/%s' % section)

class ApproveVideo(webapp.RequestHandler):
    def get(self,pre,section,video):

        logging.debug('section = '+section)
        logging.debug('video = '+video)
        querry = Video.all().filter('ytid =',video)
        video = querry.fetch(1)[0]
        logging.debug('pre ='+pre)
        if pre == 'dis':
            video.approved = False
        else:
            video.approved = True
        video.put()

        logging.debug('video.approved = '+str(video.approved))

        self.redirect('/admin/edit/section/%s' % section)

class EditSection(webapp.RequestHandler):
    def get(self,section):

        querry = Video.all().order('-time_added').filter('section =',section)
        videos = querry.fetch(1000)

        querry_section = Section.all().filter('name =',section)
        section = querry_section.fetch(1)[0]

        lines = [ 
                  FormLine({'name':'feed',
                      'text':'Feed URL:',
                            'value':section.feed}),
                ]

        template_values = {
                'section' : section,
                'videos' : videos,
                'lines' : lines,
                }

        path = os.path.join(os.path.dirname(__file__), 'edit_section.html')
        self.response.out.write(template.render(path, template_values))

class EditLanguage(webapp.RequestHandler):
    def get(self,language):

        language = Language.all().filter('code =',language).fetch(1)[0]

        sections = Section.all().filter('language =',language.key()).fetch(1000)

        lines = [ 
                  FormLine({'name':'dict_link', 'text':'Dictionary link:', 'value':language.dict_link}),
                  FormLine({'name':'translate_to_default','text':'Translate to by default','value':language.translate_to_default}),
                ]

        template_values = {
                'language' : language,
                'sections' : sections,
                'lines' : lines,
                }

        path = os.path.join(os.path.dirname(__file__), 'edit_language.html')
        self.response.out.write(template.render(path, template_values))

class EditVideo(webapp.RequestHandler):
    def get(self,ytid):

        v = Video.all().filter('ytid =',ytid).fetch(1)[0]

        sections = ['']
        query = Section.all()
        query.order('name')
        results = query.fetch(200)
        if results:
            for s in results:
                sections.append(str(s.name))

        lines = [
                FormLine({'text':'Title','name':'title','value':v.title}),
                FormLine(
                         {'type':'select',
                          'values':sections,'text':'Section',
                          'name':'section'}
                     ),
                ]

        template_values = {
                'sections' : sections,
                'lines' : lines,
                'v' : v,
                }

        path = os.path.join(os.path.dirname(__file__), 'edit_video.html')
        self.response.out.write(template.render(path, template_values))

class Backup(webapp.RequestHandler):
    """
    Generates backup xml file
    """
    def get(self,section):

        query = Video.all().filter('section =',section)
        results = query.fetch(1000)

        section_query = Section.all().filter('name =',section)
        section_result = section_query.fetch(1)[0]

        self.response.headers['Content-Type'] = 'file/xml'
        template_values = { 'videos' : results, 'section' : section_result }
        path = os.path.join(os.path.dirname(__file__), 'backup.xml')
        self.response.out.write(template.render(path, template_values))

class SectionVideos(webapp.RequestHandler):
    def get(self,section):

        querry = Video.all().order('time_added').filter('section =',section).filter('approved =',True)
        videos = querry.fetch(1000)

        section = Section.all().filter('name =',section).fetch(1)[0]

        # make section title case
        section_title = section.name.title()

        template_values = {
                'section' : section,
                'section_title' : section_title,
                'videos' : videos,
                }

        path = os.path.join(os.path.dirname(__file__), 'section_videos.html')
        self.response.out.write(template.render(path, template_values))

class SectionOrNotFound(webapp.RequestHandler):
    def get(self,section):

        section_query = Section.all().filter('name =',section)
        section_result = section_query.fetch(1)

        if section_result:
            section = section_result[0]
            v = section.first

            if v:
                t = v.transcript.replace('\n','/\\\n')
                w = v.words.replace('\n','/\\\n')
                ytid = v.ytid
                times = v.times
                if v.title:
                    title = v.title
                else:
                    title = ''

            logging.debug('link = %s' % section.language.dict_link )

            template_values = {
                'section' : section,
                'section_title' : section.name.title(),
                'title' : title,
                'ytid' : ytid,
                'transcript' : t,
                'words' : w,
                'times' : times,
                'dict_link' : section.language.dict_link,
            }

            path = os.path.join(os.path.dirname(__file__), 'section.html')
            self.response.out.write(template.render(path, template_values))
        else:
            template_values = {}
            path = os.path.join(os.path.dirname(__file__), '404.html')
            self.response.out.write(template.render(path, template_values))

class SectionFeed(webapp.RequestHandler):
    def get(self,section):

        from rfc3339 import rfc3339

        querry = Video.all().order('-time_added').filter('section =',section).filter('approved =',True)
        videos = querry.fetch(1000)

        section_title = section.title()

        last_time = rfc3339(videos[0].time_added,utc=True)

        for v in videos:
            v.time_formated = rfc3339(v.time_added,utc=True)

        self.response.headers['Content-Type'] = 'file/xml'
        template_values = {
                'section' : section,
                'section_title' : section_title,
                'videos' : videos,
                'last_time' : last_time,
                }

        path = os.path.join(os.path.dirname(__file__), 'feed.xml')
        self.response.out.write(template.render(path, template_values))

class ViewVideo(webapp.RequestHandler):
    def get(self,section,ytid):

        v = Video.all().filter('ytid =',ytid).fetch(1)
        section = Section.all().filter('name =',section).fetch(1)[0]

        if v:
            v = v[0]
            t = v.transcript.replace('\n','/\\\n')
            w = v.words.replace('\n','/\\\n')
            ytid = v.ytid
            times = v.times
            if v.title:
                title = v.title
            else:
                title = ''

        template_values = {
            'section' : section,
            'section_title' : section.name.title(),
            'title' : title,
            'ytid' : ytid,
            'transcript' : t,
            'words' : w,
            'times' : times,
            'dict_link' : section.language.dict_link,
        }

        path = os.path.join(os.path.dirname(__file__), 'section.html')
        self.response.out.write(template.render(path, template_values))

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication(
                                       [('/', MainPage),
                                        ('/submit_transcript/(.*)',SubmitTranscript), 
                                        ('/rpc', RPCHandler),
                                        ('/admin', AdminMain),
                                        ('/admin/new_(.*)', NewForm),
                                        ('/admin/submit_new_(.*)', SubmitNew),
                                        ('/admin/update_old_(.*)', UpdateOld),
                                        ('/admin/request_backup_file', RequestBackupFile),
                                        ('/admin/process_backup', ProcessBackup),
                                        ('/admin/backup/section/(.*).xml', Backup),
                                        ('/admin/edit/section/(.*)/first/(.*)', MakeFirst),
                                        ('/admin/(.*)approve/section/(.*)/video/(.*)', ApproveVideo),
                                        ('/admin/edit/section/(.*)', EditSection),
                                        ('/admin/edit/language/(.*)', EditLanguage),
                                        ('/admin/edit/video/(.*)', EditVideo),
                                        ('/(.*)/videos', SectionVideos),
                                        ('/(.*)/video/(.*)', ViewVideo),
                                        ('/(.*)/feed', SectionFeed),
                                        ('/(.*)', SectionOrNotFound),
                                        ],
                                       debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
