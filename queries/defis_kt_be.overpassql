[out:json][timeout:300];
(
//Kanton Bern
area["ISO3166-2"="CH-BE"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"](area.searchArea);
);
// print results
out body;
>;
out skel qt;