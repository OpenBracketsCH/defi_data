[out:json][timeout:300];
(
//Kanton Appenzell Innerhoden
area["ISO3166-2"="CH-AI"];
)->.searchArea;
// gather results
(
nwr["emergency"="defibrillator"](area.searchArea);
);
// print results
out body;
>;
out skel qt;