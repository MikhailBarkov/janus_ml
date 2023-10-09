package org.predictplugin;

import org.janusgraph.graphdb.database.StandardJanusGraph;
import org.janusgraph.graphdb.configuration.GraphDatabaseConfiguration;
import org.apache.tinkerpop.gremlin.structure.service.ServiceRegistry;

import org.yaml.snakeyaml.Yaml;
import org.yaml.snakeyaml.constructor.Constructor;
import org.yaml.snakeyaml.LoaderOptions;

import java.io.FileInputStream;
import java.io.InputStream;
import java.util.Objects;
import java.util.HashMap;


public class PredictJanusGraph extends StandardJanusGraph {

    private ServiceRegistry registry;

    public PredictJanusGraph(GraphDatabaseConfiguration configuration) {
        super(configuration);
        registry = new ServiceRegistry();
    }

    @Override
    public ServiceRegistry getServiceRegistry() {
        HashMap<String, String> services = loadServicesConfiguration();

        services.forEach((key, value) -> {
            registry.registerService(new PredictServiceFactory(key, value));
        });

        return registry;
    }

    private static class ServicesConfig {
        public HashMap<String, String> services;
    }

    private static HashMap<String, String> loadServicesConfiguration() {
        HashMap<String, String> services = new HashMap();
        try {
            InputStream stream = new FileInputStream("conf/gremlin-server/services.yaml");
            Objects.requireNonNull(stream);

            Yaml yaml = new Yaml(new Constructor(ServicesConfig.class, new LoaderOptions()));

            ServicesConfig servicesConfig = yaml.loadAs(stream, ServicesConfig.class);
            services = servicesConfig.services;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return services;
    }
}
