-- SQLite
/*SELECT 
viewer_id, viewer_weight, demo, display_name
FROM digital_viewer_mapping;*/

select * from
(select 
viewer_id,
viewer_weight,
rank() OVER (
    PARTITION BY demo ORDER BY viewer_weight
    ) AS activation_order
from digital_viewer_mapping
)
order by activation_order;