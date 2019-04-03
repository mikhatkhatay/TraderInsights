/*
To run go to psql use command:
\i '[PATH TO SQL FILE]'
*/

/*Create User Table*/

create table users (
email varchar(50) primary key,
password varchar(100),
full_name varchar(50),
company_name varchar(50),
addr1 varchar(100),
addr2 varchar(100),
city varchar(100),
state varchar(2),
zipcode varchar(9),
number_of_attempts numeric default 0,
logged_in numeric default 0);

/*Attempts*/

create  table attempts (
id serial primary key,
email varchar(50),
password varchar(100),
result numeric,
ip_address varchar(50));


/*Requests/History*/

create table history (
id serial primary key,
email varchar(50) references users(email),
full_name varchar(50),
company_name varchar(50),
addr1 varchar(100),
addr2 varchar(100),
city varchar(100),
state varchar(2),
zipcode varchar(9),
gallons numeric,
date timestamp,
price_per_gal numeric
transport numeric,
discount_level varchar(50),
percent_discount numeric,
comp_price numeric,
total numeric
);


/*Comp_rate*/

create table comp_rate (
id serial primary key,
name varchar(50),
January numeric,
February numeric,
March numeric,
April numeric,
May numeric,
June numeric,
July numeric,
August numeric,
September numeric
October numeric,
November numeric,
December numeric,
year numeric);


/*Season_flux*/

create table season_flux (
season numeric,
perc_inc numeric);

