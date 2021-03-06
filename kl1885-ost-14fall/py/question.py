import webapp2, datetime, time, py.homepage as homepage, py.jinjaprint as jinjaprint, py.utility as utility
from py.datamodel import *
import py.vote as vote
from google.appengine.api import users
from google.appengine.ext import ndb

def put_question(self, createnew):
    current_user = users.get_current_user()
    submit=self.request.get("submit")
    if not current_user:
        jinjaprint.return_message(self, jinjaprint.MESSAGE_LOGIN_FIRST)
    else:
        if submit.lower() == "cancel":
            self.redirect(jinjaprint.URL_QUESTION)
        elif submit.lower() == "submit":
            q_content=unicode(self.request.get("qcontent"))
            q_title=unicode(self.request.get("qtitle"))
            tag_string=unicode(self.request.get("qtags"))
            jinjaprint.header(self,jinjaprint.TITLE_CREATE_Q)
            jinjaprint.left_nav(self)

            if utility.check_string_empty(q_title):
                jinjaprint.return_message(self, jinjaprint.MESSAGE_EMPTY_Q_TITLE)
            elif utility.check_string_empty(q_content):
                jinjaprint.return_message(self, jinjaprint.MESSAGE_EMPTY_Q_CONTENT)
            else:
                if createnew:
                    newQ=Question()
                    newQ.q_user=str(current_user)
                    newQ.q_content=q_content
                    newQ.q_tags=utility.tag_split(tag_string)
                    newQ.q_title=q_title
                    create_time=datetime.datetime.now()
                    newQ.create_time=create_time.replace(microsecond=0)
                    newQ.edit_time=create_time.replace(microsecond=0)
                    newQ.q_id=create_time.strftime("%s")
                    newQ.vd_num=0
                    newQ.vp_num=0
                    newQ.put()
                    templ_para={'link' : jinjaprint.URL_QUESTION_VIEW+"?qid="+newQ.q_id}
                    jinjaprint.return_message(self,jinjaprint.MESSAGE_SUCCEED_NEW_Q, templ_para)
                else:
                    qid=self.request.get('qid')
                    Qs=Question.get_by_qid(qid)
                    if len(Qs) == 0:
                        jinjaprint.return_message(self,jinjaprint.MESSAGE_NO_SUCH_QID+qid)
                    else:
                        editQ=Qs[0]
                        editQ.edit_time=datetime.datetime.now().replace(microsecond=0)
                        editQ.q_title=q_title
                        editQ.q_content=q_content
                        editQ.q_tags=utility.tag_split(tag_string)
                        editQ.put()
                        templ_para={'link' : jinjaprint.URL_QUESTION_VIEW+"?qid="+editQ.q_id}                                        
                        jinjaprint.return_message(self,jinjaprint.MESSAGE_SUCCEED_EDIT_Q, templ_para)

            jinjaprint.content_end(self)
            jinjaprint.footer(self)

class CreateQuestion(webapp2.RequestHandler):
    def get(self):
        jinjaprint.header(self,jinjaprint.TITLE_CREATE_Q)
        jinjaprint.left_nav(self)
        current_user = users.get_current_user()
        if not current_user:
            jinjaprint.return_message(self, jinjaprint.MESSAGE_LOGIN_FIRST)
        else:
            jinjaprint.create_question(self)

        jinjaprint.content_end(self)
        jinjaprint.footer(self)

    def post(self):
        put_question(self, True)


class EditQuestion(webapp2.RequestHandler):
    def get(self):
        jinjaprint.header(self,jinjaprint.TITLE_EDIT_Q)
        jinjaprint.left_nav(self)

        current_user = users.get_current_user()
        if not current_user:
            jinjaprint.return_message(self, jinjaprint.MESSAGE_LOGIN_FIRST)
        else:
            qid=self.request.get("qid")
            Q=Question.get_by_qid(str(qid))
            if len(Q) == 0:
                jinjaprint.return_message(self, jinjaprint.MESSAGE_NO_SUCH_QID+qid)
            elif str(Q[0].q_user) != str(current_user):
                jinjaprint.return_message(self, jinjaprint.MESSAGE_CANNOT_EDIT_Q)
            else:
                tag_string=utility.merge_tags(Q[0].q_tags)
                templ_para={'q':Q[0],'qtags': tag_string}
                jinjaprint.edit_question(self, templ_para)
        jinjaprint.content_end(self)
        jinjaprint.footer(self)

    def post(self):
        put_question(self, False)


class ViewFullQuestion(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        jinjaprint.header(self, jinjaprint.TITLE_VIEW_Q)
        jinjaprint.left_nav(self)
        jinjaprint.view_header(self, jinjaprint.HEADER_VIEW_Q)

        qid=self.request.get("qid")
        Q=Question.get_by_qid(str(qid))
        
        if len(Q) == 0:
                jinjaprint.return_message(self, jinjaprint.MESSAGE_NO_SUCH_QID+qid)
        else:
            q=Q[0]
            q.q_content=utility.replace_content(q.q_content)
            templ_para={'q': q, 'tag_mode': jinjaprint.MODE_TAG_ALL_Q, 
            'view_question_mode':True,
            'current_user':current_user}
            As = Answer.get_by_qid(str(qid))
            for a in As:
                a.a_content=utility.replace_content(a.a_content)
            jinjaprint.view_full_question(self, templ_para)
            templ_para['As']=As
            templ_para['current_user']=str(current_user)
            jinjaprint.view_question_answer(self,templ_para)
        jinjaprint.content_end(self)
        jinjaprint.footer(self)

    def post(self):
        vote.vote(self)


class ListQuestion(webapp2.RequestHandler):
    def get(self):
        page_num = self.request.get('page')
        tag=unicode(self.request.get('tag'))
        user=self.request.get("user")
        current_user = users.get_current_user()
        templ_para={"current_user":str(current_user)}
        max_page_num=0
        Qs=[]
        mine_mode = str(current_user) == str(user)

        jinjaprint.header(self,jinjaprint.TITLE_HOME)
        jinjaprint.left_nav(self)
        if user:
            if tag:
                Qs=Question.get_by_tag_user(tag, user)
                if mine_mode:
                    jinjaprint.view_header(self, jinjaprint.HEADER_LIST_TAG_Q_MINE+tag)
                else:
                    jinjaprint.view_header(self, jinjaprint.HEADER_LIST_OTHER_Q+user+" with tag: "+tag)
            else:
                Qs=Question.get_by_user(user)
                if mine_mode:
                    jinjaprint.view_header(self, jinjaprint.HEADER_LIST_MY_Q)
                else:
                    jinjaprint.view_header(self, jinjaprint.HEADER_LIST_OTHER_Q+user)
        else:
            if tag:
                Qs=Question.get_by_tag(tag)
                jinjaprint.view_header(self, jinjaprint.HEADER_LIST_TAG_Q_ALL+tag)
            else:
                Qs=Question.get_all()
                jinjaprint.view_header(self, jinjaprint.HEADER_LIST_ALL_Q)

        if page_num and not str(page_num).isdigit():
            jinjaprint.return_message(self, jinjaprint.MESSAGE_INVALID_PAGE_NUM)
        else:
            if not str(page_num):
                page_num=1
            else:
                page_num=int(page_num)

            max_page_num=utility.max_page_num(len(Qs))
            Qs=utility.split_element_by_page_num(Qs,page_num)
            for q in Qs:
                q.q_content=utility.replace_newline(q.q_content)
                
            if len(Qs) != 0:
                jinjaprint.page_num_temp(self, max_page_num, current_page=page_num)
            templ_para['Qs']=Qs
            jinjaprint.list_question(self, templ_para)
            if len(Qs) != 0:
                jinjaprint.page_num_temp(self, max_page_num, current_page=page_num)
            
            jinjaprint.content_end(self)
            jinjaprint.footer(self)

    def post(self):
        vote.vote(self)


app = webapp2.WSGIApplication([
     (jinjaprint.URL_QUESTION, ListQuestion)
    ,(jinjaprint.URL_QUESTION_LIST, ListQuestion)
    ,(jinjaprint.URL_QUESTION_CREATE, CreateQuestion)
    ,(jinjaprint.URL_QUESTION_VIEW, ViewFullQuestion)
    ,(jinjaprint.URL_QUESTION_EDIT, EditQuestion)
], debug=True)