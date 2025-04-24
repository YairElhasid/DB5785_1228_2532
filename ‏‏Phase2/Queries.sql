-- Query 1: Identifies students living on the highest floor of each building who reported ceiling water leaks, 
-- to address roof infrastructure issues.
SELECT 
    s.studentid, 
    s.firstname || ' ' || s.lastname AS fullname, 
    b.buildingname,
    a.floornumber,
	EXTRACT(DAY FROM mr.requestdate) AS requestday,
	EXTRACT(MONTH FROM mr.requestdate) AS requestmonth,
    EXTRACT(YEAR FROM mr.requestdate) AS requestyear
FROM student s
JOIN rental r ON s.studentid = r.studentid
JOIN room rm ON r.roomid = rm.roomid
JOIN apartment a ON rm.apartmentid = a.apartmentid AND rm.buildingid = a.buildingid
JOIN building b ON a.buildingid = b.buildingid
JOIN maintenance_request mr ON rm.roomid = mr.roomid
WHERE a.floornumber = (SELECT MAX(floornumber) FROM apartment a2 WHERE a2.buildingid = b.buildingid)
AND mr.issuedescription = 'Water leak from ceiling'
AND CURRENT_DATE BETWEEN r.checkindate AND r.checkoutdate
ORDER BY b.buildingname, a.floornumber DESC;

-- Query 2: Finds rooms where the same issue was reported more than once in the past year, to plan targeted renovations.
SELECT 
    r.roomid, 
    b.buildingname, 
    mr.issuedescription, 
    COUNT(mr.requestid) AS issuecount,
    STRING_AGG('Day ' || EXTRACT(DAY FROM mr.requestdate), ', ') AS requestdays,
	EXTRACT(MONTH FROM mr.requestdate) AS requestmonth,
	EXTRACT(YEAR FROM mr.requestdate) AS requestyear
FROM room r
JOIN apartment a ON r.apartmentid = a.apartmentid AND r.buildingid = a.buildingid
JOIN building b ON a.buildingid = b.buildingid
JOIN maintenance_request mr ON r.roomid = mr.roomid
WHERE mr.requestdate >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY r.roomid, b.buildingname, mr.issuedescription, EXTRACT(YEAR FROM mr.requestdate), EXTRACT(MONTH FROM mr.requestdate)
HAVING COUNT(mr.requestid) > 1
ORDER BY issuecount DESC;

-- Query 3: Alerts students living in rooms with unresolved urgent issues (high priority or gas leaks).
SELECT 
    s.studentid, 
    s.firstname || ' ' || s.lastname AS fullname, 
    r.roomid, 
    b.buildingname, 
    mr.issuedescription, 
    EXTRACT(DAY FROM mr.requestdate) AS requestday,
	EXTRACT(MONTH FROM mr.requestdate) AS requestmonth,
	EXTRACT(YEAR FROM mr.requestdate) AS requestyear,
    AGE(CURRENT_DATE, mr.requestdate) AS dayssincerequest
FROM student s
JOIN rental r ON s.studentid = r.studentid
JOIN room rm ON r.roomid = rm.roomid
JOIN apartment a ON rm.apartmentid = a.apartmentid AND rm.buildingid = a.buildingid
JOIN building b ON a.buildingid = b.buildingid
JOIN maintenance_request mr ON rm.roomid = mr.roomid
WHERE (mr.priority = 'High' AND mr.resolveddate IS NULL) OR (mr.issuedescription = 'Gas leak') 
AND CURRENT_DATE BETWEEN r.checkindate AND r.checkoutdate
ORDER BY mr.requestdate DESC;

-- Query 4: Identifies students who received discounts higher than 15% on their leases, to review discount policy.
SELECT 
    s.studentid, 
    s.firstname || ' ' || s.lastname AS fullname, 
    s.major, 
    l.discountpercent, 
    EXTRACT(DAY FROM l.contractdate) AS leaseday,
    EXTRACT(MONTH FROM l.contractdate) AS leasemonth,
    EXTRACT(YEAR FROM l.contractdate) AS leaseyear
FROM student s
JOIN rental r ON s.studentid = r.studentid
JOIN lease l ON r.leaseid = l.leaseid
WHERE l.discountpercent > 15
ORDER BY l.discountpercent DESC;

-- Query 5: Identifies students living in rooms with balconies who reported fewer than 2 issues, for a promotional video.
SELECT 
    s.studentid, 
    s.firstname || ' ' || s.lastname AS fullname, 
    r.roomid, 
    b.buildingname, 
    COUNT(mr.requestid) AS requestcount,
    EXTRACT(MONTH FROM r.checkindate) AS checkinmonth,
	EXTRACT(YEAR FROM r.checkindate) AS checkinyear
FROM student s
JOIN rental r ON s.studentid = r.studentid
JOIN room rm ON r.roomid = rm.roomid
JOIN apartment a ON rm.apartmentid = a.apartmentid AND rm.buildingid = a.buildingid
JOIN building b ON a.buildingid = b.buildingid
LEFT JOIN maintenance_request mr ON rm.roomid = mr.roomid AND mr.requestdate >= CURRENT_DATE - INTERVAL '1 year'
WHERE rm.hasbalcony = TRUE
AND CURRENT_DATE BETWEEN r.checkindate AND r.checkoutdate
GROUP BY s.studentid, s.firstname, s.lastname, s.major, r.roomid, b.buildingname, r.checkindate
HAVING COUNT(mr.requestid) < 2
ORDER BY requestcount ASC;

-- Query 6: Identifies rooms that are currently available or will be available by September 1, 2025, 
-- for new student assignments.
SELECT 
    r.roomid, 
    b.buildingname, 
    a.floornumber, 
    r.maxpeople, 
    r.hasbalcony,
    CASE 
        WHEN MAX(rental.checkoutdate) IS NULL THEN 'Available Now'
        ELSE 'Will Be Available'
    END AS availabilitystatus
FROM room r
JOIN apartment a ON r.apartmentid = a.apartmentid AND r.buildingid = a.buildingid
JOIN building b ON a.buildingid = b.buildingid
LEFT JOIN rental ON r.roomid = rental.roomid
WHERE r.roomid NOT IN (
    SELECT roomid 
    FROM rental 
    WHERE (checkindate <= '2025-09-01' AND checkoutdate >= '2025-09-01')
       OR checkindate > '2025-09-01'
)
GROUP BY r.roomid, b.buildingname, a.floornumber, r.maxpeople, r.hasbalcony
ORDER BY b.buildingname, r.roomid;

-- Query 7: Identifies the top 20% of managers who offered the most discounts, to review their impact on profits.
SELECT 
    dm.managerid,
    dm.fullname,
    COUNT(l.leaseid) AS totaldiscounts,
    AVG(l.discountpercent) AS averagediscount
FROM dorm_management dm
JOIN lease l ON dm.managerid = l.managerid
WHERE l.discountpercent > 0
GROUP BY dm.managerid, dm.fullname
ORDER BY totaldiscounts DESC, averagediscount DESC
LIMIT (
    SELECT (COUNT(DISTINCT managerid) * 0.2)
    FROM dorm_management
);

-- Query 8: Identifies buildings with more issues reported in winter (Dec-Feb) than in summer (Jun-Aug),
-- to prepare for the cold season.
SELECT 
    b.buildingid, 
    b.buildingname, 
    SUM(CASE 
        WHEN EXTRACT(MONTH FROM mr.requestdate) IN (12, 1, 2) THEN 1 
        ELSE 0 
    END) AS winterissues,
    SUM(CASE 
        WHEN EXTRACT(MONTH FROM mr.requestdate) IN (6, 7, 8) THEN 1 
        ELSE 0
    END) AS summerissues,
    EXTRACT(YEAR FROM mr.requestdate) AS requestyear
FROM building b
JOIN apartment a ON b.buildingid = a.buildingid
JOIN room r ON a.apartmentid = r.apartmentid AND a.buildingid = r.buildingid
JOIN maintenance_request mr ON r.roomid = mr.roomid
WHERE mr.requestdate >= CURRENT_DATE - INTERVAL '2 years'
GROUP BY b.buildingid, b.buildingname, EXTRACT(YEAR FROM mr.requestdate)
HAVING SUM(CASE WHEN EXTRACT(MONTH FROM mr.requestdate) IN (12, 1, 2) THEN 1 ELSE 0 END) > 
       SUM(CASE WHEN EXTRACT(MONTH FROM mr.requestdate) IN (6, 7, 8) THEN 1 ELSE 0 END)
ORDER BY buildingid DESC;