/*Update Profile with Password*/
sql_statement = "UPDATE users SET password = '"+newpass+"',full_name = '"+first+" "+last+"',company_name = '"+company+"',addr1 = '"+\
                addr1+"',addr2 = '"+addr2+"',city = '"+city+"',state = '"+state+"', zipcode = '"+zipcode+"' WHERE email = '"+email+"'"
(newpass, first, last, company, addr1,addr2, city, state, zipcode, email)

/*Update Profile without Password*/
sql_statement = "UPDATE users SET full_name = '"+first+" "+last+"',company_name = '"+company+"',addr1 = '"+\
                addr1+"',addr2 = '"+addr2+"',city = '"+city+"',state = '"+state+"', zipcode = '"+zipcode+"' WHERE email = '"+email+"'"
(first, last, company, addr, city, state, zipcode, email)

/*NOT TESTEDAdd new request*/
'INSERT INTO requests (email, gallons, deliv_date,\
                price, transport, discLvl, percDisc, compPrice, total)\
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (session['email'], session['gal'],
                 session['deliv_date']+' ' +session['deliv_time']+":00",
                 session['price'], session['transport'],discLvl, perc_disc,
                 comp_pr, total)

/*Get Quote History*/
sql_statement = "SELECT COUNT(*) FROM history WHERE email = '"+email+"'"
 (email,)

/*Insert into attempt table*/
sql_statement = "INSERT INTO attempts (email, password, result, ip_address) VALUES ('"+email+"','"+generate_password_hash(password)+"','"+reason+"','"+ip+"')"
        (email, generate_password_hash(password), reason, ip)

/*Update Attempts to 0 after successful login*/
sql_statement = "UPDATE users SET attempts = 0 ,  logged = 1 WHERE email ='"+email+"'"
                            (0,1, email)

/*Untested should work*/
sql_statement = "UPDATE users SET logged_in = 0 WHERE email = '"+session['email']+"'"
        (0,session['email'])

/*Untested. Should work*/
sql_statement = "UPDATE users SET attempts = "+ (user['attempts']+1)+ "WHERE email ='"+email+"'"
                            (user['attempts']+1,email)

/* Untested. Should work */
'INSERT INTO attempts (email, password, result, location) VALUES (?, ?, ?, ?)'
sql_statement = "INSERT INTO attempts (email, password, result, ip_address) VALUES ('"+email+"','"+generate_password_hash(password)+"','"+reason+"','"+ip+"')"
        (email, generate_password_hash(password), reason, ip)
