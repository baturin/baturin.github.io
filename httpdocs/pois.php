<?php
header("Access-Control-Allow-Origin:*");

$db = new SQLite3('/home/alexey/wv-pois.db');
$stmt = $db->prepare(
	'SELECT * FROM wikivoyage_pois WHERE latitude >= :min_latitude and latitude <= :max_latitude and longitude >= :min_longitude and longitude <= :max_longitude LIMIT 100'
);
$stmt->bindValue(':min_latitude', $_GET['min_latitude']);
$stmt->bindValue(':max_latitude', $_GET['max_latitude']);
$stmt->bindValue(':min_longitude', $_GET['min_longitude']);
$stmt->bindValue(':max_longitude', $_GET['max_longitude']);
$result = $stmt->execute();

$data = [];
while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
	$data[] = $row;
}
print json_encode($data);
