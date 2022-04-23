INSERT INTO Users(Name,Email,Address,Phone_Number,PK_Custom)
VALUES 
('Kartik','krtikgrg@gmail.com','Sunam','9478077895','AAA'),
('Aaradhya','aardg@gmail.com','Delhi','9971352631','AAB'),
('Priyansh','p@gmail.com','Delhi','9876543210','AAC'),
('Harshit','h@gmail.com','Amritsar','1234567890','AAD'),
('Aaditya','a@gmail.com','Jaipur','4561237890','AAE'),
('Shreyash','s@gmail.com','Delhi','6543219870','AAF'),
('Ayush','ag@gmail.com','Jaipur','7896541230','AAG');

INSERT INTO Restaurants(Name,Address,Email,Rating,Specialty,Num_Reviews,PK_Custom)
VALUES
('Dominos','Gachibowli','domi@gmail.com',4,'pizza',45,'AAH'),
('SKShawarma','DLF','sks@gmail.com',3,'shawarma',38,'AAI'),
('WOWMomos','Indira_Nagar','wm@gmail.com',5,'momos',43,'AAJ'),
('h9','Garden_Road','h9@gmail.com',4,'manchurian',50,'AAK');

INSERT INTO Food_Item(Name,Item_Type,Price,Item_Category,FK_Restaurant,PK_Custom)
VALUES
('Momos','Chinese',40,'Veg','AAJ','AAL'),
('Manchurian','Chinese',50,'Veg','AAK','AAM'),
('Noodles','Chinese',45,'Veg','AAK','AAN'),
('Chowmein','Chinese',70,'Veg','AAK','AAO'),
('Special_Shawarma','Indian',100,'Non-Veg','AAI','AAP'),
('Cheese_Shawarma','Indian',90,'Veg','AAI','AAQ'),
('Marghrita','Italian',100,'Veg','AAH','AAR'),
('Non_Veg_Loaded','Italian',150,'Non-Veg','AAH','AAS'),
('Veg_Loaded','Italian',125,'Veg','AAH','AAT'),
('Pasta','Italian',95,'Veg','AAH','AAU'),
('Honey_Chilli','Indian',120,'Veg','AAK','AAV');

INSERT INTO Orders(User_ID,Restaurant_ID,Amount,PK_Custom)
VALUES
('AAG','AAK',120,'AAW'),
('AAF','AAK',70,'AAX'),
('AAE','AAH',100,'AAY');

INSERT INTO Order_Items(Order_ID,Item_ID,Quantity)
VALUES
('AAW','AAV',1),
('AAX','AAO',1),
('AAY','AAR',1);