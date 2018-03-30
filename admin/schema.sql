CREATE TABLE IF NOT EXISTS adm_users(user_id    varchar(32) NOT NULL ,
                                     user_name  varchar(32) NOT NULL ,
                                     password   varchar(80) NOT NULL ,
                                     module_ids varchar(1024) NULL ,
                                     email      varchar(64) NULL ,
                                     locked     int NOT NULL DEFAULT 0,
                                     primary key(user_id)
                                    )ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;

CREATE TABLE IF NOT EXISTS adm_config(config_id    varchar(32) NOT NULL ,
                                      config_type  varchar(32) NOT NULL ,
                                      data         mediumBlob  NOT NULL ,
                                      data_bak     mediumBlob  NOT NULL ,
                                      primary key(config_id, config_type)
                                    )ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;

CREATE TABLE IF NOT EXISTS adm_activity(activity_id  int  NOT NULL,
                                        minver     varchar(32) NOT NULL,
                                        channels   varchar(64) NOT NULL,
                                        start_time varchar(32) NOT NULL,
                                        over_time  varchar(32) NOT NULL,
                                        data       varchar(1024) NULL DEFAULT "",
                                        usable     int NOT NULL DEFAULT 0,
                                        primary key(activity_id)
                                    )ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;

CREATE TABLE IF NOT EXISTS adm_apl(apl_id  int  NOT NULL,
                                        version varchar(32) NULL,
                                        opened  int NOT NULL DEFAULT 0,
                                        primary key(apl_id)
                                    )ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;

#insert into adm_apl(apl_id,version,opened) values(1, '', 0);
#insert into adm_apl(apl_id,version,opened) values(2, '', 0);
#insert into adm_apl(apl_id,version,opened) values(3, '', 0);

CREATE TABLE IF NOT EXISTS Finance(pkey varchar(80) NOT NULL ,
                                     flag tinyint NOT NULL default 0 ,
                                     data mediumblob NULL,
                                     primary key(pkey)
                                    ) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;

CREATE TABLE IF NOT EXISTS Level( version varchar(80) NOT NULL ,
                                  datestr varchar(80) NOT NULL ,
                                  level   int NOT NULL,
                                  starts   int NOT NULL DEFAULT 0,
                                  wins     int NOT NULL DEFAULT 0,
                                  loses    int NOT NULL DEFAULT 0,
                                  quits    int NOT NULL DEFAULT 0,
                                  wins_n     int NOT NULL DEFAULT 0,
                                  loses_n    int NOT NULL DEFAULT 0,
                                  quits_n    int NOT NULL DEFAULT 0,
                                  winstars int NOT NULL DEFAULT 0,
                                  winsteps int NOT NULL DEFAULT 0,
                                  winskills int NOT NULL DEFAULT 0,
                                  losetargetrate float NOT NULL DEFAULT 0,
                                  primary key(version, datestr, level)
                                 ) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;

CREATE TABLE IF NOT EXISTS adm_message(msgid int NOT NULL AUTO_INCREMENT,
                                   msgtype   varchar(32) NOT NULL,
                                   target    varchar(32) NOT NULL,
                                   status    int NOT NULL default 0,
                                   intask    int NOT NULL default 0,
                                   send_all  int NOT NULL default 1,
                                   self_invoke int NOT NULL default 1,
                                   primary key(msgid)
                                    ) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;

CREATE TABLE IF NOT EXISTS adm_task(taskid int NOT NULL AUTO_INCREMENT,
                                    taskcode  mediumBlob NOT NULL,
                                    status    int NOT NULL default 0,
                                    intask    int NOT NULL default 0,
                                    primary key(taskid)
                                    ) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;

CREATE TABLE IF NOT EXISTS adm_payment( pid      varchar(64) NOT NULL,
                                    user_id  varchar(32) NOT NULL,
                                    order_id varchar(64) NULL,
                                    status   int         NOT NULL DEFAULT 0,
                                    num      int         NOT NULL,
                                    price    int         NOT NULL,
                                    sum      int         NOT NULL,
                                    create_time  datetime  NOT NULL,
                                    complete_time   datetime  NOT NULL,
                                    remark   varchar(128) NULL,
                                    primary key(pid)
                                  )ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
