-- Assignment Coverage: 
-- Report the percentage of successfully assigned digital sessions and any rejected or unassigned sessions.

SELECT 
COUNT(1),
FROM digital_20250904_sessions dig
LEFT JOIN output_sessions_20250904 out
ON dig.session_id = out.session_id
where out.session_id IS NULL;