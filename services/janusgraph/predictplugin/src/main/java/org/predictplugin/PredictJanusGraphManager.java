package org.predictplugin;

import org.janusgraph.graphdb.management.JanusGraphManager;
import org.janusgraph.graphdb.database.StandardJanusGraph;

import org.apache.tinkerpop.gremlin.structure.Graph;
import org.apache.tinkerpop.gremlin.server.Settings;

import java.util.function.Function;


public class PredictJanusGraphManager extends JanusGraphManager {

    public PredictJanusGraphManager(Settings settings) {super(settings);}

    public void putGraph(String gName, Graph g) {
        g = new PredictJanusGraph(((StandardJanusGraph) g).getConfiguration());
        super.putGraph(gName, g);
    }

    @Override
    public Graph openGraph(String gName, Function<String, Graph> thunk) {
        Graph graph = getGraph(gName);
        if (graph == null) {
            graph = thunk.apply(gName);
            putGraph(gName, graph);
        }
        return super.openGraph(gName, thunk);
    }
}