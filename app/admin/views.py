import os
from flask import request
from flask_appbuilder import BaseView, ModelView, expose, has_access
from flask_appbuilder.models.sqla.interface import SQLAInterface
from app.models import *

class BaseViewFields(ModelView):
    list_columns = ['id', 'name']


class TargetTgView(BaseViewFields):
    datamodel = SQLAInterface(TargetTg) 
    #list_columns = BaseView.list_columns + ['is_active']

    add_columns = edit_columns = [
        'is_active', 'name', 'source', 'channel'
    ]
class TargetVkView(BaseViewFields):
    datamodel = SQLAInterface(TargetVK) 
    #list_columns = BaseView.list_columns + ['is_active']

    add_columns = edit_columns = [
        'is_active', 'name', 'source', 'channel'
    ]
   
class SourceRssView(BaseViewFields):
    datamodel = SQLAInterface(SourceRss) 
    #list_columns = BaseView.list_columns + ['is_active']
    add_columns = edit_columns = [
        'is_active', 'name', 'url', 'cron', 'parse_link', 'limit', 'allowed_filter', 'forbidden_filter', 'ai_prompt', 'reverse', 'last_post_url'
    ]

    
class SourceTgView(BaseViewFields):
    datamodel = SQLAInterface(SourceTg) 
    #list_columns = ['is_active'] + BaseView.list_columns
    add_columns = edit_columns = [
        'is_active', 'name', 'channel', 'cron', 'repost', 'drop_author', 'limit', 'allowed_filter', 'forbidden_filter', 'ai_prompt', 'last_message_id'
    ]

class FilterView(BaseViewFields):
    datamodel = SQLAInterface(Filter)
    edit_template = 'tags.html'

class AIPromtView(BaseViewFields):
    datamodel = SQLAInterface(AIPrompt)

class LogView(BaseView):
    route_base = "/logs"
    default_view = 'show_logs'

    @expose('/show/')
    @has_access
    def show_logs(self):
        log_file = "app/logs/all_logs.log"
        
        if os.path.exists(log_file):
            try:
                with open(log_file, "r") as f:
                    lines = f.readlines()
                    content_list = lines[-200:]
                    content = "".join(content_list)
            except Exception as e:
                content = f"Error reading log file: {str(e)}"
        else:
            content = "Log file does not exist at the specified path."

        if request.args.get('raw'):
            return content

        return self.render_template('logs.html', content=content.strip())
