import static org.apache.tinkerpop.gremlin.process.traversal.AnonymousTraversalSource.traversal;

g = traversal().withRemote('conf/remote-graph.properties')

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
