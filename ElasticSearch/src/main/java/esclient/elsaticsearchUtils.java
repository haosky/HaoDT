package esclient;

import java.io.IOException;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.Map;
import java.util.concurrent.ExecutionException;

import org.elasticsearch.action.index.IndexRequest;
//import org.apache.commons.logging.Log;
//import org.apache.commons.logging.LogFactory;
import org.elasticsearch.action.index.IndexResponse;
import org.elasticsearch.action.update.UpdateRequest;
import org.elasticsearch.action.update.UpdateResponse;
import org.elasticsearch.client.transport.TransportClient;
import org.elasticsearch.common.transport.InetSocketTransportAddress;
import org.elasticsearch.common.xcontent.XContentBuilder;
import org.elasticsearch.rest.RestStatus;
import org.elasticsearch.transport.client.PreBuiltTransportClient;
import org.elasticsearch.common.settings.Settings;
import static org.elasticsearch.common.xcontent.XContentFactory.*;

public class elsaticsearchUtils {
//	public static Log log = LogFactory.getLog(elsaticsearchUtils.class);
	private TransportClient client = null;
	
	public TransportClient getClient(){
		return this.client;
	}
	
	public elsaticsearchUtils(String  ... address) throws UnknownHostException{
		if(client == null ){
//		Settings settings = Settings.builder()
//			        .put("cluster.name", "es-renda").build();
		this.client = new PreBuiltTransportClient(Settings.EMPTY);
//		this.client = new PreBuiltTransportClient(settings);
		for(String ad:address){
				String[] splitaddress = ad.split(":");
		        this.client.addTransportAddress(new InetSocketTransportAddress(InetAddress.getByName(splitaddress[0]), Integer.parseInt(splitaddress[1])));
				}
		}
	}
	
	public int indexData(String index,String type,Map<String, Object> bodymap,String id) throws IOException{
		IndexResponse response = client.prepareIndex(index, type,id).setSource(bodymap).get();
		RestStatus status = response.status();
		return status.getStatus();
	}
	
	public int upsetData(String index,String type,Map<String, Object> bodymap,String id) throws IOException, InterruptedException, ExecutionException{
		
//		IndexRequest indexRequest = new IndexRequest(index, type, id).source(builder.string());
		IndexRequest indexRequest = new IndexRequest(index, type, id).source(bodymap);
		UpdateRequest uRequest2 = new UpdateRequest(index, type, id).doc(bodymap).upsert(indexRequest);
		UpdateResponse response =  client.update(uRequest2).get();
		RestStatus status = response.status();
		return status.getStatus();
	}
	
	public void destory(){
		if(client != null){
			this.client.close();
		}
	}
}
