package org.predictplugin;

import org.apache.tinkerpop.gremlin.structure.util.CloseableIterator;
import org.apache.tinkerpop.gremlin.structure.service.Service;

import java.util.Set;
import java.util.HashSet;
import java.util.Map;
import java.util.ArrayList;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.MalformedURLException;


class PredictServiceFactory implements Service.ServiceFactory {
    private String NAME;

    protected String serviceURL;

    public PredictServiceFactory(String serviceName, String serviceURL) {
        this.serviceURL = serviceURL;
        this.NAME = serviceName;
    }

    @Override
    public String getName() {
        return NAME;
    }

    @Override
    public Set<Service.Type> getSupportedTypes() {
        HashSet<Service.Type> types = new HashSet<Service.Type>();
        types.add(Service.Type.Start);
        return types;
    }

    @Override
    public PredictService createService(final boolean isStart, final Map params) {
        if (isStart) {
            return new PredictService(params, serviceURL);
        }
        else {
            throw new UnsupportedOperationException(Service.Exceptions.cannotUseMidTraversal);
        }
    }

    public class PredictService implements Service {
        final Map params;
        protected URL serviceURL;

        public PredictService(final Map params, String serviceURL) {
            this.params = params;

            try {
                this.serviceURL = new URL(serviceURL);
            } catch (MalformedURLException e) {
                e.printStackTrace(System.out);
            }
        }

        @Override
        public Service.Type getType() {
            return Service.Type.Start;
        }

        @Override
        public CloseableIterator execute(final Service.ServiceCallContext ctx, final Map params) {
            String response;
            try {
                response = sendPredictionRequest(params);
            } catch (IOException e) {
                e.printStackTrace(System.out);
                response = "Сouldn't send request parameters.";
            }
            ArrayList<String> l = new ArrayList<String>();
            l.add(response);
            return CloseableIterator.of(l.iterator());
        }

        protected String sendPredictionRequest(final Map<String, String> params) throws IOException {
            String requestParams;
            try {
                requestParams = prepareRequestParams(params);
            } catch (Exception e) {
                e.printStackTrace(System.out);
                return "Params prepare Exception!";
            }

            HttpURLConnection httpURLConnection = (HttpURLConnection) serviceURL.openConnection();
            httpURLConnection.setRequestMethod("POST");
            httpURLConnection.setDoOutput(true);
            OutputStreamWriter osw = new OutputStreamWriter(httpURLConnection.getOutputStream(), "UTF-8");
            osw.write(requestParams);
            osw.flush();

            int responseCode = httpURLConnection.getResponseCode();

            osw.close();

            if (responseCode == HttpURLConnection.HTTP_OK) {
                BufferedReader in = new BufferedReader(new InputStreamReader(httpURLConnection.getInputStream()));
                String inputLine;
                StringBuffer response = new StringBuffer();
                while ((inputLine = in.readLine()) != null) {
                    response.append(inputLine);
                }
                in.close();

                return response.toString();
            } else {
                return "Bad response with code " + responseCode;
            }
        }

        protected String prepareRequestParams(final Map<String, String> params) throws Exception {
            StringBuilder data = new StringBuilder();

            if (params.containsKey("endpoint_id") && params.get("endpoint_id") != null) {
                data.append("{\"endpoint_id\": \"" + params.get("endpoint_id") + "\", ");
            } else {
                return null;
            }

            if (params.containsKey("predict_entity_idx") && params.get("predict_entity_idx") != null) {
                data.append("\"predict_entity_idx\": \"" + params.get("predict_entity_idx") + "\", ");
            } else {
                return null;
            }

            if (params.containsKey("interface") && params.get("interface") != null){
                data.append("\"interface\": \"" + params.get("interface") + "\"}");
            } else {
                data.append("\"interface\": \"transductive\"}");
            }

            return data.toString();
        }
    }

    @Override
    public void close() {}
}
