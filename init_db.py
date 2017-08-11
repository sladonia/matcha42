#!/usr/bin/env python

from pymysql import *

def init_db(config):
    db = connect(host=config.SQL_HOST,
             user=config.SQL_USER,
             password=config.SQL_PASSWORD,
             charset='utf8mb4',
             cursorclass=cursors.DictCursor)
    sql = "CREATE DATABASE IF NOT EXISTS %s;"
    cursor = db.cursor()
    cursor.execute(sql % config.SQL_DB)


    sql = '''
      CREATE TABLE IF NOT EXISTS {0}.gender (
      id INT(4) NOT NULL AUTO_INCREMENT PRIMARY KEY,
      type VARCHAR(40) NOT NULL UNIQUE
      );
      INSERT IGNORE INTO {0}.gender(type) VALUES('male');
      INSERT IGNORE INTO {0}.gender(type) VALUES('female');
      
      CREATE TABLE IF NOT EXISTS {0}.preferences (
      id INT(4) NOT NULL AUTO_INCREMENT PRIMARY KEY,
      type VARCHAR(40) NOT NULL UNIQUE
      );
      INSERT IGNORE INTO {0}.preferences(type) VALUES('bi-sexual');
      INSERT IGNORE INTO {0}.preferences(type) VALUES('straight');
      INSERT IGNORE INTO {0}.preferences(type) VALUES('homosexual');
      
      CREATE TABLE IF NOT EXISTS {0}.users (
      id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
      token INT DEFAULT 0,
      login VARCHAR(80) NOT NULL,
      email VARCHAR(120) NOT NULL,
      new_email VARCHAR(120),
      passwd VARCHAR(1024) NOT NULL,
      first_name VARCHAR(80) NOT NULL,
      last_name VARCHAR(80) NOT NULL,
      activated INT(4) DEFAULT 0,
      last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
      date_of_birth DATE NOT NULL,
      sexuality INT(11) DEFAULT 10,
      biography TEXT,
      city TEXT,
      show_location INT(4) DEFAULT 0,
      gender INT(4),
      preferences INT(4),
      FOREIGN KEY (gender) REFERENCES {0}.gender(id),
      FOREIGN KEY (preferences) REFERENCES {0}.preferences(id)
      );
      

      CREATE TABLE IF NOT EXISTS {0}.interests (
      id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
      user_id INT(11) NOT NULL,
      interest VARCHAR(128) NOT NULL,
      FOREIGN KEY (user_id) REFERENCES {0}.users(id) ON DELETE CASCADE ON UPDATE CASCADE
      );
      
      CREATE TABLE IF NOT EXISTS {0}.photos (
      id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
      user_id INT(11) NOT NULL,
      photo_id INT(11) NOT NULL,
      path VARCHAR(256) NOT NULL,
      avatar INT(4) DEFAULT 0,
      FOREIGN KEY (user_id) REFERENCES {0}.users(id) ON DELETE CASCADE ON UPDATE CASCADE
      );
      
      CREATE TABLE IF NOT EXISTS {0}.notification_settings (
      id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
      user_id INT(11) NOT NULL,
      likes_me TINYINT(1) DEFAULT 1,
      unlikes_me TINYINT(1) DEFAULT 1,
      likes_me_back TINYINT(1) DEFAULT 1,
      viewed_my_profile TINYINT(1) DEFAULT 1,
      incoming_massage TINYINT(1) DEFAULT 1,
      FOREIGN KEY (user_id) REFERENCES {0}.users(id) ON DELETE CASCADE ON UPDATE CASCADE
      );
      
      CREATE TABLE IF NOT EXISTS {0}.visit_history (
      id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
      user_id INT(11) NOT NULL,
      other_user_id INT(11) NOT NULL,
      other_user_login VARCHAR(80) NOT NULL,
      url VARCHAR(256) NOT NULL,
      date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
      msg VARCHAR(120),
      FOREIGN KEY (user_id) REFERENCES {0}.users(id) ON DELETE CASCADE ON UPDATE CASCADE,
      FOREIGN KEY (other_user_id) REFERENCES {0}.users(id) ON DELETE CASCADE ON UPDATE CASCADE
      );
      
      CREATE TABLE IF NOT EXISTS {0}.blocked_users (
      user_id INT(11) NOT NULL,
      blocked_user_id INT(11) NOT NULL,
      PRIMARY KEY (user_id, blocked_user_id),
      FOREIGN KEY (user_id) REFERENCES {0}.users(id) ON DELETE CASCADE ON UPDATE CASCADE,
      FOREIGN KEY (blocked_user_id) REFERENCES {0}.users(id) ON DELETE CASCADE ON UPDATE CASCADE
      );
      
      CREATE TABLE IF NOT EXISTS {0}.fake_accounts (
      id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
      user_id INT(11) NOT NULL,
      fake_account_id INT(11) NOT NULL,
      date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES {0}.users(id) ON DELETE CASCADE ON UPDATE CASCADE,
      FOREIGN KEY (fake_account_id) REFERENCES {0}.users(id) ON DELETE CASCADE ON UPDATE CASCADE
      );
      
      CREATE TABLE IF NOT EXISTS {0}.chat (
      id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
      user_id INT(11) NOT NULL,
      receiver_id INT(11) NOT NULL,
      msg TEXT NOT NULL,
      date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
      seen TINYINT(1) DEFAULT 0,
      FOREIGN KEY (user_id) REFERENCES {0}.users(id) ON DELETE CASCADE ON UPDATE CASCADE,
      FOREIGN KEY (receiver_id) REFERENCES {0}.users(id) ON DELETE CASCADE ON UPDATE CASCADE
      );
      
      CREATE TABLE IF NOT EXISTS {0}.notifications (
      id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
      user_id INT(11) NOT NULL,
      from_user INT(11) NOT NULL,
      msg_type VARCHAR(128) NOT NULL,
      msg TEXT NOT NULL,
      url VARCHAR(256) NOT NULL,
      date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
      seen TINYINT(1) DEFAULT 0,
      FOREIGN KEY (user_id) REFERENCES {0}.users(id) ON DELETE CASCADE ON UPDATE CASCADE
      );
      
      CREATE TABLE IF NOT EXISTS {0}.connections (
      this_uid INT(11) NOT NULL,
      other_uid INT(11) NOT NULL,
      PRIMARY KEY (this_uid, other_uid),
      FOREIGN KEY (this_uid) REFERENCES {0}.users(id) ON DELETE CASCADE ON UPDATE CASCADE,
      FOREIGN KEY (other_uid) REFERENCES {0}.users(id) ON DELETE CASCADE ON UPDATE CASCADE
      );
      
      CREATE TABLE IF NOT EXISTS {0}.geolocation (
      user_id INT(11) NOT NULL PRIMARY KEY,
      lat FLOAT(16, 10) NOT NULL,
      lon FLOAT(16, 10) NOT NULL,
      FOREIGN KEY (user_id) REFERENCES {0}.users(id) ON DELETE CASCADE ON UPDATE CASCADE);
      '''
    query = sql.format(config.SQL_DB)
    cursor.execute(query)
    db.commit()
    db.close()


def drop_db(config):
    db = connect(host=config.SQL_HOST,
             user=config.SQL_USER,
             password=config.SQL_PASSWORD,
             charset='utf8mb4',
             cursorclass=cursors.DictCursor)

    cursor = db.cursor()
    sql = '''DROP SCHEMA %s;'''
    cursor.execute(sql % config.SQL_DB)


if __name__ == '__main__':
    from config import production_config as config
    init_db(config)
