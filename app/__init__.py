from flask import Flask,request, url_for
from app.db_connector import Db


db = Db()


def init_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.connect_db(app)
    
    from .main import main_blueprint
    from .geolocation import geolocation_blueprint
    from .notifications import notifications_blueprint
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(geolocation_blueprint)
    app.register_blueprint(notifications_blueprint)
    
    app.jinja_env.globals['url_for_other_page'] = url_for_other_page
    
    if not app.config['DEBUG'] and not app.config['TESTING']:
        import logging
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(app.config['LOGFILE'], maxBytes=(1048576*5), backupCount=7)
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)
        
    return app


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
