-- labs is fragmented horizontally
-- Allocate labs1 to site 1/5, labs2 to site 2/6, labs3 to site 3/7, labs4 to site 4/8
Select * from labs where lab_location = 'VINDHYA' As labs2;
Select * from faculty where lab_location = 'VINDHYA' As faculty2;

-- faculty is fragmented derived horizontally with respect to labs table (faculty(i) is corresponding table to labs(i))
-- Allocate faculty1 to site 1/5, faculty2 to site 2/6, faculty3 to site 3/7, faculty4 to site 4/8

-- students is fragmented vertically
-- Allocate students1 to site site 1/5, students2 to site 2/6, students3 to site 3/7
Select rno,cgpa,expense from students As students2;