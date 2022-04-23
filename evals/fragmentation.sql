-- labs is fragmented horizontally
-- Allocate labs1 to site 1/5, labs2 to site 2/6, labs3 to site 3/7, labs4 to site 4/8
Select * from labs where lab_location = 'KCIS' As labs1 At 1;
Select * from labs where lab_location = 'VINDHYA' As labs2 At 2;
Select * from labs where lab_location = 'HIMALAYA' As labs3 At 3;
Select * from labs where lab_location = 'NILGIRI' As labs4 At 4;
Select * from faculty and labs1 As faculty1 At 1;
Select * from faculty and labs2 As faculty2 At 2;
Select * from faculty and labs3 As faculty3 At 3;
Select * from faculty and labs4 As faculty4 At 4;

Select rno,fname,lname from students As students1 At 1;
Select rno,cgpa,expense from students As students2 At 2;
Select rno,branch,facId from students As students3 At 3;


-- faculty is fragmented derived horizontally with respect to labs table (faculty(i) is corresponding table to labs(i))
-- Allocate faculty1 to site 1/5, faculty2 to site 2/6, faculty3 to site 3/7, faculty4 to site 4/8

-- students is fragmented vertically
-- Allocate students1 to site site 1/5, students2 to site 2/6, students3 to site 3/7