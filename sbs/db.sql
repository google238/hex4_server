CREATE TABLE IF NOT EXISTS Configs(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS AdminUser(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Payment(transaction_id varchar(80) NOT NULL ,
                                   user_id       varchar(32) NOT NULL ,
                                   product_id    varchar(80) NOT NULL ,
                                   quantity      int  NOT NULL,
                                   platform      varchar(32) NOT NULL ,
                                   package       varchar(128) NOT NULL ,
                                   purchased_at  datetime NOT NULL,
                                   status        int  NOT NULL,
                                   retry         int NOT NULL DEFAULT 0,
                                   primary key(transaction_id)
                                  ) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Devices_0(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Devices_1(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Devices_2(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Devices_3(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Devices_4(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Devices_5(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Devices_6(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Devices_7(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Devices_8(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Devices_9(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Devices_a(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Devices_b(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Devices_c(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Devices_d(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Devices_e(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Devices_f(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;

CREATE TABLE IF NOT EXISTS Bucket_userData_0(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_userData_1(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_userData_2(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_userData_3(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_userData_4(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_userData_5(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_userData_6(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_userData_7(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_userData_8(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_userData_9(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_userData_a(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_userData_b(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_userData_c(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_userData_d(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_userData_e(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_userData_f(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;

CREATE TABLE IF NOT EXISTS Bucket_Command_0(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_Command_1(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_Command_2(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_Command_3(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_Command_4(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_Command_5(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_Command_6(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_Command_7(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_Command_8(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_Command_9(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_Command_a(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_Command_b(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_Command_c(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_Command_d(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_Command_e(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS Bucket_Command_f(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;

CREATE TABLE IF NOT EXISTS GooglePlayBind_0(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GooglePlayBind_1(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GooglePlayBind_2(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GooglePlayBind_3(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GooglePlayBind_4(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GooglePlayBind_5(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GooglePlayBind_6(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GooglePlayBind_7(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GooglePlayBind_8(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GooglePlayBind_9(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GooglePlayBind_a(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GooglePlayBind_b(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GooglePlayBind_c(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GooglePlayBind_d(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GooglePlayBind_e(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GooglePlayBind_f(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;

CREATE TABLE IF NOT EXISTS GameCenterBind_0(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GameCenterBind_1(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GameCenterBind_2(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GameCenterBind_3(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GameCenterBind_4(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GameCenterBind_5(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GameCenterBind_6(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GameCenterBind_7(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GameCenterBind_8(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GameCenterBind_9(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GameCenterBind_a(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GameCenterBind_b(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GameCenterBind_c(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GameCenterBind_d(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GameCenterBind_e(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS GameCenterBind_f(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;

CREATE TABLE IF NOT EXISTS FacebookBind_0(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS FacebookBind_1(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS FacebookBind_2(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS FacebookBind_3(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS FacebookBind_4(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS FacebookBind_5(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS FacebookBind_6(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS FacebookBind_7(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS FacebookBind_8(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS FacebookBind_9(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS FacebookBind_a(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS FacebookBind_b(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS FacebookBind_c(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS FacebookBind_d(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS FacebookBind_e(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
CREATE TABLE IF NOT EXISTS FacebookBind_f(pkey varchar(80) NOT NULL , data mediumblob NULL, primary key(pkey)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;
