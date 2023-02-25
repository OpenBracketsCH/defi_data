[out:json][timeout:300];
(
//Kanton Graubünden
area["ISO3166-2"="CH-GR"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"](area.searchArea);
);
// print results
out body;
>;
out skel qt;