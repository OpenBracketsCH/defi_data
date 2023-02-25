[out:json][timeout:300];
(
//Kanton Wallis
area["ISO3166-2"="CH-VS"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"](area.searchArea);
);
// print results
out body;
>;
out skel qt;