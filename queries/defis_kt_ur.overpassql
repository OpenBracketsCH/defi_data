[out:json][timeout:300];
(
//Kanton Uri
area["ISO3166-2"="CH-UR"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"](area.searchArea);
);
// print results
out body;
>;
out skel qt;