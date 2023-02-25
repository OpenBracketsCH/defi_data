[out:json][timeout:300];
(
//Kanton Neuenburg
area["ISO3166-2"="CH-NE"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"](area.searchArea);
);
// print results
out body;
>;
out skel qt;