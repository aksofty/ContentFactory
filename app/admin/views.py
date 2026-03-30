from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from app.models import *

class BaseView(ModelView):
    list_columns = ['id', 'name']


class TargetTgView(BaseView):
    datamodel = SQLAInterface(TargetTg) 
    list_columns = BaseView.list_columns + ['is_active']

    add_columns = edit_columns = [
        'is_active', 'name', 'source', 'channel'
    ]
   
class SourceRssView(BaseView):
    datamodel = SQLAInterface(SourceRss) 
    list_columns = BaseView.list_columns + ['is_active']
    add_columns = edit_columns = [
        'is_active', 'name', 'url', 'cron', 'parse_link', 'limit', 'allowed_filter', 'forbidden_filter', 'ai_prompt', 'reverse', 'last_post_url'
    ]

    
class SourceTgView(BaseView):
    datamodel = SQLAInterface(SourceTg) 
    list_columns = ['is_active'] + BaseView.list_columns
    add_columns = edit_columns = [
        'is_active', 'name', 'channel', 'cron', 'repost', 'drop_author', 'limit', 'allowed_filter', 'forbidden_filter', 'ai_prompt', 'last_message_id'
    ]



class FilterView(BaseView):
    datamodel = SQLAInterface(Filter)


class AIPromtView(BaseView):
    datamodel = SQLAInterface(AIPrompt)
