[out:json][timeout:25];
(
//ganz Liechtenstein nicht 24h
area["ISO3166-1"="LI"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"]["opening_hours"!="24/7"](area.searchArea);
);
// print results
out body;
>;
out skel qt;