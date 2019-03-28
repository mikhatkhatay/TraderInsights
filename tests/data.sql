INSERT INTO users (email, password, first, last, company, addr, city, state, zipcode)
VALUES
  ('admin@mail.com', 'pbkdf2:sha256:50000$jKn20YfE$4d7fb3c413425eb712ce89cf24deabc2b5e4b09050cbd82748053c2013aaed84', 'John','Doe', 'John Doe Ltd.','1234 Main St.', 'Houston','TX','77002'),
  ('python@mail.com', 'pbkdf2:sha256:50000$GmujtOIE$78c61c172a7ee2c4bf6356af768c2edc1436f9c253c62c6b5f486acf60bb10e8', 'Johann','Bach','Bach Co.','Somewhere in Germany','Eisenach, Thuringia, DEU','AZ','99817');

INSERT INTO compRate (company, month, year, price)
VALUES
  ('Company 1', 1, 2017, 2.199),
  ('Company 1', 2, 2017, 2.119),
  ('Company 2', 1, 2017, 3.199),
  ('Company 2', 2, 2017, 2.499);

INSERT INTO seasonFlux (season, percInc)
VALUES
  ('Summer', 10),
  ('Winter', 5);