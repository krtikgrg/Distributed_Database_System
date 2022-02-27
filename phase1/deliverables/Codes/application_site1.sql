USE zomato_catalog_outlaws;

DROP TABLE IF EXISTS Food_Item_Chinese;

CREATE TABLE Food_Item_Chinese (
    Name VARCHAR(100) NOT NULL,
    Type VARCHAR(100) NOT NULL,
    Price INT NOT NULL,
    Category VARCHAR(100) NOT NULL,
    FK_Restaurant VARCHAR(100) NOT NULL,
    PK_Custom VARCHAR(100) NOT NULL,
    PRIMARY KEY(PK_Custom)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

DROP TABLE IF EXISTS User_Restaurant_Order_Amount_Chinese;

CREATE TABLE User_Restaurant_Order_Amount_Chinese (
    User_ID VARCHAR(100) NOT NULL,
    Restaurant_ID VARCHAR(100) NOT NULL,
    PK_Custom VARCHAR(100) NOT NULL,
    Amount INT NOT NULL,
    PRIMARY KEY(PK_Custom)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;