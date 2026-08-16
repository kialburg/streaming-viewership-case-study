/* 
Input DF format:
session_viewer_links[(demo, s_id, channel)] = (v_id, link_viewer_ind)


Output 1: digital_sessions 
digital_sessions + viewer_id + viewer_weight

Output 2:

*/

CASE
WHEN 
THEN 1
WHEN
THEN 0
END AS activation_status
