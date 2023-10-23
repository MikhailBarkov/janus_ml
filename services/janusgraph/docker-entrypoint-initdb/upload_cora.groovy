import static org.apache.tinkerpop.gremlin.process.traversal.AnonymousTraversalSource.traversal;

g = traversal().withRemote('conf/remote-graph.properties')

if (g.V().hasLabel("cora").hasNext()) {
    println "Cora Dataset is already uploaded."
} else {
    g.V().hasLabel("paper").drop().iterate()

    rows = new File("dataset/cora_nodes.csv").readLines().tail()*.split(';')
    nodes = []
    for (row in rows) {
        nodes.add(
            g.addV("paper").
                property("category", row[0]).
                property("word_vector", row[1]).
                next()
        )
    }

    edges = new File("dataset/cora_edges.csv").readLines().tail()*.split(';')
    for (edge in edges) {
        g.addE("citation").
            from(nodes[edge[0] as Integer]).
            to(nodes[edge[1] as Integer]).
            iterate()
    }

    g.addV("cora").next()

    println "CORA Dataset uploading is over."
}

if (g.V().hasLabel("fake_news").hasNext()) {
    println "Fake News Dataset is already uploaded."
} else {
    g.V().hasLabel("news").drop().iterate()

    new_rows = new File("dataset/FA-KES-Dataset.csv").readLines().tail()*.split(',')

    for (row in new_rows) {
        node = g.addV("news").
                property("text", row[2]).
                property("source", row[3]).
                property("date", row[4]).
                property("location", row[5]).
                property("real", row[6]).
                next()

        g.V(node).as("a")
            .V().hasLabel("news").as("b")
            .or(
                __.where("a", eq("b")).by("source"),
                __.where("a", eq("b")).by("date"),
                __.where("a", eq("b")).by("location")
            ).addE("link").from("a").to("b")
            .iterate()
    }

    g.addV("fake_news").next()

    println "Fake news Dataset uploading is over."
}
