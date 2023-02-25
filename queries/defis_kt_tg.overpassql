[out:json][timeout:300];
(
//Kanton Thurgau
area["ISO3166-2"="CH-TG"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"](area.searchArea);
);
// print results
out body;
>;
out skel qt;