Select * from Food_Item where Item_Type = "Indian" As Food_Item_Indian At 2;
Select * from Food_Item where Item_Type = "Chinese" As Food_Item_Chinese At 2;
Select * from Food_Item where Item_Type = "Italian" As Food_Item_Italian At 3;

Select * from Order_Items INNER JOIN Food_Item_Chinese On Order_Items.Item_ID=Food_Item_Chinese.PK_Custom As Order_Items_Chinese At 2;
Select * from Order_Items INNER JOIN Food_Item_Indian On Order_Items.Item_ID=Food_Item_Indian.PK_Custom As Order_Items_Indian At 2;
Select * from Order_Items INNER JOIN Food_Item_Italian On Order_Items.Item_ID=Food_Item_Italian.PK_Custom As Order_Items_Italian At 3;

-- Select * from Order_Items and Food_Item_Chinese As Order_Items_Chinese At 2;
-- Select * from Order_Items and Food_Item_Indian As Order_Items_Indian At 2;
-- Select * from Order_Items and Food_Item_Italian As Order_Items_Italian At 3;

Select * from Orders INNER JOIN Order_Items_Chinese on Orders.PK_Custom=Order_Items_Chinese.Order_ID As User_Restaurant_Order_Amount_Chinese At 2;
Select * from Orders INNER JOIN Order_Items_Indian on Orders.PK_Custom=Order_Items_Indian.Order_ID As User_Restaurant_Order_Amount_Indian At 2;
Select * from Orders INNER JOIN Order_Items_Italian on Orders.PK_Custom=Order_Items_Italian.Order_ID As User_Restaurant_Order_Amount_Italian At 3;

-- Select * from Orders and Order_Items_Indian As User_Restaurant_Order_Amount_Indian At 2;
-- Select * from Orders and Order_Items_Italian As User_Restaurant_Order_Amount_Italian At 3;
-- Select * from Orders and Order_Items_Chinese As User_Restaurant_Order_Amount_Chinese At 2;

Select Address,Phone_Number,PK_Custom from Users As User_Remaining At 2;
Select Name,Email,PK_Custom from Users As User_Minimal At 4;
Select Name,Rating,Specialty,PK_Custom from Restaurants As Restaurants_Minimal At 4;
Select Address,Email,Num_Reviews,PK_Custom from Restaurants As Restaurants_Remaining At 4;

-- chinese changed