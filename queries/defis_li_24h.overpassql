[out:json][timeout:300];
(
//ganz Liechtenstein 24h Defis
area["ISO3166-1"="LI"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"]["opening_hours"="24/7"](area.searchArea);
);
// print results
out body;
>;
out skel qt;