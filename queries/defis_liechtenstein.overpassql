[out:json][timeout:25];
(
//ganz Liechtenstein
area["ISO3166-1"="LI"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"](area.searchArea);
);
// print results
out body;
>;
out skel qt;