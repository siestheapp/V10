this file contains succesful insert statements for different tables in the tailor3 database, and should be referenced when providing insert statements for these tables

1) users table
INSERT INTO users (email, gender, height_in, preferred_units)
VALUES ('user@example.com', 'Male', 70, 'in')
RETURNING id;