g = {#[[1]] -> #[[2]], ToString[#[[3]]]} & /@ Import["g.csv"];
Graph[Table[e[[1]], {e, g}], EdgeLabels -> Table[e[[1]] -> e[[2]], {e, g}]]
gd = (#[[1]] -> #[[2]]) & /@ Import["gd.csv"];
gdchi = (#[[1]] -> ToString[\[Chi] = #[[2]]]) & /@ Import["gdchi.csv"];
Graph[gd, DirectedEdges -> True, VertexLabels -> gdchi]